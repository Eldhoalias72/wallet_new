import json
import pika
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.models.user import Subscription, PlanFeature
from datetime import datetime, timezone
from app.database import Base

# Setup database connection
DATABASE_URL = "postgresql://postgres:anjora31@localhost:5432/wallet"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def process_feature_usage(subscription_id: int, feature_id: int):
    session = SessionLocal()

    try:
        subscription = session.query(Subscription).filter_by(subscription_id=subscription_id).first()
        if not subscription:
            raise ValueError("Subscription not found")

        wallet_id = subscription.wallet_id  # ✅ This line fixes your issue

        feature = session.query(PlanFeature).filter_by(
            feature_id=feature_id, plan_id=subscription.plan_id
        ).first()
        if not feature:
            raise ValueError("Feature not found in this subscription plan")

        # Call stored procedure
        session.execute(
            text("""
                SELECT process_wallet_transaction(
                    :wallet_id, :type, :amount, :source, :remark, :info
                )
            """),
            {
                "wallet_id": wallet_id,
                "type": "debit",
                "amount": feature.points,
                "source": "feature_usage",
                "remark": f"Used feature: {feature.feature_name}",
                "info": f"Subscription ID: {subscription_id}, Feature ID: {feature_id}"
            }
        )
        session.commit()

    except Exception as e:
        print(f"❌ Error during feature usage processing: {e}")
        session.rollback()
    finally:
        session.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        subscription_id = data.get("subscription_id")
        feature_id = data.get("feature_id")

        if subscription_id and feature_id:
            process_feature_usage(subscription_id, feature_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            

        else:
            print("❌ Invalid message format")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        print("✅ Successfully processed feature_point deduction.\n")

    except Exception:
        print("❌ Failed to process message, requeuing...")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue='feature_usage_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='feature_usage_queue', on_message_callback=callback)
    print("🚀 Feature Usage Worker started, waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
