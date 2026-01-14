# Execution Plan: invoice-ingestor

## 1. Overview
This document outlines the execution plan for developing the `invoice-ingestor` microservice. The service's primary responsibility is to poll the external Bamboorose SOAP API on a schedule, fetch commercial invoices, and publish each invoice as a raw XML message to a Kafka topic. The plan is organized into sequential Dependency Layers, where work in a higher-numbered layer depends on the completion of work in a lower-numbered layer. This structure ensures a logical and efficient development flow, from project foundation to production-ready observability.

## 2. Feature Groups & Story Mapping

| Feature Group | Story ID | Summary |
| :--- | :--- | :--- |
| **1. Foundation & Configuration** | II-2 | Project Scaffolding and Dependency Setup |
| | II-3 | Implement Configuration Management with x35-settings |
| **2. Core Application Logic** | II-4 | Implement Main Application Logic and Scheduled Entrypoint |
| **3. Bamboorose API Integration** | II-5 | Implement SOAP Client for Bamboorose API (Happy Path) |
| | II-6 | Add Resilience Patterns to the SOAP Client |
| **4. Data Processing** | II-7 | Implement XML Response Parsing Logic |
| **5. Kafka Integration** | II-8 | Implement Kafka Producer Client Setup |
| | II-9 | Implement Invoice Publishing Logic to Kafka |
| **6. Observability** | II-10 | Implement Structured JSON Logging |
| | II-11 | Implement Prometheus Metrics Endpoint |
| | II-12 | Implement Distributed Tracing |

## 3. Dependency Layers

| Layer | Title | Feature Groups | Parallel Candidates |
| :--- | :--- | :--- | :--- |
| *LAYER 0* | *Foundation & Configuration* | Foundation & Configuration | None |
| *LAYER 1* | *Core Application & Client Setup* | Core Application Logic, Bamboorose API Integration, Kafka Integration | Step-3, Step-4, Step-5 |
| *LAYER 2* | *Business Logic & Resilience* | Bamboorose API Integration, Data Processing | Step-6, Step-7 |
| *LAYER 3* | *End-to-End Data Flow* | Kafka Integration | None |
| *LAYER 4* | *Observability* | Observability | Step-9, Step-10 |

---

## 4. Sequential Execution Steps

### LAYER 0: Foundation & Configuration

---

#### Step-1: Project Scaffolding and Dependency Setup
- **Objective:** Create the standard x35 service project structure and define all necessary dependencies in `pyproject.toml`.
- **Story IDs:** `II-2`
- **Status:** ✅ **Done**
- **Feature Group:** `Foundation & Configuration`
- **Dependency Layer:** `0`
- **Unit Testing:** N/A
- **Dependencies:**
    - **Depends On:** None
    - **Blocks:** Step-2
    - **Parallel Candidates:** None

---

#### Step-2: Implement Configuration Management
- **Objective:** Create a Pydantic settings class using `x35-settings` to load and validate all required environment variables.
- **Story IDs:** `II-3`
- **Status:** ✅ **Done**
- **Feature Group:** `Foundation & Configuration`
- **Dependency Layer:** `0`
- **Unit Testing:** Verify that the Pydantic model correctly validates valid, invalid, and missing environment variables.
- **Dependencies:**
    - **Depends On:** Step-1
    - **Blocks:** Step-3, Step-4, Step-5
    - **Parallel Candidates:** None

---

### LAYER 1: Core Application & Client Setup

---

#### Step-3: Implement Main Application Logic
- **Objective:** Develop the main application entrypoint and high-level process flow using `x35-fastapi` to orchestrate the sequence of operations (fetch, parse, publish).
- **Story IDs:** `II-4`
- **Status:** ✅ **Done**
- **Feature Group:** `Core Application Logic`
- **Dependency Layer:** `1`
- **Unit Testing:** Use mocks to test the orchestration logic and verify the correct sequence of calls to the client, parser, and publisher.
- **Dependencies:**
    - **Depends On:** Step-2
    - **Blocks:** Step-7, Step-9, Step-10
    - **Parallel Candidates:** Step-4, Step-5

---

#### Step-4: Implement SOAP Client for Bamboorose API (Happy Path)
- **Objective:** Create an asynchronous `httpx` client to construct the SOAP request, handle basic authentication, and fetch invoice data from the Bamboorose API.
- **Story IDs:** `II-5`
- **Status:** ✅ **Done**
- **Feature Group:** `Bamboorose API Integration`
- **Dependency Layer:** `1`
- **Unit Testing:** Test the construction of the SOAP request body. Mock the `httpx` client to verify successful response handling.
- **Dependencies:**
    - **Depends On:** Step-2
    - **Blocks:** Step-6
    - **Parallel Candidates:** Step-3, Step-5

