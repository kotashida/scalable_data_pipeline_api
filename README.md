# Scalable Data Pipeline API

This project implements a scalable and resilient data ingestion pipeline using a decoupled, asynchronous architecture. It is designed to handle high-throughput data streams, ensuring reliability and providing a foundation for robust data processing systems.

## Core Concepts

The system is built around the principle of asynchronous processing. An API gateway receives data and, instead of processing it directly, offloads it to a message queue. This decouples the ingestion point from the processing logic, allowing the API to remain highly responsive under load and ensuring that data is not lost if downstream services are temporarily unavailable.

## Architectural Overview

The pipeline consists of three main containerized services orchestrated by Docker Compose:

1.  **API Gateway (`api` service):**
    *   **Technology:** FastAPI (Python)
    *   **Responsibility:** Exposes a public `/ingest` endpoint to accept incoming data. It validates the request, then publishes the data as a persistent message to a RabbitMQ queue.
    *   **Behavior:** Responds immediately to the client with a `202 Accepted` status, confirming receipt of the data without waiting for it to be processed.

2.  **Message Queue (`rabbitmq` service):**
    *   **Technology:** RabbitMQ with the management plugin.
    *   **Responsibility:** Acts as a durable, intermediate buffer for data. It guarantees message delivery to the consumer service.
    *   **Monitoring:** The RabbitMQ Management UI is accessible at `http://localhost:15672` (user: `guest`, pass: `guest`) for real-time monitoring of queues, message rates, and consumer status.

3.  **Ingestion Consumer (`ingestion_service`):**
    *   **Technology:** Python with the Pika library.
    *   **Responsibility:** Connects to the RabbitMQ queue and listens for incoming messages. It fetches messages one at a time for processing.
    *   **Behavior:** Upon receiving a message, it performs a simulated processing task. After the task is complete, it sends an acknowledgment (`ack`) to RabbitMQ, which then safely removes the message from the queue.

## Technology Stack

-   **API Framework:** **FastAPI** was chosen for its high performance, native asynchronous support, and automatic generation of interactive API documentation.
-   **Message Broker:** **RabbitMQ** provides a mature and reliable messaging system with essential features like message persistence and consumer acknowledgments, which are critical for building a fault-tolerant pipeline.
-   **Containerization:** **Docker & Docker Compose** are used to define and run the multi-container application, ensuring a consistent and reproducible environment for development and deployment.

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kotashida/scalable-data-pipeline-api.git
    cd scalable-data-pipeline-api
    ```

2.  **Build and start the services:**
    ```bash
    docker-compose up --build
    ```
    This command will build the necessary Docker images and start the API gateway, RabbitMQ, and the ingestion consumer.

### Interacting with the Pipeline

1.  **View the API Documentation:**
    Open `http://localhost:8000/docs` in your browser to access the interactive Swagger UI for the API.

2.  **Ingest Data:**
    Use the `/ingest` endpoint in the documentation or a command-line tool like `curl` to send data to the pipeline.
    ```bash
    curl -X POST "http://localhost:8000/ingest" -H "Content-Type: application/json" -d '{ "source": "curl-test", "timestamp": "2024-07-29T12:00:00Z", "data": { "sensor_id": "A-123", "temperature": 25.5 } }'
    ```

3.  **Observe the System:**
    -   Check the logs from `docker-compose` to see the `api` service publishing the message and the `ingestion_service` receiving and processing it.
    -   Visit the **RabbitMQ Management UI** at `http://localhost:15672` to see message statistics and queue activity.

## Future Enhancements

This project provides a foundational architecture that can be extended in several ways:

-   **Persistent Data Storage:** Integrate a database (e.g., PostgreSQL for structured data, InfluxDB for time-series data) into the consumer to store the processed data.
-   **Horizontal Scaling:** Launch multiple replicas of the `ingestion_service` to demonstrate how RabbitMQ automatically distributes the workload among available consumers.
-   **Dead-Letter Queue (DLQ):** Implement a DLQ to capture and isolate messages that cannot be processed successfully, preventing them from blocking the main queue and allowing for later analysis.
-   **Monitoring and Alerting:** Integrate monitoring tools like Prometheus to scrape metrics from the services and Grafana to build dashboards for visualizing system health and performance.
