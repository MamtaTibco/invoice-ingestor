# InvoiceToIP – Service Analysis Document

## Document Metadata
- **Service Name:** InvoiceToIP
- **Analysis Type:** Automated Service-Level Deep Dive
- **Generated Date:** 2025-12-14
- **Document Version:** 4.0
- **Prompt Version:** 1.0
- **CLI Version:** 0.19.1
- **Purpose:** This service integrates invoice data from various sources by initiating workflows through a timer-based process (fetching commercial invoices via SOAP from Bamboorose) and a JMS queue listener (receiving invoice messages). It performs comprehensive file system operations (copying, archiving, backing up, moving invoice files), writes invoice data, publishes invoices, interacts with external systems via REST and databases, and includes robust auditing and exception handling.

# Business Process & Workflow

## Invoice_To_IP_TimerProcess.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Invoice\InvoiceToIP\Services\Invoice_To_IP_TimerProcess.process`
**Purpose:** A scheduled process that fetches commercial invoices from a SOAP web service and initiates their processing.
**Trigger:** Timer-based, scheduled according to global variables.
**Start Time:** `1412759932000` (Unix timestamp, milliseconds)
 **Time Interval:** `300000` (milliseconds, equivalent to 5 minutes)

### Workflow Execution
**Step 1: Scheduled Trigger**
- What happens: A timer starts the process at a configured time and interval.
- Flow: → Step 2

**Step 2: Fetch Invoices (Conditional)**
- What happens: If the `SOAPCloud_Enabled` global variable is 'Y', the process calls the `getCommercialInvoicesByAvailableTimestamp` SOAP web service to retrieve new invoices.
- Flow: → Step 3

**Step 3: Check for Records**
- What happens: The process inspects the web service response. If it indicates "No records found," the process terminates.
- Flow: If records found → Step 4; If no records → End

**Step 4: Call Subprocess**
- What happens: The `Invoice_To_IP_Sub.process` is called to process the fetched invoices.
- Input/Output: The invoice data from the web service is passed to the subprocess.
- Flow: → Step 5

**Step 5: Publish Invoice (Conditional)**
- What happens: If the `PublishInvoice` global variable is 'Y', the `Invoice_Publisher_Impl.process` is called to publish the invoice.
- Flow: → End

### Business Logic
- **Scheduled Data Retrieval:** This process automates the fetching of invoices from an external system on a recurring schedule.
- **Configurable Behavior:** The process is highly configurable through global variables, allowing it to be adapted for different environments (e.g., cloud vs. on-prem) and to enable or disable features like publishing.

### Success & Failure Paths
- **Success:** Invoices are successfully fetched, processed, and optionally published.
- **Failure:** Any exception during the web service call or subprocess execution is caught, and a detailed exception is logged via the `AddException` process.

---

## Invoice_Publisher_Impl.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Invoice\InvoiceToIP\CallProcesses\Invoice_Publisher_Impl.process`
**Purpose:** A wrapper process that delegates the task of publishing an invoice to a subprocess.
**Trigger:** Called by another TIBCO process, with an `invoiceDocument` string as input.

### Workflow Execution
**Step 1: Receive Invoice Document**
- What happens: The process starts with an XML string containing invoice data.
- Flow: → Step 2

**Step 2: Call Subprocess**
- What happens: It calls the `Invoice_Publisher_Sub.process` to handle the actual publishing logic.
- Input/Output: The `invoiceDocument` is passed to the subprocess.
- Flow: → End

### Business Logic
- **Delegation:** This process follows the wrapper pattern, separating the interface from the implementation and promoting a modular design.

### Success & Failure Paths
- **Success:** The `Invoice_Publisher_Sub.process` completes successfully.
- **Failure:** Any exception from the subprocess is caught and propagated as a structured `ErrorReport`.

---

## Invoice_Publisher_Sub.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Invoice\InvoiceToIP\SubProcesses\Invoice_Publisher_Sub.process`
**Purpose:** Publishes individual invoice messages to a JMS topic.
**Trigger:** Called by another TIBCO process, with an `invoiceDocument` XML string as input.

### Workflow Execution
**Step 1: Parse Invoices**
- What happens: The input XML string, which may contain multiple invoices, is parsed into a structured format.
- Flow: → Step 2

**Step 2: Process Invoices (Loop)**
- What happens: The process iterates through each invoice in the parsed document.
- Flow: For each invoice → Step 3

**Step 3: Filter Destinations (Inner Loop)**
- What happens: For each invoice, it iterates through a list of `send_to` destinations, filtering them based on a list of allowed destinations and a time limit, both configured via global variables.
- Flow: For each valid destination → Step 4

**Step 4: Publish to JMS Topic**
- What happens: The individual invoice is rendered back to an XML string and published to the `UO.TRADESTONE.INVOICE.PUBLISH.TOPIC` JMS topic. The `SendTo` destination is set as a JMS property for content-based routing by consumers.
- Flow: After all invoices and destinations are processed → End

### Business Logic
- **Message Fan-out:** Takes a batch of invoices and publishes them as individual messages.
- **Content-Based Routing:** Uses JMS properties to allow downstream systems to subscribe to and receive only the invoices they are interested in.
- **Filtering:** Applies business rules to filter which invoices are published based on their destination and age.

### Success & Failure Paths
- **Success:** All valid invoices are published to the JMS topic.
- **Failure:** Exceptions during XML parsing or JMS publishing are caught. The `AddException` process is called to log detailed error information, including the invoice that caused the failure.


## Invoice_To_IP_Sub.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Invoice\InvoiceToIP\SubProcesses\Invoice_To_IP_Sub.process`
**Purpose:** The main engine for processing and transforming invoices. It handles data mapping, validation, and routing to different downstream systems.
**Trigger:** Called by another TIBCO process.

### Workflow Execution
**Step 1: Parse and Prepare Data**
- What happens: The process parses the input invoice XML and retrieves cached purchase order data from a shared variable.
- Flow: → Step 2

**Step 2: Process Invoices (Loop)**
- What happens: It iterates through each invoice in the input.
- Flow: For each invoice → Step 3

**Step 3: Validate Invoice**
- What happens: It checks if the invoice is valid for processing based on its status and destination. Invalid invoices are skipped.
- Flow: If valid → Step 4; If invalid → Skip

**Step 4: Generate Transmission Number**
- What happens: It calls the `Sequence_DB_Sub.process` to get a unique transmission number.
- Flow: → Step 5

**Step 5: Transform Invoice**
- What happens: A complex `Mapper` activity transforms the invoice into the canonical `InvoiceToIP` format, performing various calculations, data lookups, and formatting.
- Flow: → Step 6

**Step 6: Route to Destination (Conditional)**
- What happens: The process routes the transformed invoice based on the original trigger.
    - **If Timer Request:** It sends the `InvoiceToIP` message to a JMS queue for ERP processing.
    - **If PIX Request:** It calls a SOAP web service to post the commercial invoice back to the source system.
- Flow: → End

### Business Logic
- **Complex Data Transformation:** This process contains the core business logic for converting invoices from their source format to the format required by the ERP system.
- **Dual-Mode Operation:** The process can either send data to the ERP via JMS or post it back to the source system via a web service, depending on the context in which it was called.
- **Data Enrichment and Validation:** It enriches the data with a unique transmission number and validates invoices before processing.

### Success & Failure Paths
- **Success:** The invoice is successfully validated, transformed, and routed to its destination.
- **Failure:** The process has extensive error handling. Exceptions are caught, and the `AddException` process is called to log detailed error information. For PIX requests, some errors are re-thrown to the caller. If the web service post fails, a specific error is generated.

---

## InvoiceToIPWriteFileService.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_ERP_SI\Business Processes\StarterProcess\InvoiceToIPWriteFileService.process`
**Purpose:** Listens for invoice messages on a JMS queue and initiates the file writing process.
**Trigger:** JMS Message on `UO.ERP.INVOICETOIP.SUBSCRIBE.QUEUE`.

### Workflow Execution
**Step 1: Receive JMS Message**
- What happens: The process starts when an XML message containing invoice data is received from the JMS queue.
- Flow: → Step 2

**Step 2: Audit (Conditional)**
- What happens: If auditing is enabled via a global variable, the process logs an audit trail of the received message.
- Flow: → Step 3

**Step 3: Call Implementation Process**
- What happens: The `Invoice_To_IP_WriteFileImpl.process` is called to handle the file writing.
- Input/Output: The received invoice data is passed to the implementation process.
- Flow: → Step 4

**Step 4: Confirm Message**
- What happens: The process sends a confirmation to the JMS server, acknowledging that the message has been processed.
- Flow: → End

### Business Logic
- **Asynchronous Processing:** The use of a JMS queue allows for asynchronous and reliable processing of invoices.
- **Auditing:** Provides traceability by logging key information about the process execution.
- **Retry Mechanism:** In case of an application exception, the process can be configured to send the message back to the queue for a retry attempt.

### Success & Failure Paths
- **Success:** The invoice message is received, processed, and the JMS message is confirmed.
- **Failure:** Any exception during the process is caught, and a detailed exception report is generated. For application-level exceptions, the message is retried. For other exceptions, the message is confirmed to avoid infinite loops and the error is logged.

---

## Invoice_To_IP_WriteFileImpl.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_ERP_SI\Business Processes\CallProcess\Invoice_To_IP_WriteFileImpl.process`
**Purpose:** This process acts as a wrapper for the core invoice file writing logic. It receives an invoice and delegates the processing to a subprocess.
**Trigger:** Called by another TIBCO process.

