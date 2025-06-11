"""new proc

Revision ID: 93d9a935176e
Revises: 200e699eb1eb
Create Date: 2025-06-11 22:23:02.964358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93d9a935176e'
down_revision: Union[str, None] = '200e699eb1eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE OR REPLACE FUNCTION subscribe_to_plan(p_wallet_id INT, p_plan_id INT)
    RETURNS TABLE(
        subscription_id INT,
        wallet_id INT,
        plan_id INT,
        status TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        message TEXT
    ) AS $$
    DECLARE
        v_plan_amount FLOAT;
        v_duration INT;
        v_balance FLOAT;
        v_existing_id INT;
        v_subscription_id INT;
    BEGIN
        -- Validate plan
        SELECT plan_amount, duration_in_days INTO v_plan_amount, v_duration
        FROM plan WHERE plan_id = p_plan_id AND is_active = TRUE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Invalid or inactive plan';
        END IF;

        -- Check wallet balance
        SELECT monthly_balance INTO v_balance
        FROM wallet WHERE wallet_id = p_wallet_id;
        
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Wallet not found';
        END IF;


        -- Deactivate existing subscription
        SELECT subscription_id INTO v_existing_id
        FROM subscription
        WHERE wallet_id = p_wallet_id AND is_active = TRUE;

        IF FOUND THEN
            UPDATE subscription
            SET is_active = FALSE
            WHERE subscription_id = v_existing_id;

            INSERT INTO subscription_history(subscription_id, wallet_id, plan_id, status, comment)
            VALUES (v_existing_id, p_wallet_id, p_plan_id, 'cancelled', 'Auto-cancelled before new subscription');
        END IF;

        -- Deduct balance
        UPDATE wallet
        SET monthly_balance = monthly_balance + v_plan_amount,
            updated_at = NOW()
        WHERE wallet_id = p_wallet_id;

        -- Create new subscription
        INSERT INTO subscription(wallet_id, plan_id, is_active, start_time, end_time, is_billed)
        VALUES (
            p_wallet_id, p_plan_id, TRUE, NOW(), NOW() + (v_duration || ' days')::interval, TRUE
        )
        RETURNING subscription.subscription_id INTO v_subscription_id;

        -- Log history
        INSERT INTO subscription_history(subscription_id, wallet_id, plan_id, status, comment)
        VALUES (v_subscription_id, p_wallet_id, p_plan_id, 'activated', 'Subscribed to new plan');

        -- Return structured data
        RETURN QUERY SELECT 
            v_subscription_id,
            p_wallet_id,
            p_plan_id,
            'active'::TEXT,
            NOW()::TIMESTAMP,
            (NOW() + (v_duration || ' days')::interval)::TIMESTAMP,
            'Subscription successful'::TEXT;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION cancel_subscription(p_wallet_id INT)
    RETURNS TABLE(
        subscription_id INT,
        wallet_id INT,
        plan_id INT,
        status TEXT,
        end_time TIMESTAMP,
        message TEXT
    ) AS $$
    DECLARE
        v_sub_id INT;
        v_plan_id INT;
    BEGIN
        SELECT s.subscription_id, s.plan_id INTO v_sub_id, v_plan_id
        FROM subscription s
        WHERE s.wallet_id = p_wallet_id AND s.is_active = TRUE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'No active subscription found';
        END IF;

        UPDATE subscription
        SET is_active = FALSE, end_time = NOW()
        WHERE subscription_id = v_sub_id;

        INSERT INTO subscription_history(subscription_id, wallet_id, plan_id, status, comment)
        VALUES (v_sub_id, p_wallet_id, v_plan_id, 'cancelled', 'User cancelled');

        RETURN QUERY SELECT 
            v_sub_id,
            p_wallet_id,
            v_plan_id,
            'cancelled'::TEXT,
            NOW()::TIMESTAMP,
            'Subscription cancelled'::TEXT;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION renew_subscription(p_wallet_id INT)
    RETURNS TABLE(
        subscription_id INT,
        wallet_id INT,
        plan_id INT,
        status TEXT,
        end_time TIMESTAMP,
        message TEXT
    ) AS $$
    DECLARE
        v_sub_id INT;
        v_plan_id INT;
        v_plan_amount FLOAT;
        v_duration INT;
        v_balance FLOAT;
        v_new_end_time TIMESTAMP;
    BEGIN
        SELECT s.subscription_id, s.plan_id INTO v_sub_id, v_plan_id
        FROM subscription s
        WHERE s.wallet_id = p_wallet_id AND s.is_active = TRUE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'No active subscription found';
        END IF;

        SELECT plan_amount, duration_in_days INTO v_plan_amount, v_duration
        FROM plan WHERE plan_id = v_plan_id;

        SELECT monthly_balance INTO v_balance
        FROM wallet WHERE wallet_id = p_wallet_id;


        -- Deduct balance
        UPDATE wallet
        SET monthly_balance = monthly_balance + v_plan_amount
        WHERE wallet_id = p_wallet_id;

        -- Extend subscription
        UPDATE subscription
        SET end_time = end_time + (v_duration || ' days')::interval
        WHERE subscription_id = v_sub_id
        RETURNING end_time INTO v_new_end_time;

        INSERT INTO subscription_history(subscription_id, wallet_id, plan_id, status, comment)
        VALUES (v_sub_id, p_wallet_id, v_plan_id, 'renewed', 'Subscription renewed');

        RETURN QUERY SELECT 
            v_sub_id,
            p_wallet_id,
            v_plan_id,
            'active'::TEXT,
            v_new_end_time,
            'Subscription renewed'::TEXT;
    END;
    $$ LANGUAGE plpgsql;
    """)

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS subscribe_to_plan(INT, INT);")
    op.execute("DROP FUNCTION IF EXISTS cancel_subscription(INT);")
    op.execute("DROP FUNCTION IF EXISTS renew_subscription(INT);")
    pass
