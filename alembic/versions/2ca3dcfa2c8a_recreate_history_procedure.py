"""recreate history procedure

Revision ID: 2ca3dcfa2c8a
Revises: b81b24ddd46d
Create Date: 2025-06-16 11:59:14.249689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ca3dcfa2c8a'
down_revision: Union[str, None] = 'b81b24ddd46d'
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
        SELECT * INTO sub_rec FROM subscription WHERE subscription_id = sub_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Subscription not found for ID: %', sub_id;
        END IF;

        SELECT * INTO plan_rec FROM plan WHERE plan_id = sub_rec.plan_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Plan not found for ID: %', sub_rec.plan_id;
        END IF;

        comment_text := format(
            'Plan "%s" activated for %s days',
            plan_rec.plan_name,
            plan_rec.duration_in_days
        );

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