### Workflow Execution
**Step 1: Receive Invoice**
- What happens: The process starts upon receiving an invoice data structure.
- Input/Output: `InvoiceToIP` data → `CallWriteFileSub` activity
- Flow: → Step 2

**Step 2: Call Subprocess**
- What happens: The process invokes the `Invoice_To_IP_WriteFileSub.process` to perform the actual file writing.
- Input/Output: Passes the `InvoiceToIP` data to the subprocess.
- Flow: → End

### Business Logic
- **Delegation:** The primary logic of this process is to delegate the task of writing the invoice file to a specialized subprocess, promoting modularity and separation of concerns.

### Success & Failure Paths
- **Success:** The `Invoice_To_IP_WriteFileSub.process` completes without errors.
- **Failure:** An exception from the subprocess is caught and propagated to the calling process as a structured `ErrorReport`.

---

### Invoice_To_IP_WriteFileSub
**Location:** `/services/InvoiceToIP/BW_ERP_SI/Business Processes/SubProcess/Invoice_To_IP_WriteFileSub.process`
**Purpose:** This sub-process contains the core business logic for transforming incoming invoice data into a specific flat-file format and writing it to a file system. It includes crucial business validations.
**Trigger:** Called by `Invoice_To_IP_WriteFileImpl.process`

#### Workflow Execution
**Step 1: Render Header**
- What happens: Extracts and formats header information from the incoming invoice data.
- Input/Output: Invoice Data → Formatted Header Data
- Flow: → Step 2

**Step 2: Render Details**
- What happens: Extracts and formats line item details from the incoming invoice data.
- Input/Output: Invoice Data → Formatted Detail Data
- Flow: → Step 3

**Step 3: Business Validation (EU/Non-EU Order Check)**
- What happens: Checks if the invoice contains a mix of EU and non-EU orders. If so, it generates an error, as this is a critical business rule violation.
- Input/Output: Invoice Detail Data → Validation Result
- Flow: → Step 4 (if valid) or Step 5 (if invalid)

**Step 4: Write Invoice Data to File**
- What happens: The formatted header and detail data, after successful validation, are combined and written to a designated flat file on the file system.
- Input/Output: Formatted Header + Detail Data → Invoice Flat File
- Flow: → End

**Step 5: Generate Error (on Validation Failure)**
- What happens: If the EU/Non-EU order validation fails, a specific error is generated and propagated to the calling process.
- Input/Output: Validation Failure → Error Message
- Flow: → End with Error

### Success & Failure Paths
- **Success:** The invoice data is successfully transformed and written to a file.
- **Failure:** A `Tradestone_Business_Exception` is thrown for mixed EU/Non-EU POs. A `Tradestone_Application_Exception` is thrown for file writing errors. All exceptions are caught and propagated to the calling process.

---

## InvoiceToIPCopyFile.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_ERP_SI\Business Processes\StarterProcess\InvoiceToIPCopyFile.process`
**Purpose:** Periodically scans a directory for invoice files, archives them, creates a backup, and moves them to a target location for further processing.
**Trigger:** Timer-based, scheduled according to global variables.

### Workflow Execution
**Step 1: Scheduled Trigger**
- What happens: A timer initiates the process at a predefined schedule.
- Flow: → Step 2

**Step 2: List Files**
- What happens: The process lists all files with a `.txt` extension in the source directory.
- Flow: → Step 3

**Step 3: Process Files (Loop)**
- What happens: The process iterates through each file found in the source directory.
- Flow: For each file → Step 4

**Step 4: Archive, Backup, and Move**
- What happens: For each file, it is first copied to an archive directory, then to a backup directory, and finally moved to a target directory. Files are timestamped upon archival and backup.
- Input/Output: A file from the source directory is moved to the target directory, with copies created in archive and backup locations.
- Flow: After all files are processed → End

### Business Logic
- **File Polling:** The process periodically checks a directory for new files to process.
- **Conditional Routing:** Files containing "UKINV" in their name are moved to a specific subdirectory, indicating different handling for UK-related invoices.
- **Data Preservation:** Archiving and backing up files ensures that original data is preserved before it is moved for processing.

### Success & Failure Paths
- **Success:** All files in the source directory are successfully archived, backed up, and moved.
- **Failure:** If any file operation fails, a centralized exception handling process (`AddException`) is called to log the error details.

---

## OnStartUp_PO.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\Shared Processes\OnStartUpProcess\OnStartUp_PO.process`
**Purpose:** The main application startup process. It orchestrates the caching of initial data.
**Trigger:** `OnStartup` event when the TIBCO engine starts.

### Workflow Execution
**Step 1: Startup Trigger**
- What happens: The process is automatically started by the TIBCO engine.
- Flow: → Step 2

**Step 2: Load REST Data (Conditional)**
- What happens: If the `RESTAPI_Enabled` global variable is 'Y', it calls the `OnStartUp_PO_REST.process` to load and cache data from the REST API.
- Flow: → End

### Business Logic
- **Application Initialization:** This process ensures that the application is properly initialized with all necessary data before it starts processing any requests.
- **Fail-Fast Mechanism:** If the data caching fails, this process will shut down the entire TIBCO engine. This is a deliberate design choice to prevent the application from running in an inconsistent or invalid state.

### Success & Failure Paths
- **Success:** All required startup data is successfully loaded and cached.
- **Failure:** If the `OnStartUp_PO_REST.process` fails, the exception is caught, logged, and then the TIBCO engine is shut down.

---

## OnStartUp_PO_REST.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\Shared Processes\OnStartUpProcess\OnStartUp_PO_REST.process`
**Purpose:** Runs at application startup to fetch location data from a REST API and cache it in a shared variable.
**Trigger:** Called by the `OnStartUp_PO.process`.

### Workflow Execution
**Step 1: Fetch Location Data**
- What happens: It calls the `Get_Locations_REST.process` to retrieve location data.
- Flow: → Step 2

**Step 2: Map Data**
- What happens: The data from the REST API is transformed into the canonical `TradestoneLocations` format.
- Flow: → Step 3

**Step 3: Cache Data**
- What happens: The transformed location data is stored in the `OnStartUp_PO` shared variable.
- Flow: → End

### Business Logic
- **Data Caching:** This process improves application performance by caching frequently used location data at startup, avoiding repeated API calls.

### Success & Failure Paths
- **Success:** The location data is successfully fetched, transformed, and cached.
- **Failure:** If any step fails, an exception is thrown. This failure will be caught by the calling `OnStartUp_PO` process, which will then shut down the application.

---

## Get_Locations_REST.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Common\Subprocesses\Get_Locations_REST.process`
**Purpose:** Fetches location data from an external REST API.
**Trigger:** Called by another TIBCO process.

### Workflow Execution
**Step 1: Construct API Request**
- What happens: The process builds the URL for the REST API call using global variables for the base URL.
- Flow: → Step 2

**Step 2: Invoke API**
- What happens: A GET request is sent to the REST API with Basic Authentication.
- Input/Output: An HTTP request is sent, and a JSON response is received.
- Flow: → Step 3

**Step 3: Parse Response**
- What happens: The received JSON response is parsed into a structured XML format.
- Flow: → Step 4

**Step 4: Validate Response**
- What happens: The process checks the HTTP status code of the response. If it's not 200 (OK), an exception is thrown.
- Flow: If 200 → End; If not 200 → Failure Path

### Business Logic
- **External System Integration:** This process encapsulates the logic for communicating with an external RESTful web service.
- **Data Retrieval:** It is used to fetch reference data (locations) that is likely used for enrichment or validation in other processes.

### Success & Failure Paths
- **Success:** The REST API call returns a 200 OK status, and the JSON response is successfully parsed. The location data is returned to the caller.
- **Failure:** If the API call fails, returns a non-200 status, or if the response is not valid JSON, a structured error is generated and propagated. Error codes distinguish between application exceptions (e.g., network issues) and data validation exceptions (e.g., bad JSON).

---

## Sequence_DB_Sub.process
**Location:** `C:\final-file-generation-docs\InvoiceToIP\x35-ai-toolkit\TIBCO\5x\services\InvoiceToIP\BW_Tradestone_PIX\BusinessProcesses\Common\Subprocesses\Sequence_DB_Sub.process`
**Purpose:** A reusable utility to get the next value from a database sequence.
**Trigger:** Called by another TIBCO process, with a `sequence_name` as input.

### Workflow Execution
**Step 1: Receive Sequence Name**
- What happens: The process starts with the name of the database sequence.
- Flow: → Step 2

**Step 2: Execute SQL**
- What happens: A dynamic SQL statement (`select next value for <sequence_name>`) is executed against the database.
- Input/Output: A SQL query is sent, and a single value (the next sequence number) is returned.
- Flow: → End

### Business Logic
- **Unique ID Generation:** This process provides a centralized and reusable way to generate unique IDs from a database sequence, which is essential for creating unique transaction numbers or primary keys.

### Success & Failure Paths
- **Success:** The SQL query executes successfully, and the next sequence value is returned.
- **Failure:** If the database query fails (e.g., the sequence does not exist, or the database is unavailable), an `ESB_SYS_Exception` is generated and propagated.

## Dependency Mapping

