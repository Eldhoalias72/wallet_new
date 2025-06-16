"""history

Revision ID: b81b24ddd46d
Revises: 6d169775c3e0
Create Date: 2025-06-16 10:57:40.343304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b81b24ddd46d'
down_revision: Union[str, None] = '6d169775c3e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE PROCEDURE history(sub_id INT)
    LANGUAGE plpgsql
    AS $$
    DECLARE
        sub_rec RECORD;
        plan_rec RECORD;
        comment_text TEXT;
    BEGIN
        -- Fetch subscription
        SELECT * INTO sub_rec FROM subscription WHERE subscription_id = sub_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Subscription not found for ID: %', sub_id;
        END IF;

        -- Fetch plan
        SELECT * INTO plan_rec FROM plan WHERE plan_id = sub_rec.plan_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Plan not found for ID: %', sub_rec.plan_id;
        END IF;

        -- Compose comment
        comment_text := format(
            'Plan "%s" activated for %s days',
            plan_rec.plan_name,
            plan_rec.duration_in_days
        );

        -- Insert into history
        INSERT INTO subscription_history (
            subscription_id,
            wallet_id,
            plan_id,
            status,
            comment,
            created_at
        ) VALUES (
            sub_rec.subscription_id,
            sub_rec.wallet_id,
            sub_rec.plan_id,
            'activated',
            comment_text,
            NOW()
        );
    END;
    $$;
    """)

def downgrade():
    op.execute("DROP PROCEDURE IF EXISTS history(INT);")