---

#### Step-5: Implement Kafka Producer Client Setup
- **Objective:** Configure and initialize the Kafka producer using `urbn-confluent-methods` during the application's startup sequence.
- **Story IDs:** `II-8`
- **Status:** ✅ **Done**
- **Feature Group:** `Kafka Integration`
- **Dependency Layer:** `1`
- **Unit Testing:** Test the producer initialization logic with mocked configurations to ensure it handles correct and incorrect settings.
- **Dependencies:**
    - **Depends On:** Step-2
    - **Blocks:** Step-8
    - **Parallel Candidates:** Step-3, Step-4

---

### LAYER 2: Business Logic & Resilience

---

#### Step-6: Add Resilience Patterns to the SOAP Client
- **Objective:** Enhance the SOAP client with retry logic using the `backoff` library and implement request timeouts to handle transient API failures gracefully.
- **Story IDs:** `II-6`
- **Status:** ✅ **Done**
- **Feature Group:** `Bamboorose API Integration`
- **Dependency Layer:** `2`
- **Unit Testing:** Mock the `httpx` client to simulate 5xx errors, connection errors, and timeouts to confirm that the retry logic is triggered as expected. Test that 4xx errors do not trigger retries.
- **Dependencies:**
    - **Depends On:** Step-4
    - **Blocks:** None
    - **Parallel Candidates:** Step-7

---

#### Step-7: Implement XML Response Parsing Logic
- **Objective:** Develop the logic to parse the batch XML response from the API, extract the inner XML from the CDATA block, and iterate to produce a list of individual invoice XML strings.
- **Story IDs:** `II-7`
- **Status:** ✅ **Done**
- **Feature Group:** `Data Processing`
- **Dependency Layer:** `2`
- **Unit Testing:** Test the parsing logic with valid single and multi-invoice payloads, malformed XML, and empty responses to ensure correct output and exception handling.
- **Dependencies:**
    - **Depends On:** Step-3
    - **Blocks:** Step-8
    - **Parallel Candidates:** Step-6

---

### LAYER 3: End-to-End Data Flow

---

#### Step-8: Implement Invoice Publishing Logic to Kafka
- **Objective:** Create the logic to iterate through a list of parsed invoices, create a Kafka message for each with a `trace_id` header, and publish it to the configured topic.
- **Story IDs:** `II-9`
- **Status:** ✅ **Done**
- **Feature Group:** `Kafka Integration`
- **Dependency Layer:** `3`
- **Unit Testing:** Mock the Kafka producer to verify that the `publish` method is called with the correct topic, body, and headers for each invoice.
- **Dependencies:**
    - **Depends On:** Step-5, Step-7
    - **Blocks:** Step-11
    - **Parallel Candidates:** None

---

### LAYER 4: Observability

---

#### Step-9: Implement Structured JSON Logging
- **Objective:** Integrate `x35-json-logging` to ensure all operational events are logged in a structured JSON format, including a consistent `trace_id`.
- **Story IDs:** `II-10`
- **Status:** ✅ **Done**
- **Feature Group:** `Observability`
- **Dependency Layer:** `4`
- **Unit Testing:** Verify that key functions generate logs with the expected messages, severity levels, and `trace_id`.
- **Dependencies:**
    - **Depends On:** Step-3
    - **Blocks:** Step-11
    - **Parallel Candidates:** Step-10

---

#### Step-10: Implement Prometheus Metrics Endpoint
- **Objective:** Expose a `/metrics` endpoint and implement all specified Prometheus counters and histograms for monitoring service health and performance.
- **Story IDs:** `II-11`
- **Status:** ✅ **Done**
- **Feature Group:** `Observability`
- **Dependency Layer:** `4`
- **Unit Testing:** Verify that the metric objects are correctly incremented by the functions that are supposed to trigger them.
- **Dependencies:**
    - **Depends On:** Step-3
    - **Blocks:** None
    - **Parallel Candidates:** Step-9

---

#### Step-11: Implement Distributed Tracing
- **Objective:** Ensure a unique `trace_id` is generated for each run and consistently propagated through all logs and Kafka message headers.
- **Story IDs:** `II-12`
- **Status:** ✅ **Done**
- **Feature Group:** `Observability`
- **Dependency Layer:** `4`
- **Unit Testing:** Test that functions correctly pass the `trace_id` to sub-functions, loggers, and the Kafka producer.
- **Dependencies:**
    - **Depends On:** Step-8, Step-9
    - **Blocks:** None
    - **Parallel Candidates:** None

---