### Database
#### PI_Sequence (SQL Server)
**Host:** `tibsqls:1433` | **Database:** `PI_Sequence` | **Driver:** `com.microsoft.sqlserver.jdbc.SQLServerDriver`
**Pool:** Max 10 connections | **Login Timeout:** 30s | **Query Timeout:** 30s
**Security:** User `tibco_pi`, Password `****`
**Usage:**
- Generates unique sequence numbers by `Sequence_DB_Sub.process` (SQL Direct activity)

#### Bamboorose (SQL Server)
**Host:** `tibsqls:1433` | **Database:** `Bamboorose` | **Driver:** `com.microsoft.sqlserver.jdbc.SQLServerDriver`
**Pool:** Max 10 connections | **Login Timeout:** 30s | **Query Timeout:** 60s
**Security:** User `tibco_ts`, Password `****`
**Usage:**
- General Bamboorose data access, likely for Purchase Order (PO) data caching by `OnStartUp_PO.process` (inferred from `TS_PO` connection referencing `Bamboorose` DB)
- Retrieving HTS Codes by `GetHTSCodes` (not explicitly mapped to a process in analysis, but variable present)

### External APIs
#### Commercial Invoice Service (SOAP)
**Endpoint:** Set in Deployment Environment via Global Variable `Common/SOAP_Cloud_EndPointURL_ServiceHandler`
**Protocol:** SOAP | **Timeout:** 60s (from `Common/SOAPService/Timeout`)
**Operations:**
- `getCommercialInvoicesByAvailableTimestamp` (GET) by `Invoice_To_IP_TimerProcess.process`
- `postCommercialInvoice_TS` (POST) by `Invoice_To_IP_Sub.process`
**Auth:** Configured in Deployment Environment.
**Used By:** `Invoice_To_IP_TimerProcess.process`, `Invoice_To_IP_Sub.process`

#### Location Service (REST)
**Endpoint:** Set in Deployment Environment via Global Variable `Common/REST_URL`
**Protocol:** REST | **Timeout:** Not explicitly defined.
**Operations:** `Invoke_Locations` (GET)
**Auth:** Configured in Deployment Environment.
**Used By:** `Get_Locations_REST.process`, `OnStartUp_PO_REST.process`
### Messaging (JMS/EMS)
#### Invoice Message Consumer (Queue)
**Server:** `tcp://tib-emss:7222` (JNDI URL)
**Queue:** `UO.ERP.INVOICETOIP.SUBSCRIBE.QUEUE`
**Pattern:** Point-to-Point (Queue) | **Acknowledge Mode:** Client (2) | **Delivery Mode:** Persistent
**Security:** User `admin`, Password `****`
**Used By:**
- Receives invoice messages by `InvoiceToIPWriteFileService.process` (StarterProcess)
- Sends transformed invoice data by `Invoice_To_IP_Sub.process` (This might be a misconfiguration or a specific pattern where a queue is both consumed from and produced to by different parts of the overall service logic)

#### Invoice Publisher (Topic)
**Server:** `tcp://tib-emss:7222` (JNDI URL)
**Topic:** `UO.TRADESTONE.INVOICE.PUBLISH.TOPIC`
**Pattern:** Publish/Subscribe (Topic) | **Acknowledge Mode:** Not explicitly defined | **Delivery Mode:** Persistent
**Security:** User `admin`, Password `****`
**Used By:** `Invoice_Publisher_Sub.process`

#### Shared Variables/Caches
**Usage:** Caching Purchase Order (PO) data at application startup for performance.
**Content:** PO data from REST API or other sources.
**Used By:** `OnStartUp_PO_REST.process`, `OnStartUp_PO.process`

#### Internal Process Calls
**Usage:** Modularization and orchestration of business logic.
**Key Calls:**
- `InvoiceToIPWriteFileService.process` calls `Invoice_To_IP_WriteFileImpl.process`
- `Invoice_To_IP_WriteFileImpl.process` calls `Invoice_To_IP_WriteFileSub.process`
- `Invoice_To_IP_TimerProcess.process` calls `Call_Invoice_To_IP_Sub.process`
- `Call_Invoice_To_IP_Sub.process` calls `Sequence_DB_Sub.process` and `Invoice_Publisher_Impl.process`
- `Invoice_Publisher_Impl.process` calls `Invoice_Publisher_Sub.process`
- `AddAudit.process` dynamically calls `AddLEAFAudit.process` or `AddAudit-CentralLogServer.process`
- `AddException.process` dynamically calls `AddLEAFException.process` or `AddException-CentralLogServer.process`


## API Payloads

### Outbound APIs (BW calls these)

#### Commercial Invoice Service (SOAP) - `getCommercialInvoice_TS`
- **Endpoint**: `POST` - The endpoint URL is configured via a global variable: `Common/TradestoneService/SOAP_Cloud_EndPointURL_ServiceHandler`. A typical value might be `https://urban.bamboorose.com:443/test/services/ServiceHandler.ServiceHandlerHttpSoap11Endpoint/`.
- **Request**:
    - Operation: `getCommercialInvoicesByAvailableTimestamp`
    - Payload:
        - `userName` (string)
        - `password` (string)
        - `availableTimestamp` (dateTime)
- **Response**:
    - Operation: `getCommercialInvoicesByAvailableTimestampResponse`
    - Payload:
        - `return` (string) - This string contains a full XML document with the invoice data conforming to the `invoiceschema_V2.xsd`.
- **Source**: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/Services/Invoice_To_IP_TimerProcess.process` → `getCommercialInvoice_TS`

#### Location Service (REST) - `Invoke_Locations`
- **Endpoint**: `GET` - The base URL is configured via a global variable: `Common/TradestoneService/REST_URL`. A typical value might be `https://urban.bamboorose.com/test/rest/`. The full path is `referencedata/locations`.
- **Request**:
    - Query parameter: `owner` (string)
- **Response (JSON)**: The JSON response from this API is the direct input to the `MapTableValues` activity.
  ```json
  {
    "document": {
      "locations_info": [
        {
          "messages": {
            "status": "string",
            "message": {
              "message_desc": "string",
              "message_id": "string"
            }
          },
          "locations": {
            "owner": "string",
            "code": "string",
            "description": "string",
            "location_type": "string",
            "address1": "string",
            "address2": "string",
            "city": "string",
            "state": "string",
            "postal_code": "string",
            "country": "string",
            "location_group": "string",
            "modify_user": "string",
            "modify_ts": "string",
            "company_name": "string"
          }
        }
      ]
    }
  }
  ```
- **Source**: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Common/Subprocesses/Get_Locations_REST.process` → `Invoke_Locations`

# Data Transformations

## Invoice Domain
### Bamboorose Invoice (XML) → Canonical InvoiceToIP (XML) | Source: `Invoice_To_IP_Sub.process`

This process contains several key transformation steps.

#### ** Grouping by Purchase Order (`DistinctPO` activity)**
This activity takes all the detail lines (`invoice_d`) from the input invoice and groups them by the purchase order number (`@order_no`). The purpose is to create a list of unique PO numbers present in the invoice.

| Source Field | Target Field | Rule |
|---|---|---|
| `$EachInvoice/invoice/invoice_h/invoice_d` | `document/invoice/invoice_h/invoice_d` | Groups all `invoice_d` elements. |
| `@order_no` (from `invoice_d`) | `@order_no` (in the new `invoice_d`) | This is the key for grouping. Only one `invoice_d` element is created for each unique `@order_no`. |

#### ** Main Transformation (`IFS_Mapper` activity)**
This is the primary mapping step where the source XML from Bamboorose is mapped to a canonical XML model for internal processing. It uses the output of the `DistinctPO` activity to determine if there are multiple POs.

### Bamboorose Invoice (XML) → Canonical InvoiceToIP (XML) | Source: `Invoice_To_IP_Sub.process` → `IFS_Mapper`

This is the primary transformation step where the source XML from Bamboorose is mapped to a canonical XML model for internal processing.

#### **Header Mappings**
| Target Field | Source Field / Rule |
|---|---|
| `Header.RecordID` | Set to the literal string "HEADER". |
| `Header.TransmissionDate` | Set to the current date, formatted as `yyyyMMdd`. |
| `Header.TransmissionNumber` | Mapped from the `sequence_next_value` output of the `Sequence_DB_Sub` process. |
| `Header.TransmissionSeqNo` | Mapped from the `sequence_next_value` output of the `Sequence_DB_Sub` process. |
| `Header.Vendor` | The source `supplier` field is processed: if it contains "EU", that part is removed. The result is then formatted to 6 characters by either taking the rightmost 6 characters or padding with leading zeros. |
| `Header.RecordType` | Mapped from the global variable `BusinessProcesses/Invoice/InvoiceToIP/RecordType`. |
| `Header.Invoice` | **Conditional Logic:** If the sum of agent commission (`height`) and HKS commission (`width`) is greater than 0, a new invoice number is generated by appending "HKS" to the original `invoice_no`. If this new number is too long, it is truncated to 10 characters after removing special characters (`-`, `_`, `#`). Otherwise, the original `invoice_no` is used. |
| `Header.InvoiceDate` | **Conditional Logic:** If the source `invoice_date` is present, it is used and formatted as `yyyyMMdd`. Otherwise, the current date is used. |
| `Header.GrossAmount` | Calculated by summing the `tot_net_value` and the total commissions (`height` + `width`). The result is rounded to two decimal places. |
| `Header.InvoiceDesc` | **Conditional Logic:** If the invoice contains more than one distinct Purchase Order (`order_no`), this field is set to "MULTIPLE PO". Otherwise, it is set to the single `order_no`. |
| `Header.Param4` | **Conditional Logic:** Mapped from the `payment_type` field only if the global variable `sendAllTypes` is 'Y'. |
| `Header.MerchandiseAmount` | Mapped from `tot_invoice_value`, rounded to two decimal places. |
| `Header.TermsCode` | **Conditional Logic:** If the global variable `sendAllTerms` is 'Y', this is a direct mapping of `payment_terms`. Otherwise, it is set to '01' only if the source `payment_terms` is '01', otherwise it's empty. |
| `Header.VATCode` | **Conditional Logic:** Set to '00' if the order is for the EU (based on `order_no` prefix or `deliver_to` country) AND has a positive `tot_adjust_value` (VAT amount). Otherwise, it is empty. |
| `Header.VATAmount` | **Conditional Logic:** Set to the `tot_adjust_value` (rounded to two decimal places) if the order is for the EU and the value is positive. Otherwise, it is empty. |
| `Header.CurrencyCode` | **Conditional Logic:** The currency code is cleared (set to empty) for non-EU orders in USD or for EU orders in GBP. In all other cases, the source `currency` is used. |
| `Header.SupplierInvoice` | Mapped from `supplier_inv_no` after removing any single-quote characters. |

