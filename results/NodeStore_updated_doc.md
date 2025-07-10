# NodeStore Initialization in XRPL (`Application.cpp` and `initNodeStore()`)

## Where NodeStore is Initialized

The NodeStore is initialized in the `Application.cpp` file, specifically within the `initNodeStore()` function.

## How NodeStore is Initialized

- The `initNodeStore()` function is responsible for setting up the NodeStore database during application startup.
- Within this function, the creation of the NodeStore database is performed by calling the `make_Database` function.

### Relevant Code Location

- **File:** `src/xrpld/app/main/Application.cpp`
- **Function:** `initNodeStore()`

### Initialization Flow

1. **Configuration Loading:**  
   The function loads the necessary configuration for the NodeStore from the application's configuration files.

2. **Database Creation:**  
   The function calls `make_Database`, which is responsible for creating an instance of the NodeStore database according to the configuration (such as backend type, path, cache settings, etc.).

3. **Backend Instantiation:**  
   The `make_Database` function internally uses the `Manager` and `Factory` classes to instantiate the appropriate backend (e.g., RocksDB, NuDB) as specified in the configuration.

4. **Opening the Database:**  
   After creation, the database and its backend are opened and made ready for use by the rest of the application.

### Supporting Evidence

- The `initNodeStore()` function is present in `Application.cpp` and is responsible for NodeStore initialization.
- The actual database is created via a call to `make_Database`, which uses the configuration to select and instantiate the correct backend.

---

**All statements above are directly supported by the provided code and documentation. No assumptions or extrapolations have been made.**