import pika
import os
import json
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = "ingestion_queue"

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Received {data}")
    # Simulate processing time
    time.sleep(2)
    print(f" [x] Done processing {data}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = None
    while connection is None:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
            print(f"Consumer connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Consumer could not connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(' [*] Consumer stopped by user.')
        channel.stop_consuming()
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == '__main__':
    main()
