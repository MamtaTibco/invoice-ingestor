# -*- coding: utf-8 -*-
"""FastAPI application factory."""
import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from lxml import etree
from x35_fastapi import FastAPIAppBuilder, CustomHeaderMiddleware
from x35_json_logging import initialize_logging, trace_context, dynamic_context

from src.clients.bamboorose import BambooroseClient, get_bamboorose_client
from src.clients.kafka import KafkaProducerClient, get_kafka_producer_client
from src.routes.metrics import metrics_router
from src.services.metrics import (
    bamboorose_api_request_duration_seconds,
    bamboorose_api_requests_total,
    invoices_fetched_total,
    invoices_published_total,
    kafka_produce_failures_total,
)
from src.services.parser import parse_invoices
from src.settings.config import get_settings

initialize_logging()
logger = logging.getLogger(f"x35.{__name__}")


async def process_invoices(
    bamboorose_client: BambooroseClient, kafka_producer_client: KafkaProducerClient
) -> None:
    """
    Orchestrates the fetching, parsing, and publishing of invoices.
    
    This is the main entrypoint for the scheduled job.
    """
    trace_id = str(uuid.uuid4())
    with trace_context(trace_id):
        logger.info("Starting invoice processing run.")

        # In a real application, you would want to get the last successful
        # timestamp from a persistent store. For now, we will just use a
        # hardcoded value.
        available_timestamp = "2023-01-01T00:00:00Z"

        with dynamic_context(available_timestamp=available_timestamp):
            logger.info(f"Fetching invoices for timestamp: {available_timestamp}")
            start_time = time.time()
            try:
                response = await bamboorose_client.get_invoices(available_timestamp)
                bamboorose_api_requests_total.labels(outcome="success").inc()
            except Exception:
                bamboorose_api_requests_total.labels(outcome="failure").inc()
                raise
            finally:
                duration = time.time() - start_time
                bamboorose_api_request_duration_seconds.observe(duration)

            invoices = parse_invoices(response.text)
            invoices_fetched_total.inc(len(invoices))

            for invoice in invoices:
                try:
                    # Assuming invoice is an XML string, we parse it to get more context
                    invoice_xml = etree.fromstring(invoice.encode("utf-8"))
                    invoice_id_element = invoice_xml.find("invoice_id")
                    vendor_id_element = invoice_xml.find("vendor_id")
                    
                    invoice_id = invoice_id_element.text if invoice_id_element is not None else "unknown"
                    vendor_id = vendor_id_element.text if vendor_id_element is not None else "unknown"

                    with dynamic_context(invoice_id=invoice_id, vendor_id=vendor_id):
                        logger.info("Publishing invoice.")
                        await kafka_producer_client.publish_invoice(invoice, trace_id)
                        invoices_published_total.inc()
                except etree.XMLSyntaxError:
                    logger.error("Failed to parse invoice XML, skipping.")
                    continue
                except Exception:
                    kafka_produce_failures_total.inc()

            logger.info(
                "Invoice processing run finished.",
                extra={"invoices_published": len(invoices)},
            )


async def invoice_processing_loop(app: FastAPI):
    """Continuously processes invoices on a schedule."""
    settings = get_settings()
    bamboorose_client = app.state.bamboorose_client
    kafka_producer_client = app.state.kafka_producer_client

    while True:
        try:
            await process_invoices(bamboorose_client, kafka_producer_client)
        except Exception as e:
            logger.error("Error processing invoices", exc_info=e)
        
        logger.info(f"Sleeping for {settings.app.poll_interval_seconds} seconds.")
        await asyncio.sleep(settings.app.poll_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    This is where clients and other resources will be initialized.
    """
    logger.info("Application startup: initializing clients.")
    
    # Run blocking constructors in a thread
    kafka_producer_client = await asyncio.to_thread(get_kafka_producer_client)
    app.state.kafka_producer_client = kafka_producer_client
    
    # Non-blocking client can be initialized directly
    app.state.bamboorose_client = get_bamboorose_client()

    logger.info("Clients initialized. Starting background processing task.")
    
    loop = asyncio.get_running_loop()
    app.state.invoice_processor_task = loop.create_task(invoice_processing_loop(app))
    
    yield
    
    logger.info("Application shutdown: cleaning up resources.")
    if hasattr(app.state, "invoice_processor_task"):
        app.state.invoice_processor_task.cancel()

    if hasattr(app.state, "kafka_producer_client"):
        logger.info("Flushing Kafka producer.")
        await asyncio.to_thread(app.state.kafka_producer_client.producer.flush)
        logger.info("Kafka producer flushed.")
    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    """
    Creates the FastAPI application.

    This is a minimal application, as the service does not expose any APIs.
    The lifespan context manager is used to initialize clients.
    """
    settings = get_settings()
    
    builder = FastAPIAppBuilder(
        settings=settings.fastapi,
        routers=[metrics_router],
        lifespan=lifespan,
        middleware=[CustomHeaderMiddleware],
    )
    return builder.create_app()