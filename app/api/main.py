from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import pika
import os
import json

app = FastAPI(
    title="Scalable Data Pipeline API",
    description="API for efficient data ingestion, processing, and retrieval.",
    version="0.1.0",
)

# RabbitMQ connection details from environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = "ingestion_queue"

class IngestDataRequest(BaseModel):
    data: Dict[str, Any]
    source: str
    timestamp: str # ISO 8601 format recommended

@app.on_event("startup")
async def startup_event():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print(f"Successfully connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Could not connect to RabbitMQ: {e}. Please ensure RabbitMQ is running.")
        # Depending on desired behavior, you might want to exit or retry here.

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Scalable Data Pipeline API! Access /docs for API documentation."}

@app.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_data(request: IngestDataRequest):
    """
    Ingest raw data into the pipeline.
    This endpoint accepts data and publishes it to a RabbitMQ queue for asynchronous processing.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        
        # Ensure the queue exists (idempotent operation)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        message = json.dumps(request.dict())
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()
        print(f"Published message to RabbitMQ: {message}")
        return {"message": "Data accepted for processing", "data_id": "message_published_to_queue"}
    except pika.exceptions.AMQPConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to RabbitMQ: {e}. Please ensure RabbitMQ is running.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to ingest data: {str(e)}")

# This endpoint is no longer needed as the queue is external
# @app.get("/queue_status")
# async def get_queue_status():
#     return {"message": "Queue status is now managed by RabbitMQ. Use RabbitMQ management UI (port 15672) for details."}

# Placeholder for future processing service endpoint
@app.post("/process_data")
async def process_data():
    """
    This endpoint would be consumed by the processing service.
    It would pull data from the message queue, process it, and store it.
    This endpoint is for demonstration/placeholder purposes only.
    """
    return {"message": "This endpoint is a placeholder. Data processing will be handled by a separate consumer service."}