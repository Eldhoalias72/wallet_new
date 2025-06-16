import json
import pika

def publish_subscription_event(subscription_id: int):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="subscription_queue", durable=True)

    message = json.dumps({"subscription_id": subscription_id})

    channel.basic_publish(
        exchange='',
        routing_key='subscription_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2  # Make message persistent
        )
    )

    print(f"📤 Published subscription_id {subscription_id} to queue")
    connection.close()