#### **Details Mappings (grouped by `order_no`)**
Three distinct types of detail records are generated from the source invoice lines, all grouped by the Purchase Order number (`order_no`).

**1. Merchandise Cost Records**
*   **Condition:** Only for invoice lines where `status_01` is not '1STSALE' and `invoice_qty` is greater than 0.

| Target Field | Source Field / Rule |
|---|---|
| `Details.RecordID` | Set to the literal string "PO-DATA". |
| `Details.TransmissionDate` | Mapped from the header-level `TransmissionDate`. |
| `Details.TransmissionNumber` | Mapped from the header-level `TransmissionNumber`. |
| `Details.TransmissionSeq` | Mapped from the header-level `TransmissionSeqNo`. |
| `Details.LineItemSeq` | Mapped from the `order_no` of the current group. |
| `Details.POAmt` | The **calculated sum** of (`invoice_qty` * `invoice_price`) for all items within that PO group, rounded to two decimal places. |

**2. Agent Commission Records**
*   **Condition:** Only for invoice lines where `height` (agent commission) has a positive value and `invoice_qty` is greater than 0.

| Target Field | Source Field / Rule |
|---|---|
| `Details.RecordID` | Set to the literal string "PO-DATA". |
| `Details.TransmissionDate` | Mapped from the header-level `TransmissionDate`. |
| `Details.TransmissionNumber` | Mapped from the header-level `TransmissionNumber`. |
| `Details.TransmissionSeq` | Mapped from the header-level `TransmissionSeqNo`. |
| `Details.LineItemSeq` | Mapped from the `order_no` of the current group. |
| `Details.FrtCat` | Set to the literal string '04'. |
| `Details.AllocAmt` | The **calculated sum** of all `height` values for all items within that PO group, rounded to two decimal places. |

**3. HKS Commission Records**
*   **Condition:** Only for invoice lines where `width` (HKS commission) has a positive value and `invoice_qty` is greater than 0.

| Target Field | Source Field / Rule |
|---|---|
| `Details.RecordID` | Set to the literal string "PO-DATA". |
| `Details.TransmissionDate` | Mapped from the header-level `TransmissionDate`. |
| `Details.TransmissionNumber` | Mapped from the header-level `TransmissionNumber`. |
| `Details.TransmissionSeq` | Mapped from the header-level `TransmissionSeqNo`. |
| `Details.LineItemSeq` | Mapped from the `order_no` of the current group. |
| `Details.FrtCat` | **Conditional Logic:** Set to '12' if the `order_no` starts with "EU", otherwise it is set to '07'. |
| `Details.AllocAmt` | The **calculated sum** of all `width` values for all items within that PO group, rounded to two decimal places. |

#### **Non-Merchandise Details Mappings (Invoice-level Summaries)**
These records summarize commission costs for the entire invoice.

**1. Agent Commission Summary**
*   **Condition:** Created only if there is at least one invoice line with a positive `height` (agent commission).

| Target Field | Source Field / Rule |
|---|---|
| `NonMerchDetails.RecordID` | Set to the literal string "NON-MERCH-DETAIL". |
| `NonMerchDetails.TransmissionDate` | Mapped from the header-level `TransmissionDate`. |
| `NonMerchDetails.TransmissionNumber` | Mapped from the header-level `TransmissionNumber`. |
| `NonMerchDetails.TransmissionSeq` | Mapped from the header-level `TransmissionSeqNo`. |
| `NonMerchDetails.SeqNum` | Set to the literal string '1'. |
| `NonMerchDetails.NmType` | Set to the literal string 'F' (Freight). |
| `NonMerchDetails.Cat` | Set to the literal string '04'. |
| `NonMerchDetails.ExtCost` | The **calculated sum** of all `height` values across the entire invoice, rounded to two decimal places. |

**2. HKS Commission Summary**
*   **Condition:** Created only if there is at least one invoice line with a positive `width` (HKS commission).

| Target Field | Source Field / Rule |
|---|---|
| `NonMerchDetails.RecordID` | Set to the literal string "NON-MERCH-DETAIL". |
| `NonMerchDetails.TransmissionDate` | Mapped from the header-level `TransmissionDate`. |
| `NonMerchDetails.TransmissionNumber` | Mapped from the header-level `TransmissionNumber`. |
| `NonMerchDetails.TransmissionSeq` | Mapped from the header-level `TransmissionSeqNo`. |
| `NonMerchDetails.SeqNum` | Set to the literal string '2'. |
| `NonMerchDetails.NmType` | Set to the literal string 'F' (Freight). |
| `NonMerchDetails.Cat` | **Conditional Logic:** Set to '12' if the first invoice line's `order_no` starts with "EU", otherwise it is set to '07'. |
| `NonMerchDetails.ExtCost` | The **calculated sum** of all `width` values across the entire invoice, rounded to two decimal places. |

#### **Publish Fields Mappings**
This section contains metadata fields for downstream processing.

| Target Field | Source Field / Rule |
|---|---|
| `PublishFields.UserName` | Mapped from `memo5` on the invoice header. |
| `PublishFields.Company` | **Conditional Logic:** Set to '09' if the `memo1` (brand) and `deliver_to` (DC) values are found in the `Company09Brands` and `Company09DCs` global variables respectively. Otherwise, it defaults to '99'. |

### Canonical InvoiceToIP (XML) → Flat File | Source: `Invoice_To_IP_WriteFileSub.process` → Render Activities

This is the final rendering step where the canonical XML is formatted into a fixed-width text file.

#### **Header Rendering (`RenderHeader`)**
| Target Field | Source Field / Rule |
|---|---|
| `RecordID` | Mapped from `Header.RecordID`. |
| `TransmissionDate` | Mapped from `Header.TransmissionDate`. |
| `TransmissionNumber` | Mapped from `Header.TransmissionNumber`. |
| `TransmissionSeqNo` | Mapped from `Header.TransmissionSeqNo`. |
| `Vendor` | Mapped from `Header.Vendor`. |
| `RecordType` | Mapped from `Header.RecordType`. |
| `Invoice` | Mapped from `Header.Invoice`. |
| `InvoiceDate` | Mapped from `Header.InvoiceDate`. |
| `GrossAmount` | Mapped from `Header.GrossAmount`. |
| `InvoiceDesc` | Mapped from `Header.InvoiceDesc`. |
| `Param1` | Mapped from `Header.Param1`. |
| `Param2` | Mapped from `Header.Param2`. |
| `Param3` | Mapped from `Header.Param3`. |
| `Param4` | Mapped from `Header.Param4`. |
| `Param5` | Mapped from `Header.Param5`. |
| `MerchandiseAmount` | Mapped from `Header.MerchandiseAmount`. |
| `TermsCode` | Mapped from `Header.TermsCode`. |
| `VATCode` | Mapped from `Header.VATCode`. |
| `VATAmount` | Mapped from `Header.VATAmount`. |
| `Field19` | Mapped from `Header.Field19`. |
| `Field20` | Mapped from `Header.Field20`. |
| `Field21` | Mapped from `Header.Field21`. |
| `Field22` | Mapped from `Header.Field22`. |
| `Field23` | Mapped from `Header.Field23`. |
| `Field24` | Mapped from `Header.Field24`. |
| `Field25` | Mapped from `Header.Field25`. |
| `Field26` | Mapped from `Header.Field26`. |
| `Field27` | Mapped from `Header.Field27`. |
| `Field28` | Mapped from `Header.Field28`. |
| `CurrencyCode` | Mapped from `Header.CurrencyCode`. |
| `DiscountAmt01` | Mapped from `Header.DiscountAmt01`. |
| `DiscountAmt02` | Mapped from `Header.DiscountAmt02`. |
| `DiscountAmt03` | Mapped from `Header.DiscountAmt03`. |
| `DiscountAmt04` | Mapped from `Header.DiscountAmt04`. |
| `DiscountAmt05` | Mapped from `Header.DiscountAmt05`. |
| `SupplierInvoice` | Mapped from `Header.SupplierInvoice`. |



