# XRPL RPC Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the RPC (Remote Procedure Call) subsystem in the XRPL (XRP Ledger) source code. It covers every aspect of the RPC system, including request parsing, handler lookup and dispatch, role and permission management, precondition checks, error handling, handler implementation, and response formatting. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [RPC Overview](#rpc-overview)
- [RPC Request Lifecycle](#rpc-request-lifecycle)
  - [Request Parsing and Validation](#request-parsing-and-validation)
  - [Batch Request Handling](#batch-request-handling)
  - [API Version Detection](#api-version-detection)
- [Role and Permission Management](#role-and-permission-management)
  - [roleRequired](#rolerequired)
  - [requestRole](#requestrole)
- [Resource Management](#resource-management)
- [Handler Lookup and Dispatch](#handler-lookup-and-dispatch)
  - [Handler Table and getHandler](#handler-table-and-gethandler)
  - [Handler Structure](#handler-structure)
- [Precondition Checks](#precondition-checks)
  - [conditionMet](#conditionmet)
- [Command Validation and Dispatch](#command-validation-and-dispatch)
  - [fillHandler](#fillhandler)
  - [doCommand](#docommand)
  - [callMethod](#callmethod)
- [Handler Implementation](#handler-implementation)
  - [Handler Function Prototypes](#handler-function-prototypes)
  - [Example Handlers](#example-handlers)
- [Error Handling and Response Formatting](#error-handling-and-response-formatting)
  - [Error Codes and Utilities](#error-codes-and-utilities)
  - [Response Structure](#response-structure)
- [Supporting Classes and Utilities](#supporting-classes-and-utilities)
- [References to Source Code](#references-to-source-code)

---

## RPC Overview

- The XRPL server exposes a comprehensive RPC interface for interacting with the ledger, submitting transactions, querying state, and managing server operations.
- RPC requests can be made over HTTP, WebSocket, or gRPC (for select endpoints).
- The RPC subsystem is responsible for:
  - Parsing and validating incoming requests.
  - Determining the required and actual user roles.
  - Enforcing resource and rate limits.
  - Locating and dispatching the correct handler for each command.
  - Checking preconditions (network/ledger state).
  - Executing the handler and formatting the response.
  - Handling errors and masking sensitive information.

---

## RPC Request Lifecycle

### Request Parsing and Validation

- Incoming requests are parsed as JSON objects. If the request is too large, cannot be parsed, or is not a valid JSON object, an HTTP 400 error is returned.
- The main entry point for request processing is the `processRequest` function ([src/xrpld/rpc/detail/ServerHandler.cpp.txt](src/xrpld/rpc/detail/ServerHandler.cpp.txt)), which performs the following:
  - Parses the request using a JSON reader.
  - Validates that the request is a JSON object.
  - Checks for the presence and validity of the `method` field.
  - Validates the `params` field, ensuring it is an array of length 1 containing an object (for non-batch requests).

### Batch Request Handling

- The system supports batch requests, where the `method` is `"batch"` and `params` is an array of requests.
- For batch requests:
  - Each sub-request is validated and processed independently.
  - Errors in individual sub-requests do not affect the processing of others.
  - The reply is an array of results, one per sub-request.

### API Version Detection

- The API version is determined from the request parameters or, for batch requests, from the batch object itself.
- If the API version is invalid or unspecified, an error is returned.

---

## Role and Permission Management

### roleRequired

- The function `roleRequired` ([src/xrpld/rpc/detail/RPCHandler.cpp.txt](src/xrpld/rpc/detail/RPCHandler.cpp.txt)) determines the minimum user role required to execute a given RPC method:
  - It calls `RPC::getHandler(version, betaEnabled, method)` to look up the handler for the method, API version, and beta flag.
  - If no handler is found, returns `Role::FORBID`.
  - Otherwise, returns the handler's `role_` field.
- The `Role` enum ([src/xrpld/rpc/Role.h.txt](src/xrpld/rpc/Role.h.txt)) includes: `GUEST`, `USER`, `IDENTIFIED`, `ADMIN`, `PROXY`, `FORBID`.

### requestRole

- The function `requestRole` ([src/xrpld/rpc/Role.h.txt](src/xrpld/rpc/Role.h.txt), [src/xrpld/rpc/detail/Role.cpp.txt](src/xrpld/rpc/detail/Role.cpp.txt)) determines the actual role of the client making the request:
  - Checks if the client is an admin (IP in admin network and correct password).
  - If admin, returns `Role::ADMIN`.
  - Otherwise, determines the role based on other criteria (not fully shown in the provided code).
  - Returns one of: `GUEST`, `USER`, `IDENTIFIED`, `ADMIN`, `PROXY`, `FORBID`.
- The result is used to enforce access control and resource limits.

---

## Resource Management

- Resource usage is tracked per request using a `Resource::Consumer` object.
- If the server is overloaded, a 503 error is returned.
- Resource fees are charged based on the request type and outcome (e.g., malformed requests are charged `Resource::feeMalformedRPC`).

---

## Handler Lookup and Dispatch

### Handler Table and getHandler

- The handler table is a multimap of method names to `Handler` objects ([src/xrpld/rpc/detail/Handler.cpp.txt](src/xrpld/rpc/detail/Handler.cpp.txt)).
- Each `Handler` specifies:
  - Method name (e.g., `"account_info"`)
  - Function pointer (`valueMethod_`)
  - Required user role (`role_`)
  - Required precondition (`condition_`)
  - Minimum and maximum API versions
- The function `getHandler` ([src/xrpld/rpc/detail/Handler.cpp.txt](src/xrpld/rpc/detail/Handler.cpp.txt)):
  - Checks if the requested API version is within the supported range.
  - Looks up all handlers for the given method name.
  - Returns the handler whose version range includes the requested version.
  - If no handler is found, returns `nullptr`.

### Handler Structure

- The `Handler` struct ([src/xrpld/rpc/detail/Handler.h.txt](src/xrpld/rpc/detail/Handler.h.txt)):
  - `name_`: method name
  - `valueMethod_`: function pointer to the handler implementation
  - `role_`: required user role
  - `condition_`: required precondition (see below)
  - `minApiVer_`, `maxApiVer_`: supported API version range

---

## Precondition Checks

### conditionMet

- The function `conditionMet` ([src/xrpld/rpc/detail/Handler.h.txt](src/xrpld/rpc/detail/Handler.h.txt)) checks whether the necessary preconditions are met before executing a handler:
  - Checks if the server is amendment blocked (`rpcAMENDMENT_BLOCKED`).
  - Checks if the validator list is expired (`rpcEXPIRED_VALIDATOR_LIST`).
  - Checks if the server's operating mode is at least SYNCING (`rpcNO_NETWORK` or `rpcNOT_SYNCED`).
  - Checks if the validated ledger is too old or the current ledger is too far behind (`rpcNO_CURRENT` or `rpcNOT_SYNCED`).
  - Checks if a closed ledger is available (`rpcNO_CLOSED` or `rpcNOT_SYNCED`).
  - Returns `rpcSUCCESS` if all checks pass.

---

## Command Validation and Dispatch

### fillHandler

- The function `fillHandler` ([src/xrpld/rpc/detail/RPCHandler.cpp.txt](src/xrpld/rpc/detail/RPCHandler.cpp.txt)) validates the incoming RPC request, checks permissions, and locates the appropriate handler:
  - Checks job queue load for non-unlimited users (`rpcTOO_BUSY`).
  - Validates the presence and consistency of the `command`/`method` fields (`rpcCOMMAND_MISSING`, `rpcUNKNOWN_COMMAND`).
  - Looks up the handler for the command, API version, and beta flag (`rpcUNKNOWN_COMMAND`).
  - Checks if the handler requires admin and the user is not admin (`rpcNO_PERMISSION`).
  - Checks if the required preconditions are met (`conditionMet`).
  - Returns the handler pointer and `rpcSUCCESS` if all checks pass.

### doCommand

- The function `doCommand` ([src/xrpld/rpc/detail/RPCHandler.cpp.txt](src/xrpld/rpc/detail/RPCHandler.cpp.txt)) orchestrates the entire process of handling an RPC command:
  - Calls `fillHandler` to validate the command and permissions.
  - If valid, retrieves the handler and calls its function pointer using `callMethod`.
  - Handles exceptions and error codes, formatting the result as a JSON error object if needed.
  - Returns a `Status` object indicating success or the specific error encountered.

### callMethod

- The function template `callMethod` ([src/xrpld/rpc/detail/RPCHandler.cpp.txt](src/xrpld/rpc/detail/RPCHandler.cpp.txt)) wraps the execution of an RPC handler:
  - Assigns a unique request ID.
  - Starts performance logging.
  - Measures the execution time of the handler.
  - Calls the handler function with the current context and result object.
  - Logs the duration and signals completion to the performance logger.
  - Handles exceptions, logging errors and signaling the error to the performance logger.

---

## Handler Implementation

### Handler Function Prototypes

- All handler functions are declared in [src/xrpld/rpc/handlers/Handlers.h.txt](src/xrpld/rpc/handlers/Handlers.h.txt).
- Each handler takes a reference to an `RPC::JsonContext` object and returns a `Json::Value` representing the result.
- Example:
  - `Json::Value doAccountInfo(RPC::JsonContext&);`
  - `Json::Value doBookOffers(RPC::JsonContext&);`
  - `Json::Value doPing(RPC::JsonContext&);`
  - (See [src/xrpld/rpc/handlers/Handlers.h.txt](src/xrpld/rpc/handlers/Handlers.h.txt) for the full list.)

### Example Handlers

#### doAccountInfo ([src/xrpld/rpc/handlers/AccountInfo.cpp.txt](src/xrpld/rpc/handlers/AccountInfo.cpp.txt))

- Validates input parameters to ensure an account identifier is present and well-formed.
- Parses the account identifier into an internal `AccountID` type.
- Looks up the specified ledger to search for the account.
- Checks if the account exists in the ledger.
- Retrieves detailed account data, including flags, optional fields, and queued transactions if requested.
- Constructs a JSON object with all the requested account information or error details.

#### doBookOffers ([src/xrpld/rpc/handlers/BookOffers.cpp.txt](src/xrpld/rpc/handlers/BookOffers.cpp.txt))

- Validates input parameters, ensuring `taker_pays` and `taker_gets` are present and well-formed.
- Enforces a maximum limit on the number of offers returned.
- Supports pagination via a `marker` parameter.
- Calls `getBookPage` to fetch the relevant offers from the ledger.
- Returns a JSON object containing the list of offers and pagination information.

#### doPing ([src/xrpld/rpc/handlers/Ping.cpp.txt](src/xrpld/rpc/handlers/Ping.cpp.txt))

- Constructs a JSON response based on the user's role, including role, username, and IP address if available.
- Indicates if the request is associated with a subscription that has unlimited access.

(See [src/xrpld/rpc/handlers/Handlers.h.txt](src/xrpld/rpc/handlers/Handlers.h.txt) for the full set of handlers.)

---

## Error Handling and Response Formatting

### Error Codes and Utilities

- Error codes are defined in [include/xrpl/protocol/ErrorCodes.h.txt](include/xrpl/protocol/ErrorCodes.h.txt) and implemented in [src/libxrpl/protocol/ErrorCodes.cpp.txt](src/libxrpl/protocol/ErrorCodes.cpp.txt).
- Utilities are provided to inject error information into JSON responses, generate standard error messages, and check for the presence of errors in JSON objects.
- Example error codes:
  - `rpcCOMMAND_MISSING`: Missing command entry.
  - `rpcUNKNOWN_COMMAND`: Unknown method.
  - `rpcNO_PERMISSION`: You don't have permission for this command.
  - `rpcTOO_BUSY`: The server is too busy to help you now.
  - `rpcNO_NETWORK`: Not synced to the network.
  - `rpcINTERNAL`: Internal error.
  - (See [include/xrpl/protocol/ErrorCodes.h.txt](include/xrpl/protocol/ErrorCodes.h.txt) and [src/libxrpl/protocol/ErrorCodes.cpp.txt](src/libxrpl/protocol/ErrorCodes.cpp.txt) for the full list.)

### Response Structure

- The response is formatted according to the API version.
- For errors, the status is set to `"error"` and sensitive fields in the request are masked before including it in the response.
- For success, the status is set to `"success"`.
- For batch requests, each result is appended to the reply array.
- If the reply contains a nested `"result"` object, the structure is flattened.

---

## Supporting Classes and Utilities

- `RPC::JsonContext` ([src/xrpld/rpc/Context.h.txt](src/xrpld/rpc/Context.h.txt)):
  - Inherits from `RPC::Context`.
  - Contains references to application state, resource usage, user role, API version, JSON parameters, and headers (user and forwarded IP).
  - Constructed via aggregate initialization.
- `RPC::Context`:
  - Contains references to logging, application, resource charge, network operations, ledger master, resource consumer, user role, coroutine, subscription pointer, and API version.
- Helper functions for parsing and validating account IDs, retrieving account objects, looking up ledgers, and handling API versioning are defined in [src/xrpld/rpc/detail/RPCHelpers.h.txt](src/xrpld/rpc/detail/RPCHelpers.h.txt).

---

## References to Source Code

- [src/xrpld/rpc/detail/ServerHandler.cpp.txt](src/xrpld/rpc/detail/ServerHandler.cpp.txt)
- [src/xrpld/rpc/detail/RPCHandler.cpp.txt](src/xrpld/rpc/detail/RPCHandler.cpp.txt)
- [src/xrpld/rpc/detail/Handler.cpp.txt](src/xrpld/rpc/detail/Handler.cpp.txt)
- [src/xrpld/rpc/detail/Handler.h.txt](src/xrpld/rpc/detail/Handler.h.txt)
- [src/xrpld/rpc/Context.h.txt](src/xrpld/rpc/Context.h.txt)
- [src/xrpld/rpc/Role.h.txt](src/xrpld/rpc/Role.h.txt)
- [src/xrpld/rpc/handlers/Handlers.h.txt](src/xrpld/rpc/handlers/Handlers.h.txt)
- [src/xrpld/rpc/handlers/AccountInfo.cpp.txt](src/xrpld/rpc/handlers/AccountInfo.cpp.txt)
- [src/xrpld/rpc/handlers/BookOffers.cpp.txt](src/xrpld/rpc/handlers/BookOffers.cpp.txt)
- [src/xrpld/rpc/handlers/Ping.cpp.txt](src/xrpld/rpc/handlers/Ping.cpp.txt)
- [include/xrpl/protocol/ErrorCodes.h.txt](include/xrpl/protocol/ErrorCodes.h.txt)
- [src/libxrpl/protocol/ErrorCodes.cpp.txt](src/libxrpl/protocol/ErrorCodes.cpp.txt)
- [src/xrpld/rpc/detail/RPCHelpers.h.txt](src/xrpld/rpc/detail/RPCHelpers.h.txt)

---

All statements and explanations above are directly supported by the provided source code and documentation. No assumptions or extrapolations have been made beyond the available information.