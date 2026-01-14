import argparse
import os
from abc import ABC, abstractmethod

import requests
from confluent_kafka import Consumer, Producer, KafkaError
from google.auth import default
from google.auth.transport.requests import Request


class KafkaClient(ABC):
    @abstractmethod
    def produce_message(self, topic: str, message: str) -> None:
        pass

    @abstractmethod
    def consume_messages(self, topic: str) -> None:
        pass


class TCPKafkaClient(KafkaClient):
    def __init__(self, conf: dict):
        # Producer setup
        producer_conf = conf.copy()
        producer_conf.update({"client.id": "python-producer", "acks": "all"})
        self.producer = Producer(producer_conf)

        # Consumer setup
        consumer_conf = conf.copy()
        consumer_conf.update(
            {
                "group.id": os.getenv("CRED_CONSUMER_GROUP"),
                "auto.offset.reset": "earliest",
            }
        )
        self.consumer = Consumer(consumer_conf)

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce_message(self, topic: str, message: str) -> None:
        self.producer.produce(
            topic, message.encode("utf-8"), callback=self.delivery_report
        )
        self.producer.flush()

    def consume_messages(self, topic: str) -> None:
        self.consumer.subscribe([topic])

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print("Reached end of partition")
                    else:
                        print(f"Error: {msg.error()}")
                else:
                    print(f"Received message: {msg.value().decode('utf-8')}")
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()


class RESTKafkaClient(KafkaClient):
    def __init__(self, rest_endpoint: str):
        self.base_url = rest_endpoint.rstrip("/")

        # Get Kafka credentials
        self.kafka_username = os.getenv("CRED_USERNAME")
        self.kafka_password = os.getenv("CRED_PASSWORD")
        if not self.kafka_username or not self.kafka_password:
            raise ValueError(
                "CRED_USERNAME and CRED_PASSWORD are required for Kafka authentication"
            )

        # Set up Google auth for Cloud Run access
        try:
            credentials, project = default()
            request = Request()
            credentials.refresh(request)
            if hasattr(credentials, "id_token"):
                self.google_token = credentials.id_token
            else:
                raise ValueError("Could not get ID token from credentials")
            print(f"Successfully obtained Google credentials for project: {project}")
        except Exception as e:
            print(f"Error setting up Google authentication: {str(e)}")
            raise

        # Base headers with Google auth
        self.headers = {
            "Content-Type": "application/vnd.kafka.json.v2+json",
            "Accept": "application/vnd.kafka.v2+json",
            "Authorization": f"Bearer {self.google_token}",
        }

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with both Google auth and Kafka credentials"""
        # Add Kafka credentials to the request
        if "json" not in kwargs:
            kwargs["json"] = {}

        # Add Kafka auth to the payload if it's a POST request creating a consumer
        if method == "POST" and "/consumers/" in url and "name" in kwargs["json"]:
            kwargs["json"].update(
                {
                    "sasl.username": self.kafka_username,
                    "sasl.password": self.kafka_password,
                    "security.protocol": "SASL_SSL",
                    "sasl.mechanisms": "PLAIN",
                }
            )

        response = requests.request(method, url, headers=self.headers, **kwargs)

        # Handle 401/403 by refreshing Google token and retrying once
        if response.status_code in (401, 403):
            print("Refreshing Google auth token and retrying...")
            self._refresh_google_token()
            self.headers["Authorization"] = f"Bearer {self.google_token}"
            response = requests.request(method, url, headers=self.headers, **kwargs)

        return response

    def _refresh_google_token(self):
        """Refresh the Google authentication token"""
        credentials, _ = default()
        request = Request()
        credentials.refresh(request)
        if hasattr(credentials, "id_token"):
            self.google_token = credentials.id_token
        else:
            raise ValueError("Could not refresh ID token")

    def produce_message(self, topic: str, message: str) -> None:
        url = f"{self.base_url}/topics/{topic}"
        payload = {"records": [{"value": message}]}

        response = self._make_request("POST", url, json=payload)
        if response.status_code == 200:
            print(f"Message successfully produced to {topic}")
        else:
            print(f"Error producing message: {response.status_code} - {response.text}")

    def consume_messages(self, topic: str) -> None:
        # Create a consumer instance with both auth mechanisms
        consumer_url = f"{self.base_url}/consumers/{os.getenv('CRED_CONSUMER_GROUP')}"
        consumer_config = {
            "name": "rest_consumer",
            "format": "json",
            "auto.offset.reset": "earliest",
            "auto.commit.enable": "false",
            "sasl.username": self.kafka_username,
            "sasl.password": self.kafka_password,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
        }

        response = self._make_request("POST", consumer_url, json=consumer_config)
        if response.status_code != 200:
            print(f"Error creating consumer: {response.status_code} - {response.text}")
            return

        consumer_instance = response.json()
        base_uri = consumer_instance["base_uri"]

        # Subscribe to the topic
        subscribe_url = f"{base_uri}/subscription"
        response = self._make_request("POST", subscribe_url, json={"topics": [topic]})

        if response.status_code != 204:
            print(
                f"Error subscribing to topic: {response.status_code} - {response.text}"
            )
            return

        # Consume messages
        consume_url = f"{base_uri}/records"
        try:
            while True:
                response = self._make_request("GET", consume_url)
                if response.status_code == 200:
                    records = response.json()
                    for record in records:
                        print(f"Received message: {record['value']}")
                else:
                    print(
                        f"Error consuming messages: {response.status_code} - {response.text}"
                    )

        except KeyboardInterrupt:
            # Delete the consumer instance
            delete_url = base_uri
            self._make_request("DELETE", delete_url)


def main():
    parser = argparse.ArgumentParser(description="Kafka Connection Tester")
    parser.add_argument(
        "--mode",
        choices=["tcp", "rest"],
        required=True,
        help="Connection mode: tcp for direct connection, rest for REST API",
    )
    args = parser.parse_args()

    topic = os.getenv("CRED_TEST_TOPIC")

    if args.mode == "tcp":
        conf = {
            "bootstrap.servers": os.getenv("CRED_BROKER_URL"),
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": os.getenv("CRED_USERNAME"),
            "sasl.password": os.getenv("CRED_PASSWORD"),
        }
        client = TCPKafkaClient(conf)
    else:  # rest mode
        rest_endpoint = os.getenv("CRED_REST_ENDPOINT")
        if not rest_endpoint:
            raise ValueError(
                "CRED_REST_ENDPOINT environment variable is required for REST mode"
            )
        client = RESTKafkaClient(rest_endpoint)

    # Test both produce and consume
    client.produce_message(topic, f"Hello Kafka! Regards, {args.mode} Client.")
    client.consume_messages(topic)


if __name__ == "__main__":
    main()