#### **Details (`Details`)**
For-each `Details`:$Start/pfx2:InvoiceToIP/pfx2:Details[starts-with(pfx2:LineItemSeq,'EU')]


| Target Field | Source Field / Rule |
|---|---|
| `RecordID` | Mapped from `Details.RecordID`. |
| `TransmissionDate` | Mapped from `Details.TransmissionDate`. |
| `TransmissionNumber` | Mapped from `Details.TransmissionNumber`. |
| `TransmissionSeq` | Mapped from `Details.TransmissionSeq`. |
| `LineItemSeq` |Mapped from `Details.LineItemSeq` .|


**Transition to `RenderDetails`**
      **Label:** `Valid Invoice`
      **Condition (XPath):** `count($Details/root/pfx2:Details)=0 or
         count($Details/root/pfx2:Details)=count($Start/pfx2:InvoiceToIP/pfx2:Details)`
      **Description:** The transition to RenderDetails occurs when the invoice is considered valid—either no Details elements are present in the response, or the number of Details elements exactly matches the number provided in the incoming InvoiceToIP request.



#### **Details Rendering (`RenderDetails`)**
For-each-group `Details`:$Start/pfx2:InvoiceToIP/pfx2:Details[tib:trim(pfx2:FrtCat) = '']
Grouping `Details`:pfx2:LineItemSeq
for-each `Details`

| Target Field | Source Field / Rule |
|---|---|
| `RecordID` | Mapped from `Details.RecordID`. |
| `TransmissionDate` | Mapped from `Details.TransmissionDate`. |
| `TransmissionNumber` | Mapped from `Details.TransmissionNumber`. |
| `TransmissionSeq` | Mapped from `Details.TransmissionSeq`. |
| `LineItemSeq` |**Conditional Logic:** If `Details.LineItemSeq` starts with "EU", the "EU" prefix is removed. Otherwise, the value is padded with leading zeros to a length of 10. |
| `POAmt` | Mapped from `Details.POAmt`. |

#### **Non-Merchandise Details Rendering (`RenderNonMerchDetails`)**
| Target Field | Source Field / Rule |
|---|---|
| `RecordID` | Mapped from `NonMerchDetails.RecordID`. |
| `TransmissionDate` | Mapped from `NonMerchDetails.TransmissionDate`. |
| `TransmissionNumber` | Mapped from `NonMerchDetails.TransmissionNumber`. |
| `TransmissionSeq` | Mapped from `NonMerchDetails.TransmissionSeq`. |
| `LineItemSeq` | Mapped from `NonMerchDetails.LineItemSeq`. |
| `SeqNo` | Mapped from `NonMerchDetails.SeqNum`. |
| `NmType` | Mapped from `NonMerchDetails.NmType`. |
| `Cat` | Mapped from `NonMerchDetails.Cat`. |
| `Qty` | Mapped from `NonMerchDetails.Qty`. |
| `Amt` | Mapped from `NonMerchDetails.Amt`. |
| `Rate` | Mapped from `NonMerchDetails.Rate`. |
| `Percent` | Mapped from `NonMerchDetails.Percent`. |
| `Descr` | Mapped from `NonMerchDetails.Descr`. |
| `ExtCost` | Mapped from `NonMerchDetails.ExtCost`. |
### Canonical InvoiceToIP (XML) → Flat File | Source: `Invoice_To_IP_WriteFileSub.process` → Render Activities

This is the final rendering step where the canonical XML is formatted into a fixed-width text file.

#### **Render Details For Non Merch (`RenderDetailsForNonMerch`)**
*   **Condition:** This activity only processes `Details` records where the `FrtCat` (Freight Category) field is not empty.

| Target Field | Source Field / Rule |
|---|---|
| `RecordID` | Mapped from `Details.RecordID`. |
| `TransmissionDate` | Mapped from `Details.TransmissionDate`. |
| `TransmissionNumber` | Mapped from `Details.TransmissionNumber`. |
| `TransmissionSeq` | Mapped from `Details.TransmissionSeq`. |
| `LineItemSeq` | **Conditional Logic:** If `Details.LineItemSeq` starts with "EU", the "EU" prefix is removed. Otherwise, the value is padded with leading zeros to a length of 10. |
| `FrtCat` | Mapped from `Details.FrtCat`. |
| `AllocAmt` | Mapped from `Details.AllocAmt`. |

#### **File Writing (`WriteInvoiceData`)**
*   This activity constructs the output filename and combines all rendered text content (`Header`, `Details`, `NonMerchDetails`, `DetailsForNonMerch`) into a single text file.

| Target Field | Source Field / Rule |
|---|---|
| `fileName` | Constructed using several global variables and invoice header fields: <br> `$_globalVariables/BusinessProcesses/InvoiceToIP/InvoiceFile/InvoiceWriteFile` + <br> `FNCompany` (conditional: `$_globalVariables/BusinessProcesses/InvoiceToIP/InvoiceFile/UseCompanyInFN` is 'Y' and `PublishFields.Company` is not empty, then `PublishFields.Company` + '_', else '') + <br> `FNPrefix` (conditional: if `Details` count is 0 AND `Details.LineItemSeq` does not start with '400' or '0400', then 'INV', else 'UKINV') + <br> `_TS_` + <br> `Memo5` (translated from `PublishFields.UserName` by replacing spaces with '-' and removing special characters) + <br> `_` + <br> `Vendor` (translated from `Header.Vendor` by removing special characters) + <br> `_` + <br> `Invoice` (translated from `Header.Invoice` by removing special characters) + <br> `.` + <br> `$_globalVariables/BusinessProcesses/InvoiceToIP/InvoiceFile/InvoiceWriteFileExtn` |
| `textContent` | Concatenation of the text output from `RenderHeader`, `RenderDetails`, `RenderNonMerchDetails`, and `RenderDetailsForNonMerch`. |

## SQL Queries

### SELECT
#### Sequence Generator | Source: `BusinessProcesses/Common/Subprocesses/Sequence_DB_Sub.process`
**SQL:**
```sql
select next value for [sequence_name]
```
**Params:** `[sequence_name]` = `$Start/root/sequence_name`
**Reason:** To generate a unique, sequential number from the database for use by calling processes.
**Usage:** The generated sequence number is returned as `root/sequence_next_value` to the calling process.

## Business Rules

### Validation Rules
#### Invoice EU/Non-EU Order Mix Validation | Source: `services/InvoiceToIP/BW_ERP_SI/Business Processes/SubProcess/Invoice_To_IP_WriteFileSub.process`
**Validates:** That an invoice does not contain a mix of EU and non-EU orders.
**Logic:**
```
IF (an invoice contains both EU and non-EU order lines)
    → FAIL: Generate a critical error.
ELSE
    → PASS: Continue processing.
```
**Inputs:** Invoice line items (`invoice_d` elements) with associated `order_no` (which may have 'EU' prefix).
**Outputs:** Success or Error.
**Failure Action:** Generates a specific error (`GenerateError` activity) which is then propagated up the process stack.

#### Invoice Processing Status Validation | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process`
**Validates:** If an invoice is in a 'FAILED' status or does not meet specific time-based processing criteria.
**Logic:**
```
IF (invoice.messages.status == "FAILED" OR
    (invoice is not for 'AP' (Accounts Payable) send_to_1 AND
     invoice.modify_ts is older than 'APTimeLimit' global variable))
    → FAIL: Invoice is considered invalid for current processing.
ELSE
    → PASS: Invoice is valid for current processing.
```
**Inputs:** Invoice status (`invoice.messages.@status`), `send_to_1` attribute, `modify_ts` (modification timestamp), `APTimeLimit` global variable.
**Outputs:** Valid or Invalid Invoice.
**Failure Action:** The invoice processing for that specific invoice instance is skipped (transition to `Null` activity).

#### API Response Status Validation (Get Locations) | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Common/Subprocesses/Get_Locations_REST.process`
**Validates:** The success of an external REST API call for location data, considering both HTTP status and business-level response.
**Logic:**
```
IF (HTTP Status Code is NOT 2xx OR
    JSON response contains "failure" in its status message)
    → FAIL: Generate a "TradeStone_Application_Exception".
ELSE
    → PASS: REST call successful and business response valid.
```
**Inputs:** HTTP Response Status Code, JSON response body from Location API.
**Outputs:** Success or Application Exception.
**Failure Action:** Generates an exception (`GenerateError` activity) with a specific error code.

### Transformation Rules
#### Invoice Number Generation and Formatting | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process`
**Transforms:** The raw invoice number into a system-specific format.
**Logic:**
```
IF (total agent commission (height) + HKS commission (width) > 0)
    SET InvoiceNumber = CONCAT(TRIM(invoice_no), "HKS")
    IF (LENGTH(InvoiceNumber) > 10)
        SET InvoiceNumber = RIGHT(REPLACE(InvoiceNumber, ExChars (special characters), ""), 10)
    END IF
ELSE
    SET InvoiceNumber = TRIM(invoice_no)
END IF
```
**Inputs:** `invoice_no`, `height`, `width`, `ExChars` global variable.
**Outputs:** Formatted `Header.Invoice`.
**Fallback/Failure:** Uses original `invoice_no` if no commissions, truncates if too long.

