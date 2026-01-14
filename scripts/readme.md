# Scripts

| Script                               | Description                                                                                     |
|--------------------------------------|-------------------------------------------------------------------------------------------------|
| `cloud_run_auth_test.py`<sup>1</sup> | Validate that our Google Cloud Run credentials are working as expected.                         |
| `kafka_auth_test.py`                 | Validate that our Kafka credentials are working as expected.                                    |
| `local-docker-build.sh`<sup>1</sup>  | Build the Docker image locally. From the project root:<br />`$ ./scripts/local-docker-build.sh` |

<sup>**[1]**</sup> Both of these scripts rely on Google Application Default
Credentials ([ADC](https://cloud.google.com/docs/authentication/application-default-credentials)). It is assumed the
reader understands ADC thoroughly.

## Kafka Environment Variables

Set these environment variables to run the Kafka scripts. We suggest using a `./configs/local.env` file to store these
values.

| Variable Name         | Description                                                     |
|-----------------------|-----------------------------------------------------------------|
| `CRED_TEST_TOPIC`     | The Kafka topic used for testing.                               |
| `CRED_BROKER_URL`     | The URL of the Kafka broker (relevant to `tcp` implementation). |
| `CRED_USERNAME`       | The username for Kafka authentication.                          |
| `CRED_PASSWORD`       | The password for Kafka authentication.                          |
| `CRED_CONSUMER_GROUP` | The Kafka consumer group ID.                                    |
| `CRED_REST_ENDPOINT`  | The REST endpoint for the Kafka REST proxy.                     |
