# `lookupcache` API Reference

## Overview

The `lookupcache` library provides services to cache database lookup data in memory. It is designed to load data at application startup and provide fast, in-memory access to that data, reducing the need for repeated database queries.

## Library Version

**Version:** `0.1.5`

## Configuration

Configuration is managed via environment variables.

### Database Settings

| Variable Name | Description | Default |
| :--- | :--- | :--- |
| `LOOKUP_DATABASE_HOST` | Hostname for the Lookup database. | (required) |
| `LOOKUP_DATABASE_PORT` | Port for the Lookup database. | `1433` |
| `LOOKUP_DATABASE_USER_NAME` | Username for the Lookup database. | (required) |
| `LOOKUP_DATABASE_PASSWORD` | Password for the Lookup database. | (required) |
| `LOOKUP_DATABASE_NAME` | Name of the Lookup database. | `TIBCO_LOOKUP_Tables_Dev` |
| `LOOKUP_DATABASE_DRIVER` | ODBC driver for the Lookup database. | `ODBC Driver 18 for SQL Server` |
| `LOOKUP_DATABASE_ECHO` | Enable SQL query logging (`True`/`False`). | `False` |
| `LOOKUP_DATABASE_POOL_SIZE` | Database connection pool size. | `10` |
| `LOOKUP_DATABASE_MAX_OVERFLOW` | Max temporary connections over pool size. | `20` |
| `LOOKUP_DATABASE_POOL_TIMEOUT` | Connection acquisition timeout (seconds). | `30` |
| `LOOKUP_DATABASE_POOL_RECYCLE` | Reconnect stale connections after (seconds). | `1800` |
| `LOOKUP_DATABASE_POOL_PRE_PING`| Check connection validity before use (`True`/`False`). | `True` |
| `LOOKUP_DATABASE_TRUST_SERVER_CERTIFICATE` | Trust server certificate (`yes`/`no`). | `yes` |
| `LOOKUP_DATABASE_URL` | The full connection URL for the lookup database. Example: `postgresql://user:password@localhost:5432/mydatabase` | |

### Cache Settings

| Variable Name | Description | Default |
| :--- | :--- | :--- |
| `LOOKUP_CACHE_CACHE_SIZE` | The maximum number of cache regions to store. | `20` |

## Core Concepts / How It Works

1.  **Database Engine**: `LookupDatabaseEngine` creates a singleton SQLAlchemy engine with a connection pool based on the `LOOKUP_DATABASE_URL` environment variable.
2.  **Caching**: `LookupCache` uses `dogpile.cache` to create a simple in-memory cache region. Data is stored indefinitely until the application process restarts.
3.  **Dynamic Models**: When `run_select_and_cache` is called, it inspects the columns and data types of the SQL query result and dynamically generates a `pydantic.BaseModel` (via `sqlmodel.SQLModel`) to represent the data structure. This allows caching of arbitrary query results without pre-defining models.
4.  **Retrieval**: `get` and `get_by_columns` perform a linear scan through the cached list of model instances for the given `table_name` to find a match.

## API Reference

### `lookup` Package

#### `run_select_and_cache`

Executes a SQL query and caches its results in memory under a specified `table_name`. This is the primary function for loading data into the cache. It dynamically creates a `SQLModel` based on the query's result set.

- **Parameters:**
  - `session` (`sqlalchemy.orm.Session`): An active SQLAlchemy session.
  - `query` (`str`): The SQL `SELECT` statement to execute.
  - `table_name` (`str`): A unique name to identify this cached dataset. This name is used for subsequent retrievals.

- **Returns:**
  - `List[SQLModel]`: A list of `SQLModel` instances representing the cached rows.

- **Example Usage:**
  ```python
  from lookup import get_lookup_session, run_select_and_cache
  from contextlib import asynccontextmanager
  from fastapi import FastAPI

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Load data on startup
      with get_lookup_session() as session:
          run_select_and_cache(session, "SELECT Carrier, Server FROM Proship", "Proship")
          run_select_and_cache(session, "SELECT * FROM another_table", "AnotherTable")
      yield
      # Cleanup if needed
  ```

#### `get_by_columns`

Retrieves a single record from the cache that matches a dictionary of filter criteria. The match is case-insensitive.

- **Parameters:**
  - `table_name` (`str`): The name under which the data was cached (e.g., `"Proship"`).
  - `filters` (`Dict[str, Any]`): A dictionary where keys are column names and values are the values to match.

- **Returns:**
  - `dict`: A dictionary representing the first matching row, or an empty `dict` if no match is found.

- **Example Usage:**
  ```python
  from lookup import get_by_columns

  # Assuming "Proship_Transfer_Service" was cached previously
  filters = {'brand': '04', 'country': 'US'}
  result = get_by_columns("Proship_Transfer_Service", filters)

  if result:
      print(f"Found matching record: {result}")
  ```

#### `get`

A convenience function to retrieve a single record by matching a single column's value.

- **Parameters:**
  - `table_name` (`str`): The name of the cached dataset.
  - `column` (`str`): The column name to filter on.
  - `value` (`Any`): The value to match in the specified column.

- **Returns:**
  - `dict`: A dictionary representing the first matching row, or an empty `dict` if no match is found.

- **Example Usage:**
  ```python
  from lookup import get

  # Get a record from the "Proship" cache where the "Carrier" is "UPS"
  result = get("Proship", "Carrier", "UPS")
  ```

#### `get_lookup_session`

A context manager that provides a SQLAlchemy `Session` for database operations, configured with the connection settings from the environment variables.

- **Parameters:**
  - None

- **Returns:**
  - `sqlalchemy.orm.Session`: A database session (yielded).

- **Example Usage:**
  ```python
  from lookup import get_lookup_session

  with get_lookup_session() as session:
      # perform database operations if needed, e.g., loading cache
      pass
  ```

## Error Handling / Exceptions

The library uses standard Python exceptions and SQLAlchemy exceptions for database connectivity issues. Ensure that the database connection parameters are correctly configured in the environment variables to avoid connection errors during startup.