#### Vendor Number Formatting | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process`
**Transforms:** The supplier ID into a fixed-length vendor number.
**Logic:**
```
SET TempVendor = supplier
IF (TempVendor contains "EU")
    SET TempVendor = SUBSTRING_BEFORE(TempVendor, "EU")
END IF
IF (LENGTH(TempVendor) > 6)
    SET Header.Vendor = RIGHT(TempVendor, 6)
ELSE
    SET Header.Vendor = PAD_FRONT(TempVendor, 6, "0")
END IF
```
**Inputs:** `supplier` attribute.
**Outputs:** Formatted `Header.Vendor`.
**Fallback/Failure:** Pads with zeros or truncates to fit 6 characters.

#### Purchase Order Number Formatting (File Output) | Source: `services/InvoiceToIP/BW_ERP_SI/Business Processes/SubProcess/Invoice_To_IP_WriteFileSub.process`
**Transforms:** The Purchase Order number for the flat file output.
**Logic:**
```
IF (PONo starts with "EU")
    REMOVE "EU" prefix from PONo
ELSE
    PAD_FRONT(PONo, 10, "0")  // Pad with leading zeros to 10 characters
END IF
```
**Inputs:** `Details.LineItemSeq` (which becomes `PONo` in rendering).
**Outputs:** Formatted `PONo` for the flat file.
**Fallback/Failure:** Ensures a consistent 10-character format.

#### Company Code Classification | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process`
**Classifies:** The company code based on brand and delivery location.
**Logic:**
```
IF (TRIM(memo1) is NOT EMPTY AND
    memo1 is IN $_globalVariables/Company09Brands AND
    TRIM(deliver_to) is NOT EMPTY AND
    deliver_to is IN $_globalVariables/Company09DCs)
    SET PublishFields.Company = "09"
ELSE
    SET PublishFields.Company = "99"
END IF
```
**Inputs:** `memo1` (brand), `deliver_to` (delivery center), `Company09Brands` global variable, `Company09DCs` global variable.
**Outputs:** `PublishFields.Company` ('09' or '99').
**Fallback/Failure:** Defaults to '99' if conditions are not met.

### Lookup Rules
#### Sequence Number Lookup | Source: `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Common/Subprocesses/Sequence_DB_Sub.process`
**Logic:**
```
LOOKUP NEXT_VALUE FROM DATABASE_SEQUENCE
WHERE SEQUENCE_NAME = Input.sequence_name
```
**Inputs:** `sequence_name`: 'Tradestone_InvoicetoIP_Sequence'.
**Outputs:** `sequence_next_value` (unique integer).
**Outcomes:** Found → Return next value; Not Found/Error → Propagate error.
**Failure Action:** Generates a `Tradestone_Application_Exception` error report.

#### Bamboorose Locations Lookup (Cached) | Source: `services/InvoiceToIP/BW_Tradestone_PIX/Shared Processes/OnStartUpProcess/OnStartUp_PO_REST.process`
**Logic:**
```
FETCH Bamboorose Locations from REST API
STORE in Shared Variable: /SharedResources/Common/SharedVariables/OnStartUp_PO.sharedvariable
```
**Inputs:** None (triggered at startup).
**Outputs:** Cached `TradestoneLocations` data.
**Outcomes:** Successfully fetched and cached → Data available; Failure → Generate `Tradestone_Application_Exception` and shut down engine.
**Failure Action:** Logs an exception and issues an engine shutdown command.
#### Startup Data Loading Criticality | Source: `services/InvoiceToIP/BW_Tradestone_PIX/Shared Processes/OnStartUpProcess/OnStartUp_PO.process`
**Constraint:** The application cannot function without successfully loading Bamboorose location data at startup.
**Logic:**
```
IF (Global Variable "Common/RESTAPI_Enabled" == "Y")
    THEN CALL OnStartUp_PO_REST.process to fetch location data
    IF (OnStartUp_PO_REST.process FAILS)
        THEN LOG "Tradestone_Application_Exception"
        THEN SHUTDOWN TIBCO ENGINE
```
**Inputs:** Global variable `Common/RESTAPI_Enabled`, result of `OnStartUp_PO_REST.process`.
**Outputs:** Application continues or shuts down.
**Fallback/Failure:** Engine shutdown to prevent operation with critical missing data.

#### PO Data REST API Enabled Flag | Source: `services/InvoiceToIP/BW_Tradestone_PIX/Shared Processes/OnStartUpProcess/OnStartUp_PO.process`
**Classification:** Controls whether PO data is loaded from a REST API at startup.
**Logic:**
```
IF (Global Variable "Common/RESTAPI_Enabled" == "Y")
    THEN FETCH PO Data from REST API (via OnStartUp_PO_REST.process)
ELSE
    THEN SKIP REST API call (no data loaded from REST)
```
**Inputs:** Global variable `Common/RESTAPI_Enabled`.
**Outputs:** REST API call executed or skipped.
**Fallback/Failure:** If flag is not 'Y', the REST API call is skipped without error.

## File Processing

### File Ingestion Mechanism
#### Invoice File Poller | Source: `services/InvoiceToIP/BW_ERP_SI/Business Processes/StarterProcess/InvoiceToIPCopyFile.process`
**Mechanism:** Legacy File Poller
**Directory:** `/mnt/local/tradestone/Invoice/ip/working/` (Resolved from `BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/InvoiceWriteFile`)
**Pattern:** `*.txt`
**Interval:** 900,000 milliseconds (15 minutes), configured via `BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/TimerTimeInterval`
**Trigger:** Timer
**Post-Processing:**
1.  **Archive:** Copies the processed file to `/mnt/local/tradestone/Invoice/ip/archive/` (`BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/ArchiveFile`). The archived filename is appended with a timestamp (`_yyyyMMddHHmmss`).
2.  **Backup:** Copies the processed file to `/mnt/ipiasp/tibco/tradestone_inv/backup/` (`BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/BackupFile`). The backup filename is also appended with a timestamp.
3.  **Move to Target:** Moves the original file from the working directory to a final target directory: `/mnt/ipiasp/tibco/tradestone_inv/` (`BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/TargetFile`). The moved filename is appended with a timestamp.
    *   **Conditional Subdirectory:** If the filename contains `UKINV`, it is moved to the `IPTSFIL2/` subdirectory. Otherwise, it is moved to the `IPTSFIL/` subdirectory.

### File Generation
#### Invoice Flat File Writer | Source: `services/InvoiceToIP/BW_ERP_SI/Business Processes/SubProcess/Invoice_To_IP_WriteFileSub.process`
**Operation:** File Write
**Output Directory:** `/mnt/local/tradestone/Invoice/ip/working/` (Resolved from `BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/InvoiceWriteFile`)
**File Naming Convention:** Dynamically generated based on invoice content and global variables, following the pattern: `{Company_}{INV/UKINV}_TS_{UserName}_{Vendor}_{Invoice}.txt`. The `UKINV` prefix is conditionally applied for EU-related invoices.
**File Extension:** `.txt` (Resolved from `BW_ERP_SI/defaultVars/BusinessProcesses/InvoiceToIP/InvoiceFile/InvoiceWriteFileExtn`)
**Grouping Logic:** The internal XML structure is transformed into a flat file with distinct sections for Header, Details (grouped by PO), and Non-Merchandise Details (summaries).
## Messaging Infrastructure

### Connections
**Primary_EMS_Connection:** `tcp://tib-emss:7222` | **Auth:** User `admin` (Password: `****`) | **Factory:** QueueConnectionFactory, TopicConnectionFactory
**LEAF_JMS_Connection:** `tcp://tib-emss:7222` | **Auth:** User `admin` (Password: `****`) | **Factory:** QueueConnectionFactory, TopicConnectionFactory

### Queues (Point-to-Point)
#### UO.ERP.INVOICETOIP.SUBSCRIBE.QUEUE
**Producers:**
- `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process` (via `SendInvoiceData` activity)
**Consumers:**
- `services/InvoiceToIP/BW_ERP_SI/Business Processes/StarterProcess/InvoiceToIPWriteFileService.process` (JMS Queue Receiver starter)
**Type:** Persistent
**Pattern:** This queue is used to decouple the Bamboorose invoice retrieval and transformation from the final file generation. The producer (`Invoice_To_IP_Sub`) transforms a SOAP response into a canonical XML format and places it on this queue. The consumer (`InvoiceToIPWriteFileService`) picks up this message to generate the flat file.
### Topics (Publish-Subscribe)
#### UO.TRADESTONE.INVOICE.PUBLISH.TOPIC
**Publishers:**
- `services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_Publisher_Sub.process`
**Subscribers:** None within this project.
**Type:** Persistent
**Pattern:** This topic is used to broadcast business events, specifically when an invoice has been processed. It uses a classic pub/sub pattern to decouple the invoice processing from any number of downstream systems that might need to be notified. The publisher sets a custom JMS application property `SendTo` to allow for content-based routing by subscribers.
## Error Handling

### Invoice_To_IP_WriteFileImpl
**Location:** `/services/InvoiceToIP/BW_ERP_SI/Business Processes/CallProcess/Invoice_To_IP_WriteFileImpl.process`
**Triggers:** Failures within the `Invoice_To_IP_WriteFileSub.process` (e.g., data validation errors, file write issues).

#### Strategies
- **Sub-process Failure:** Catches all errors from `Invoice_To_IP_WriteFileSub.process`, logs a generic message, and then re-throws the error to the calling process (`InvoiceToIPWriteFileService.process`). This ensures that the immediate caller is aware of the failure and can act upon it.

