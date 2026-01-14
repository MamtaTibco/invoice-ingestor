# x35 Service Template

This repository serves as the standard template for creating new x35 microservices. It provides a production-ready
foundation with GitHub Actions CI/CD, FastAPI configuration, and built-in testing capabilities for Cloud Run
authentication and Kafka connectivity (both REST and TCP).

## Creating a New Service

Replace service-specific code in `src/` with your implementation
and update the README with your service-specific documentation.

[`self-ci.yaml`](./workflows/self-ci.yaml) workflow handles automated testing, building and pushing your service image.
Unless you specify a custom `Dockerfile`,
the [x35-default.Dockerfile](https://github.com/urbn/x35-actions/blob/main/docker-build/x35-default.Dockerfile)
is used for builds.
Consult [x35-actions/docker-build](https://github.com/urbn/x35-actions/tree/main/docker-build#x35-docker-build-action)
docs for more information.

## Local Development

### Setup

1. Install
   ```bash
   # Clone your new repository
   git clone <your-new-repo>
   cd <your-new-repo>

   ./install.sh  # Install dependencies

   source venv/bin/activate  # Activate virtual environment
   ```

2. Run Tests
   ```bash
   # Run tests
   tox
   ```

3. Run Service w/Hot Reload
   ```bash
   PYTHONPATH=$(pwd) UVICORN_RELOAD=true python src/app.py
   ```

### Auth/ Connect Test Scripts

The `scripts/` directory contains tools for validating connectivity:

#### Cloud Run Authentication Test

   ```bash
   python scripts/cloud_run_auth_test.py <service-url>
   ```

#### Kafka Connectivity Test

  ```bash
python scripts/kafka_auth_test.py --mode tcp
```

```bash
python scripts/kafka_auth_test.py --mode rest
```

Required environment variables are documented in [`scripts/readme.md`](../scripts/readme.md).

### OpenAPI Documentation

FastAPI provides interactive API documentation (See also: `FASTAPI_ENABLE_DOCS`
in [Configuration](#configuration-environment-variables) section):

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

### Configuration: Environment Variables

x35 uses environment variables for configuration. This repository uses only
default values.

Either set them in your environment or create a
`configs/local.env` file.

| Variable Name                          | Description                  | Default |
|----------------------------------------|------------------------------|---------|
| `UVICORN_PORT`<sup>1</sup>             | Server port                  | 8080    |
| `UVICORN_WORKERS`                      | Number of uvicorn workers    | 1       |
| `UVICORN_ACCESS_LOG`                   | Enable access logging        | True    |
| `UVICORN_RELOAD`                       | Enable hot reload            | False   |
| `FASTAPI_ENABLE_DOCS`                  | Enable OpenAPI documentation | False   |
| `X35_LOGGING_SERVICE_NAME`<sup>2</sup> | Service name for logs        |         |
| `X35_LOGGING_LOG_LEVEL`                | Log level for application    |         |

<sup>[1]</sup> For `UVICORN_` and `FASTAPI_` settings and defaults,
consult [x35-settings](https://github.com/urbn-x35/x35-settings?tab=readme-ov-file#x35-settings)
<br /><sup>[2]</sup> For `X35_LOGGING_` settings and defaults,
consult [x35-json-logging](https://github.com/urbn/x35-json-logging/blob/main/src/x35_json_logging/x35_json_logging.py)

Additional variables for testing scripts are documented in `scripts/readme.md`.
