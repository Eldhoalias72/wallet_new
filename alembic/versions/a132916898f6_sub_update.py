"""sub_update

Revision ID: a132916898f6
Revises: 487d269c55d6
Create Date: 2025-06-10 15:01:27.357996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a132916898f6'
down_revision: Union[str, None] = '487d269c55d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE OR REPLACE PROCEDURE complete_subscription(p_subscription_id INT)
    LANGUAGE plpgsql
    AS $$
    DECLARE
        v_wallet_id INT;
        v_plan_id INT;
        v_amount FLOAT;
        v_duration INT;
        v_now TIMESTAMP := NOW();
        v_end TIMESTAMP;
    BEGIN
        -- Get wallet_id and plan_id from subscription
        SELECT wallet_id, plan_id INTO v_wallet_id, v_plan_id
        FROM subscription
        WHERE subscription_id = p_subscription_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Subscription not found';
        END IF;

        -- Get plan details
        SELECT plan_amount, duration_in_days INTO v_amount, v_duration
        FROM plan
        WHERE plan_id = v_plan_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Plan not found';
        END IF;

        -- Call existing wallet transaction processor
        PERFORM process_wallet_transaction(
            v_wallet_id,
            'credit',
            v_amount,
            'Subscription',
            CONCAT('Subscription for plan ', v_plan_id),
            CONCAT('subscription_id=', p_subscription_id)
        );

        -- Update subscription record
        v_end := v_now + (v_duration || ' days')::INTERVAL;

        UPDATE subscription
        SET
            is_billed = TRUE,
            is_active = TRUE,
            start_time = v_now,
            end_time = v_end
        WHERE subscription_id = p_subscription_id;

    END;
    $$;


    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP PROCEDURE IF EXISTS complete_subscription(INTEGER);")
    pass