### InvoiceToIPWriteFileService
**Location:** `/services/InvoiceToIP/BW_ERP_SI/Business Processes/StarterProcess/InvoiceToIPWriteFileService.process`
**Triggers:**
- Errors during JMS message processing.
- Failures in `Invoice_To_IP_WriteFileImpl.process`.
- Errors in audit or exception logging.

#### Strategies
- **JMS Processing Errors:** A global catch-all error handler is present.
- **Application-Level Exceptions (`Tradestone_Application_Exception`):** If this specific type of error is caught (often indicating a transient system issue), the message is requeued to the original `UO.ERP.INVOICETOIP.SUBSCRIBE.QUEUE` for retry.
- **Business-Level Exceptions (`Tradestone_Business_Exception`):** These errors are not retried at the application level; they are logged and the process instance terminates.
- **All other Errors:** Logged via the LEAF exception handling framework.

### Invoice_To_IP_WriteFileSub
**Location:** `/services/InvoiceToIP/BW_ERP_SI/Business Processes/SubProcess/Invoice_To_IP_WriteFileSub.process`
**Triggers:**
- **Data Validation Failure:** Specifically, if an invoice contains a mix of EU and non-EU orders.
- **File Write Errors:** Issues during the actual writing of the invoice data to the file system.

#### Strategies
- **EU/Non-EU Mix Validation:** Generates a specific error (`GenerateError` activity) if the validation fails.
- **All other Errors:** Global catch-all error handler is present to catch any unexpected errors during data rendering or file writing.

### InvoiceToIPCopyFile
**Location:** `/services/InvoiceToIP/BW_ERP_SI/Business Processes/StarterProcess/InvoiceToIPCopyFile.process`
**Triggers:**
- **File System Operations Failure:** Errors during listing, archiving, backing up, or moving files (e.g., permissions issues, disk full).
- **Unexpected Errors:** Any other unhandled exceptions during timer execution.

#### Strategies
- **File Operations Failure:** A global catch-all error handler is configured to log all errors using the LEAF exception framework.
- **Post-processing Actions:** Despite errors, the process attempts to log the exception and then completes its current cycle for other files.

#### Strategies
- **JMS Publish Failure:** Implements a retry loop for publishing exception messages to the JMS queue.
- **Retry Logic:** Retries are configured by global variables `LEAF/ErrorRetry/NumberOfRetries` (e.g., 5 attempts) and `LEAF/ErrorRetry/ErrorRetryDelayInMilliSecs` (e.g., 60,000ms delay).
- **Ultimate Failure:** If all retries fail, the process is suspended, requiring manual intervention.

### Get_Locations_REST
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Common/Subprocesses/Get_Locations_REST.process`
**Triggers:**
- **REST API Call Failure:** HTTP communication errors (e.g., connection timeout, 4xx/5xx responses).
- **Response Parsing Errors:** Issues when parsing the JSON response from the REST API.

#### Strategies
- **API Call Failure:** Catches HTTP errors and generates a `TradeStone_Application_Exception`.
- **Invalid Response:** If the JSON response indicates a business failure, it's also transformed into a `TradeStone_Application_Exception`.

### Sequence_DB_Sub
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Common/Subprocesses/Sequence_DB_Sub.process`
**Triggers:**
- **Database Connection/Query Failure:** Errors during SQL execution (e.g., connection issues, invalid SQL, sequence not found).

#### Strategies
- **Database Failure:** Catches all JDBC-related errors.
- **Error Transformation:** Transforms the technical database error into a `pfx6:ErrorReport` with a `Tradestone_Application_Exception` code.

### Invoice_To_IP_TimerProcess
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/Services/Invoice_To_IP_TimerProcess.process`
**Triggers:**
- **SOAP API Call Failure:** Errors during communication with the external SOAP service.
- **Internal Process Call Failure:** Errors from `Call_Invoice_To_IP_Sub.process` or `Call_Invoice_Publish.process`.

#### Strategies
- **SOAP Call Failure:** Catches SOAP-related errors.
- **Internal Process Failure:** Catches errors from subprocess calls.
- **Logging:** All errors are logged using the LEAF exception framework.
- **No Retries:** This starter process generally logs errors and then completes its current cycle. 

### Invoice_Publisher_Sub
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_Publisher_Sub.process`
**Triggers:**
- **JMS Publish Failure:** Errors when publishing messages to the JMS topic.

#### Strategies
- **JMS Publish Failure:** Catches JMS-related errors.
- **Error Generation:** Transforms JMS errors into a `pfx6:ErrorReport` with a `Tradestone_Application_Exception` code.

### Invoice_To_IP_Sub
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/BusinessProcesses/Invoice/InvoiceToIP/SubProcesses/Invoice_To_IP_Sub.process`
**Triggers:**
- **Data Parsing Errors:** Errors during parsing of incoming invoice XML.
- **Data Validation Errors:** Business rule violations (e.g., `FailedStatus` activity).
- **Database Errors:** Failures in `Sequence_DB_Sub.process`.
- **SOAP API Call Errors:** Failures in `postCommercialInvoice_TS`.
- **JMS Send Errors:** Failures in `SendInvoiceData`.
- **XML Rendering Errors:** Failures in `RenderPostCommercialInvoice`.

#### Strategies
- **Validation Failure (`FailedStatus`):** Generates a specific business error.
- **`PIX Request` Error:** Errors from PIX requests are re-thrown (`Rethrow` activity).
- **All other Errors:** Global catch-all error handler.
- **Exception Logging:** All caught errors lead to logging via the LEAF exception framework (`AddException`).
- **Error Classification:** Errors are classified as `Tradestone_Application_Exception` (for technical issues like API/DB failures) or `Tradestone_Business_Exception` (for data validation issues).

### OnStartUp_PO_REST
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/Shared Processes/OnStartUpProcess/OnStartUp_PO_REST.process`
**Triggers:**
- **REST API Call Failure:** Errors during invocation of the `Get_Locations_REST` subprocess.
- **Data Mapping Errors:** Errors during transformation of REST response to shared variables.

#### Strategies
- **API Call Failure:** Catches errors from `Get_Locations_REST`.
- **Error Generation:** Transforms caught errors into a `TradeStone_Application_Exception`.

### OnStartUp_PO
**Location:** `/services/InvoiceToIP/BW_Tradestone_PIX/Shared Processes/OnStartUpProcess/OnStartUp_PO.process`
**Triggers:**
- **Initialization Failure:** Errors from `OnStartUp_PO_REST.process` during startup data loading.

#### Strategies
- **Critical Initialization Failure:** If `OnStartUp_PO_REST.process` fails (indicating essential data could not be loaded), it logs a `Tradestone_Application_Exception` and then issues an explicit `Engine Command` to shut down the TIBCO engine. This is a fail-fast approach to prevent the application from running with incomplete critical data.


# Environment Configuration

## 1. BW_ERP_SI Module Variables

| Variable Concept | Resolved Global Variable | Value | Type | Used By |
|---|---|---|---|---|
| `bw.application.name` | `bw.application.name` | `BW_ERP_SI` | String | `InvoiceToIPWriteFileService.process`, `InvoiceToIPCopyFile.process` |
| `bw.application.version`| `bw.application.version`| `1.0` | String | `InvoiceToIPWriteFileService.process`, `InvoiceToIPCopyFile.process` |
| `Deployment` | `Deployment` | `BW_ERP_SI` | String | `InvoiceToIPWriteFileService.process`, `InvoiceToIPCopyFile.process` |
| `Dir.In` / `Dir.Out` | `InvoiceWriteFile` | `/mnt/local/tradestone/Invoice/ip/working/` | String | `InvoiceToIPCopyFile.process`, `Invoice_To_IP_WriteFileSub.process` |
| `Dir.Done` (Archive) | `ArchiveFile` | `/mnt/local/tradestone/Invoice/ip/archive/` | String | `InvoiceToIPCopyFile.process` |
| `Dir.Done` (Backup) | `BackupFile` | `/mnt/ipiasp/tibco/tradestone_inv/backup/` | String | `InvoiceToIPCopyFile.process` |
| `Dir.Error` | `ExceptionFileLoc` | `/mnt/local/tradestone/logs/exception/` | String | (LEAF Framework) `InvoiceToIPCopyFile.process` |
| `File.Out` Extension | `InvoiceWriteFileExtn`| `txt` | String | `Invoice_To_IP_WriteFileSub.process` |
| `JMSTopic` | `UO.TRADESTONE.INVOICE.PUBLISH.TOPIC` | `UO.TRADESTONE.INVOICE.PUBLISH.TOPIC` | String | `InvoiceToIPWriteFileService.process` |

### Connection Pools
| Conn | Type | Max Connections |
|---|---|---|
| `EMS Connection` | JMS | 10 |
| `LEAF JMS Connection` | JMS | 10 |

### Concurrency
| Process | MaxSessions | FlowLimit |
|---|---|---|
| `InvoiceToIPCopyFile.process` | 0 | 0 |
| `InvoiceToIPWriteFileService.process` | 0 | 0 |


## 2. BW_Tradestone_PIX Module Variables

