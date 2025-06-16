import pika, json
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Replace with your actual DB URL
engine = create_engine(DATABASE_URL)

def callback(ch, method, properties, body):
    data = json.loads(body)
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                SELECT process_wallet_transaction(
                    :wallet_id, :transaction_type, :amount,
                    :source, :remark, :additional_info
                )
            """), {
                "wallet_id": data["wallet_id"],
                "transaction_type": data["transaction_type"],
                "amount": data["amount"],
                "source": data["source"],
                "remark": data["remark"],
                "additional_info": data["additional_info"]
            })
        print("✅ Wallet debited for feature usage")
    except Exception as e:
        print("❌ Error processing transaction:", e)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="feature_usage_queue", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="feature_usage_queue", on_message_callback=callback)
    print("🐇 Waiting for feature usage messages")
    channel.start_consuming()

if __name__ == "__main__":
    main()
