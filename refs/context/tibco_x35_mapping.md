# TIBCO BusinessWorks 5.x to x35 Mapping

This document maps legacy TIBCO BusinessWorks concepts to their modern equivalents within the x35 microservices architecture. It is designed to guide developers in migrating and building services that align with x35 standards.

---

## Core Architecture

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| Process Definition (`.process`) / BusinessWorks Process | x35 Service (Python/FastAPI) | A TIBCO process is a self-contained executable, which maps directly to a Python microservice built using the `x35-service-template`, which internally uses `(x35-fastapi)`. |
| TIBCO BW Engine | Python Runtime / Docker Container | The execution environment for a TIBCO process is replaced by a Python runtime packaged within a Docker container. |
| EAR File | Docker Image | The deployable TIBCO Enterprise Archive (EAR) file is analogous to a Docker image, which is the standard deployment artifact in x35. |

---

## Lifecycle

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| Process Starter (Event Driven, RestAPI, Timer, File Poller) | Event Triggers (Cloud Scheduler, Eventarc) | Scheduled or event-based process starters are replaced by cloud-native triggers that invoke the service. |
| `OnStartup` Process | FastAPI `lifecycle("startup")` | Initialization logic that runs when a TIBCO engine starts is implemented using FastAPI's startup event handler, often used to initialize the `lookupcache`. |

---

## Process Logic & Structure

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| Activity | Python Function/Method | An individual TIBCO activity (e.g., a mapper, a call process) corresponds to a specific function or method within a Python service. |
| Subprocess (`CallProcessActivity`) | Python Module/Function Call | A call to a reusable subprocess in TIBCO is equivalent to importing and calling a function from another Python module within the service's `src/` directory. |

---

## Communication & Messaging

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| TIBCO EMS/JMS | Confluent Kafka | The primary messaging backbone. TIBCO EMS topics and queues are replaced by Kafka topics. |
| JMS Queue Receiver (Starter) | Kafka Consumer (`urbn-confluent-methods`) | A process started by a JMS message is equivalent to a Kafka consumer service that subscribes to a topic. |
| JMS Queue Sender (Activity) | Kafka Producer (`urbn-confluent-methods`) | Sending a JMS message within a process maps to a Kafka producer publishing a message to a topic. |

---

## Integrations

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| TIBCO Palettes (General) | Python Libraries | The functionality provided by various TIBCO palettes is replaced by specific Python libraries (e.g., `httpx` for HTTP, `SQLAlchemy` for databases). |
| Database Activities (`JDBCQueryActivity`) | Database Libraries (`SQLAlchemy` via `lookupcache`) | Database interactions are performed using libraries like SQLAlchemy, often managed through the `lookupcache` library for connection pooling and caching. |
| HTTP Activities (`HttpRequestActivity`) | `httpx` | Outbound HTTP requests are made using `httpx`, the preferred asynchronous HTTP client in the x35 stack. |
| File Activities (`.adfiles`) | Cloud Storage + Eventarc | File-based triggers and processing are replaced by cloud-native solutions like Google Cloud Storage, with Eventarc notifications triggering the service. |

---

## Data Handling

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| TIBCO Mapper / XPath / XSLT | Python Data Transformation / `lxml` | Data mapping and transformation, typically done with XPath, are performed in Python, often using Pydantic for data shaping and validation. |
| XML Parser (`ParseXML` activity) | `lxml` | Parsing XML data is handled by standard Python libraries. |
| Data Format (XSD) | Pydantic Models | While the wire format (e.g., XML, JSON) may remain the same, the internal, type-safe representation of data is defined using Pydantic models. |
| Shared Variables (`.sharedvariable`) | In-memory Cache (`lookupcache`) | In-memory data caching, often loaded at startup by an `OnStartup` process, is replaced by the `lookupcache` library, which provides a standardized caching mechanism. |

---

## Configuration

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| Global Variables (`defaultVars.substvar`) [*Development Global Variable*] | Environment Variables & `x35-settings` | TIBCO's XML-based variable files are replaced by environment variables, managed and validated by the `x35-settings` library using Pydantic models. |
| TIBCO Administrator/Global Variables [*Runtime Global Variable*] | Configuration Management (GCP Secret Manager) | Centralized configuration and secret management is handled by cloud-native services like GCP Secret Manager, which injects values as environment variables. |

---

## Error Handling & Observability

| TIBCO Concept | x35 Equivalent | Description |
|---------------|----------------|-------------|
| Error Handler (`Catch` activity) | Python Exception Handling | TIBCO's explicit error transitions and catch blocks are replaced by standard Python `try...except` blocks. Custom Error Codes and Exceptions are mentioned in (`x35-errors`)|
| AutoResubmitter Queue | Dead-Letter Topic (DLT) | A dedicated queue for failed messages in TIBCO is replaced by a DLT in Kafka for handling unrecoverable system errors. |
| LEAF Library | Observability Stack (GCP Logging, New Relic) | Monitoring and alerting are handled by a modern observability stack, with structured logs provided by `x35-json-logging`. |