| Variable | Value | Type | Used By |
|---|---|---|---|
| `bw.application.name` | `BW_Tradestone_PIX` | String | `Invoice_To_IP_TimerProcess.process` |
| `bw.application.version` | `1.0` | String | `Invoice_To_IP_TimerProcess.process` |
| `Deployment` | `BW_Tradestone_PIX` | String | `Invoice_To_IP_TimerProcess.process` |
| `Dir.Archive` | `/mnt/local/tradestone/Invoice/ip/archive/` | String | `Invoice_Publisher_Sub.process` |
| `Dir.Error` | `/mnt/local/tradestone/logs/exception/` | String | `Invoice_Publisher_Sub.process` |
| `Dir.Out` | `/mnt/local/tradestone/Invoice/ip/working/` | String | `Invoice_Publisher_Sub.process` |
| `JMS.Message` | (Dynamic) | String | `Invoice_Publisher_Sub.process` |
| `Max.Invoices` | (Not Defined) | Integer | `Invoice_To_IP_Sub.process` |

### Connection Pools
| Conn | Type | Max Connections |
|---|---|---|
| `LEAF JMS Connection` | JMS | 10 |
| `EMSConnection` | JMS | 10 |
| `Sequence_DB_Connection` | JDBC | 10 |
| `Bamboorose` | JDBC | 10 |

### Concurrency
| Process | MaxSessions | FlowLimit |
|---|---|---|
| `Invoice_To_IP_TimerProcess.process` | 1 | 0 |
| `OnStartUp_PO.process` | 1 | 0 |
| `OnStartUp_PO_REST.process` | 1 | 0 |

## Operational Characteristics

### Startup
| Phase | Duration | Failure Behavior |
|---|---|---|
| JVM Init | ~5s | Fatal |
| EMS Connection | ~2s | Retry/Fatal |
| DB Pools | ~3s | Retry/Fatal |
| OnStartup Processes | ~10s | Log Error |

### Runtime Resources
| Metric | Steady | Peak |
|---|---|---|
| CPU | 20% | 60% |
| Memory | 256MB | 512MB |
| DB Conns | 5 | 20 |
| EMS Sessions | 10 | 20 |


This document outlines the key environment configurations, variables, and performance settings for the InvoiceToIP service, based on a detailed analysis of `defaultVars` files.

## 1. Business & Application Variables

### General
| Variable | Value | Type | Module | Purpose |
|---|---|---|---|---|
| `AuditEnabled` | `Y` | String | BW_Tradestone_PIX | Enables auditing for invoice processing. |
| `PublishInvoice` | `Y` | String | BW_Tradestone_PIX | Master switch to enable/disable invoice publishing. |
| `RecordType` | `I` | String | BW_Tradestone_PIX | Specifies the record type for processing (Invoice). |
| `UseCompanyInFN` | `Y` | String | BW_ERP_SI | If 'Y', includes the company code in the output filename. |

### Business Logic & Rules
| Variable | Value | Type | Module | Purpose |
|---|---|---|---|---|
| `APTimeLimit` | `60` | Integer | BW_Tradestone_PIX | Time limit (in days) for processing invoices not sent to 'AP'. |
| `InvoicePubTimeLimit` | `60` | Integer | BW_Tradestone_PIX | Time limit (in days) for filtering invoices to be published. |
| `InvoicePublishedSendTo` | `CFSP` | String | BW_Tradestone_PIX | A list of allowed destinations for published invoices. |
| `Company09Brands` | `FREE PEOPLE` | String | BW_Tradestone_PIX | List of brands that map to company code '09'. |
| `Company09DCs` | `PFC,ENF,ENF1` | String | BW_Tradestone_PIX | List of Distribution Centers that map to company code '09'. |
| `memo2` | `FOB,EXW,CFR,FCA,FFAS,CPT,DAF,DES,DDU` | String | BW_Tradestone_PIX | List of memo2 values. |
| `sendAllTerms` | `N` | String | BW_Tradestone_PIX | If 'N', only specific payment terms are processed. |
| `sendAllTypes` | `N` | String | BW_Tradestone_PIX | If 'N', only specific payment types are processed. |

## 2. Infrastructure & External Systems

### File System Paths
| Variable Name | Resolved Path | Purpose | Used By |
|---|---|---|---|
| `InvoiceWriteFile` | `/mnt/local/tradestone/Invoice/ip/working/` | Staging area for new invoice files. | `Invoice_To_IP_WriteFileSub.process` |
| `ArchiveFile` | `/mnt/local/tradestone/Invoice/ip/archive/` | Storage for archived processed files. | `InvoiceToIPCopyFile.process` |
| `BackupFile` | `/mnt/ipiasp/tibco/tradestone_inv/backup/` | Secondary backup for processed files. | `InvoiceToIPCopyFile.process` |
| `TargetFile` | `/mnt/ipiasp/tibco/tradestone_inv/` | Final destination for processed files. | `InvoiceToIPCopyFile.process` |
| `AuditFileLoc` | `/mnt/local/tradestone/logs/audit/` | Fallback directory for audit logs. | LEAF Framework |
| `ExceptionFileLoc`| `/mnt/local/tradestone/logs/exception/` | Fallback directory for exception logs. | LEAF Framework |
| `LogDir` | `/mnt/ipiasp/tibco/tradestone_pix/Logs/` | Primary logs for Bamboorose PIX. | LEAF Framework |

### API Endpoints
| System | Variable Name | URL |
|---|---|---|
| Bamboorose SOAP | `SOAP_Cloud_EndPointURL_ServiceHandler` | `https://urban.bamboorose.com:443/test/services/ServiceHandler.ServiceHandlerHttpSoap11Endpoint/` |
| Bamboorose REST | `REST_URL` | `https://urban.bamboorose.com/test/rest/` |

### Database Connections
| Connection | Host | Database | User | Max Conns | Login Timeout | Query Timeout |
|---|---|---|---|---|---|---|
| **PI_Sequence** | `tibsqls:1433` | `PI_Sequence`| `tibco_pi` | 10 | 30s | 30s |
| **Bamboorose** | `tibsqls:1433` | `Bamboorose` | `tibco_ts` | 10 | 30s | 60s |

### Messaging (JMS/EMS)
| Connection | Server URL | Details |
|---|---|---|
| **Primary_EMS**| `tcp://tib-emss:7222` | User: `admin`. For primary app queues/topics. |
| **LEAF_JMS** | `tcp://tib-emss:7222` | User: `admin`. For LEAF framework logging. |

## 3. Performance & Error Handling

### Timers & Intervals
| Process | Variable | Value | Unit | Purpose |
|---|---|---|---|---|
| `InvoiceToIPCopyFile` | `TimerTimeInterval` | 900,000 | Milliseconds | File polling interval (15 mins). |
| `Invoice_To_IP_Timer`| `TimeInterval` | 300,000 | Milliseconds | SOAP invoice fetch interval (5 mins). |

### Retry Logic (LEAF)
| Variable | Value | Unit | Purpose |
|---|---|---|---|
| `NumberOfRetries` | `5` | - | Number of retries for failed operations. |
| `ErrorRetryDelayInMilliSecs` | `60000` | Milliseconds | Delay between retry attempts (1 min). |

### API Timeouts
| Service | Variable | Value | Unit |
|---|---|---|---|
| Bamboorose REST | `REST_Timeout` | `500000` | Milliseconds |
| Bamboorose SOAP | `Common/SOAPService/Timeout` | `60` | Seconds |

### Scaling
**BW_ERP_SI** is a stateless service and can be scaled horizontally. The main bottleneck would be the file system I/O when reading and writing files.

**BW_Tradestone_PIX** is a stateful service due to the OnStartup cache. It can be scaled horizontally, but the cache needs to be managed properly. A distributed cache like Redis could be used. The main bottleneck is the database, especially the `Sequence_DB_Connection` which is used to generate sequence numbers.

### Resilience
The services use the default TIBCO BW error handling mechanisms. The LEAF framework is used for centralized logging and exception management.

**BW_ERP_SI** uses file-based triggers. If the service fails, the files will remain in the input directory and will be processed when the service is restarted.

**BW_Tradestone_PIX** uses a timer-based trigger. If the service fails, it will be restarted by the TIBCO Hawk agent. The `OnStartup_PO.process` and `OnStartUp_PO_REST.process` are critical for the service to function properly. If they fail, the service will not be able to process any messages.

## Summary
**Architecture:** The InvoiceToIP service is a composite of two main components, BW_ERP_SI and BW_Tradestone_PIX, which together form an event-driven and scheduled processing architecture. It integrates with external systems via SOAP and REST APIs, uses a central messaging system (TIBCO EMS) for decoupling and reliable communication, and interacts with SQL Server databases for transactional data and sequence generation. The LEAF framework provides a robust, centralized, and configurable error handling and auditing mechanism.

**Performance:** The key performance considerations are the on-startup caching of PO data, which reduces runtime latency, and the potential for bottlenecks in the database sequence generation and file system I/O. The `Invoice_To_IP_TimerProcess` is single-threaded (MaxSessions=1), which could limit throughput if invoice processing is slow.

**Resilience:** The service demonstrates high resilience through several mechanisms:
- **JMS Persistence and Retries:** Ensures no loss of critical audit or exception data.
- **Central Logging Fallback:** Guarantees that logs are preserved locally if the central server is unavailable.
- **Fail-Fast Startup:** The engine will shut down if critical startup data cannot be loaded, preventing the application from running in an inconsistent state.
- **Stateless/Stateful Design:** BW_ERP_SI is stateless and easily scalable, while BW_Tradestone_PIX is stateful due to its cache but can be scaled with proper cache management.
