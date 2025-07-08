# XRPL Logging Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the logging infrastructure in the XRPL (XRP Ledger) source code. It covers every aspect of logging, including its architecture, log sinks, severity levels, file and console output, thread safety, log rotation, debug logging, integration with application modules, and performance logging. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [Logging Overview](#logging-overview)
- [Log Severity Levels](#log-severity-levels)
- [Core Logging Classes and Structure](#core-logging-classes-and-structure)
  - [Logs](#logs)
  - [Sink](#sink)
  - [File](#file)
  - [DebugSink and DebugLog](#debugsink-and-debuglog)
  - [Macros: JLOG and CLOG](#macros-jlog-and-clog)
- [Log Message Formatting and Output](#log-message-formatting-and-output)
- [Log Sinks and Partitions](#log-sinks-and-partitions)
- [Log File Management and Rotation](#log-file-management-and-rotation)
- [Thread Safety](#thread-safety)
- [Performance Logging (PerfLog)](#performance-logging-perflog)
- [Integration with Application Modules](#integration-with-application-modules)
- [References to Source Code](#references-to-source-code)

---

## Logging Overview

- Logging in XRPL is a cross-cutting concern, used for debugging, monitoring, auditing, and error reporting throughout the codebase.
- The logging system is designed to be modular, thread-safe, and flexible, supporting multiple log destinations (sinks), severity levels, and dynamic configuration.
- Logging is abstracted via interfaces and classes, with implementation details hidden from most modules.

---

## Log Severity Levels

Defined in [`LogSeverity`](src/xrpl/basics/Log.h):

- `lsINVALID`
- `lsTRACE`
- `lsDEBUG`
- `lsINFO`
- `lsWARNING`
- `lsERROR`
- `lsFATAL`

These map to the underlying `beast::severities::Severity` and are used to filter log messages by importance.

---

## Core Logging Classes and Structure

### Logs

Defined in [`Logs`](src/xrpl/basics/Log.h):

- Central manager for all logging in the application.
- Manages log sinks (destinations), log file handling, and severity thresholds.
- Provides thread-safe access to log sinks via mutexes.
- Supports log file rotation and dynamic adjustment of log thresholds.
- Maintains a map of sinks, each associated with a partition name (e.g., "LedgerMaster", "LoadMonitor").

Key methods:
- `open(boost::filesystem::path const& pathToLogFile)`: Opens the log file.
- `get(std::string const& name)`: Returns a reference to the sink for a given partition.
- `operator[](std::string const& name)`: Same as `get`.
- `journal(std::string const& name)`: Returns a `beast::Journal` for the partition.
- `threshold() const`: Returns the current global log threshold.
- `rotate()`: Rotates the log file.

### Sink

Defined as a nested class in [`Logs`](src/xrpl/basics/Log.h):

- Inherits from `beast::Journal::Sink`.
- Represents a log destination for a specific partition.
- Filters messages by severity threshold.
- Forwards log messages to the `Logs` manager for formatting and output.
- Methods:
  - `write(beast::severities::Severity level, std::string const& text)`: Writes a log message if above threshold.
  - `writeAlways(beast::severities::Severity level, std::string const& text)`: Writes a log message regardless of threshold.

### File

Defined as a nested class in [`Logs`](src/xrpl/basics/Log.h):

- Manages log file operations.
- Methods:
  - `isOpen() const noexcept`: Checks if the log file is open.
  - `open(boost::filesystem::path const& path)`: Opens the log file.
  - `closeAndReopen()`: Closes and reopens the log file (for rotation).
  - `close()`: Closes the log file.
  - `write(char const* text)`, `writeln(char const* text)`: Writes to the log file.

### DebugSink and DebugLog

Defined in [`Log.cpp`](src/libxrpl/basics/Log.cpp):

- `DebugSink` is a singleton that allows dynamic replacement and retrieval of a debug log sink.
- `setDebugLogSink(std::unique_ptr<beast::Journal::Sink> sink)`: Sets the debug log sink.
- `debugLog()`: Returns a `beast::Journal` for debug logging.
- Used for logging in contexts where a partitioned sink is not available.

### Macros: JLOG and CLOG

Defined in [`Log.h`](src/xrpl/basics/Log.h):

- `JLOG(x)`: Utility macro for logging; only logs if the stream is active.
- `CLOG(ss)`: Utility macro for conditional logging; only logs if the stream is active.

Example usage:
```cpp
JLOG(journal_.warn()) << "Server stalled for " << timeSpentStalled.count() << " seconds.";
```

---

## Log Message Formatting and Output

Implemented in [`Log.cpp`](src/libxrpl/basics/Log.cpp):

- Log messages are formatted with timestamps, severity levels, and partition names.
- Sensitive information (e.g., seeds, passphrases) is scrubbed from output.
- Messages are truncated if they exceed a maximum length.
- Example format:
  ```
  2024-06-01T12:34:56Z LedgerMaster:WRN Server stalled for 10 seconds.
  ```

- The `Logs::format` method handles formatting and scrubbing.

---

## Log Sinks and Partitions

- Each log message is associated with a partition (e.g., "LedgerMaster", "LoadMonitor").
- Partitions allow for fine-grained control over log output and filtering.
- Sinks are managed in a map keyed by partition name.
- The `Logs` class provides methods to retrieve or create sinks for partitions.

---

## Log File Management and Rotation

- Log files are managed by the `Logs::File` class.
- Log rotation is supported via the `rotate()` method.
- The `doLogRotate` RPC handler ([LogRotate.cpp](src/xrpld/rpc/handlers/LogRotate.cpp)) allows log rotation to be triggered via RPC:
  ```cpp
  context.app.getPerfLog().rotate();
  return RPC::makeObjectValue(context.app.logs().rotate());
  ```

---

## Thread Safety

- All access to sinks and log file operations is protected by mutexes.
- The `Logs` class uses a `std::mutex` to guard its internal state.
- The `DebugSink` singleton uses its own mutex for thread-safe replacement and retrieval.

---

## Performance Logging (PerfLog)

Defined in [`PerfLog.h`](src/xrpld/perflog/PerfLog.h) and implemented in [`PerfLogImp.cpp`](src/xrpld/perflog/detail/PerfLogImp.cpp):

- `PerfLog` is an interface for performance logging, tracking RPC calls and job queue activities.
- `PerfLogImp` implements the interface, maintaining counters for started, finished, and errored RPCs and jobs.
- Performance logs are written to a separate file, managed by `PerfLogImp`.
- Log rotation and reporting are supported.
- Methods include:
  - `rpcStart`, `rpcFinish`, `rpcError`: Track RPC lifecycle.
  - `jobQueue`, `jobStart`, `jobFinish`: Track job queue activity.
  - `countersJson`, `currentJson`: Report statistics as JSON.
  - `rotate()`: Rotate the performance log file.

- The performance logger runs in its own thread, periodically writing reports.

---

## Integration with Application Modules

- Logging is included in all major modules via `#include <xrpl/basics/Log.h>`.
- Example modules using logging:
  - Ledger management (`LedgerMaster`, `LedgerHistory`)
  - Consensus (`RCLConsensus`)
  - Network operations (`NetworkOPs`)
  - Transaction processing
  - Database backends
  - Resource management
  - Performance logging

- Logging is used for:
  - Debugging and tracing execution
  - Reporting errors and warnings
  - Auditing significant events
  - Instrumentation and performance monitoring

- Example usage in modules:
  ```cpp
  JLOG(journal_.debug()) << "Loading specified Ledger";
  JLOG(journal_.warn()) << "Server stalled for " << timeSpentStalled.count() << " seconds.";
  JLOG(journal_.fatal()) << "Unable to open performance log " << setup_.perfLog << ".";
  ```

---

## References to Source Code

- [Log.h](src/xrpl/basics/Log.h)
- [Log.cpp](src/libxrpl/basics/Log.cpp)
- [PerfLog.h](src/xrpld/perflog/PerfLog.h)
- [PerfLogImp.h](src/xrpld/perflog/detail/PerfLogImp.h)
- [PerfLogImp.cpp](src/xrpld/perflog/detail/PerfLogImp.cpp)
- [LogRotate.cpp](src/xrpld/rpc/handlers/LogRotate.cpp)
- [LedgerHistory.cpp](src/xrpld/app/ledger/LedgerHistory.cpp)
- [Application.cpp](src/xrpld/app/main/Application.cpp)
- [NetworkOPs.cpp](src/xrpld/app/misc/NetworkOPs.cpp)
- [JobTypeData.h](src/xrpld/core/JobTypeData.h)
- [beast/utility/Journal.h](src/xrpl/beast/utility/Journal.h)

---

## Source Code Snippets

**Log Severity Enum:**
```cpp
enum LogSeverity {
  lsINVALID = 1,
  lsTRACE = 0,
  lsDEBUG = 1,
  lsINFO = 2,
  lsWARNING = 3,
  lsERROR = 4,
  lsFATAL = 5
};
```
([Log.h](src/xrpl/basics/Log.h))

**Logs Class (partial):**
```cpp
class Logs {
  // ...
  std::mutex mutable mutex_;
  std::map<std::string, std::unique_ptr<beast::Journal::Sink>, boost::beast::iless> sinks_;
  beast::severities::Severity thresh_;
  File file_;
  // ...
  bool open(boost::filesystem::path const& pathToLogFile);
  beast::Journal::Sink& get(std::string const& name);
  beast::Journal journal(std::string const& name);
  beast::severities::Severity threshold() const;
  bool rotate();
  // ...
};
```
([Log.h](src/xrpl/basics/Log.h))

**Sink Write Method:**
```cpp
void Logs::Sink::write(beast::severities::Severity level, std::string const& text) {
  if (level < threshold()) return;
  logs_.write(level, partition_, text, console());
}
```
([Log.cpp](src/libxrpl/basics/Log.cpp))

**Log File Write:**
```cpp
void Logs::File::write(char const* text) {
  if (m_stream != nullptr) {
    (*m_stream) << text;
  }
}
```
([Log.cpp](src/libxrpl/basics/Log.cpp))

**Debug Log Singleton:**
```cpp
beast::Journal debugLog() {
  return beast::Journal(debugSink().get());
}
```
([Log.cpp](src/libxrpl/basics/Log.cpp))

**JLOG Macro:**
```cpp
#ifndef JLOG
#define JLOG(x) \
  if (!x)     \
  {           \
  }           \
  else        \
  x
#endif
```
([Log.h](src/xrpl/basics/Log.h))

**PerfLog Interface:**
```cpp
class PerfLog {
public:
  virtual void rpcStart(std::string const& method, std::uint64_t requestId) = 0;
  virtual void rpcFinish(std::string const& method, std::uint64_t requestId) = 0;
  virtual void rpcError(std::string const& method, std::uint64_t requestId) = 0;
  virtual void jobQueue(JobType const type) = 0;
  virtual void jobStart(JobType const type, microseconds dur, steady_time_point startTime, int instance) = 0;
  virtual void jobFinish(JobType const type, microseconds dur, int instance) = 0;
  virtual Json::Value countersJson() const = 0;
  virtual Json::Value currentJson() const = 0;
  virtual void resizeJobs(int const resize) = 0;
  virtual void rotate() = 0;
};
```
([PerfLog.h](src/xrpld/perflog/PerfLog.h))

---

## Assessment

- **Explain the role of the `Logs` class in the XRPL logging infrastructure.**
- **Describe how log severity levels are used to filter log messages.**
- **How does the logging system ensure thread safety?**
- **What is the purpose of the `PerfLog` interface and its implementation?**
- **How can log rotation be triggered in the XRPL server?**
- **What is the function of the `JLOG` macro?**

---

## Further Reading

- [Log.h](src/xrpl/basics/Log.h)
- [Log.cpp](src/libxrpl/basics/Log.cpp)
- [PerfLog.h](src/xrpld/perflog/PerfLog.h)
- [PerfLogImp.cpp](src/xrpld/perflog/detail/PerfLogImp.cpp)
- [LogRotate.cpp](src/xrpld/rpc/handlers/LogRotate.cpp)
- [beast/utility/Journal.h](src/xrpl/beast/utility/Journal.h)

---

**End of Lesson Plan**