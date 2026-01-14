
### GCS File Handling Pattern

#### Folder Structure
Three primary directories manage file lifecycle within the GCS bucket:

*   **`input/`**: Landing zone for raw data (`.txt`) and trigger (`.trg`) files.
*   **`processed/`**: Archive for successfully processed data records.
*   **`error/`**: Destination for files from total failures or logs of individual record failures.

#### File Naming & Triggering Rules

##### 1. File Pairs
Input data arrives in `input/` as pairs:
*   **Data File**: `.txt` extension, contains wholesale cost data.
*   **Trigger File**: `.trg` extension, zero-byte file, signals data file readiness.

**Naming Convention**: Trigger files must match the data file's base name (e.g., `input/<base_filename>.txt` and `input/<base_filename>.trg`).

##### 2. Event Trigger
The application listens for GCS `google.cloud.audit.log.v1.written` events via Eventarc.
*   Processing is initiated **only** when a `.trg` file is created in `input/`.
*   `.txt` file creation events are ignored to prevent race conditions and infinite loops.

#### File Handling Logic - Post Processing State
This section details the final file locations after processing:

##### 1. Successful Processing:
*   **`input/`**: Original `.txt` file is **deleted**. Original `.trg` file remains for GCS lifecycle cleanup.
*   **`processed/`**: A new, timestamped file (`<Time>_<Name>.txt`) is **created** with all successfully processed records.
*   **`error/`**: Remains empty.

##### 2. Partial Failure:
*   **`input/`**: Original `.txt` file is **deleted**. Original `.trg` file remains for GCS lifecycle cleanup.
*   **`processed/`**: A new, timestamped file (`<Time>_<Name>.txt`) is **created** with only successfully processed records.
*   **`error/`**: A new, timestamped error log (`<Time>_<Name>.errors`) is **created** with raw lines of failed records.

##### 3. Total Failure:
*   **`input/`**: Original `.txt` file is **moved** to `error/`. Original `.trg` file remains for GCS lifecycle cleanup.
*   **`processed/`**: Remains empty.
*   **`error/`**: The original data file (`<Name>.txt`) is now located here.
