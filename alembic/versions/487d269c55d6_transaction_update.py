"""transaction_update

Revision ID: 487d269c55d6
Revises: 3b3fc365bb30
Create Date: 2025-06-10 14:44:58.739078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '487d269c55d6'
down_revision: Union[str, None] = '3b3fc365bb30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS process_wallet_transaction(INTEGER, VARCHAR, FLOAT, VARCHAR, VARCHAR, VARCHAR);")
    op.execute("""
    CREATE OR REPLACE FUNCTION process_wallet_transaction(
        p_wallet_id INTEGER,
        p_transaction_type VARCHAR,
        p_amount FLOAT,
        p_source VARCHAR DEFAULT NULL,
        p_remark VARCHAR DEFAULT NULL,
        p_additional_info VARCHAR DEFAULT NULL
    )
    RETURNS INTEGER AS $$
    DECLARE
        v_monthly_balance FLOAT;
        v_fixed_balance FLOAT;
        v_previous_balance FLOAT;
        v_new_monthly_balance FLOAT;
        v_new_fixed_balance FLOAT;
        v_new_current_balance FLOAT;
        v_remaining_amount FLOAT;
        v_transaction_id INTEGER;
    BEGIN
        -- Get current wallet balances with row-level lock
        SELECT monthly_balance, fixed_balance 
        INTO v_monthly_balance, v_fixed_balance
        FROM wallet 
        WHERE wallet_id = p_wallet_id
        FOR UPDATE;
        
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Wallet with ID % not found', p_wallet_id;
        END IF;
        
        -- Calculate previous total balance
        v_previous_balance := v_monthly_balance + v_fixed_balance;
        
        -- Process based on transaction type
        IF LOWER(p_transaction_type) = 'credit' THEN
            -- For credit, add to fixed balance
            v_new_monthly_balance := v_monthly_balance + p_amount;
            v_new_fixed_balance := v_fixed_balance ;
            v_new_current_balance := v_new_monthly_balance + v_new_fixed_balance;
            
        ELSIF LOWER(p_transaction_type) = 'debit' THEN
            -- Check if sufficient balance exists
            IF v_previous_balance < p_amount THEN
                RAISE EXCEPTION 'Insufficient balance. Available: %, Required: %', v_previous_balance, p_amount;
            END IF;
            
            -- Deduct from monthly balance first, then fixed balance
            v_remaining_amount := p_amount;
            
            IF v_monthly_balance >= v_remaining_amount THEN
                -- Sufficient monthly balance
                v_new_monthly_balance := v_monthly_balance - v_remaining_amount;
                v_new_fixed_balance := v_fixed_balance;
            ELSE
                -- Need to use both monthly and fixed balance
                v_remaining_amount := v_remaining_amount - v_monthly_balance;
                v_new_monthly_balance := 0;
                v_new_fixed_balance := v_fixed_balance - v_remaining_amount;
            END IF;
            
            v_new_current_balance := v_new_monthly_balance + v_new_fixed_balance;
            
        ELSE
            RAISE EXCEPTION 'Invalid transaction type. Must be either credit or debit, got: %', p_transaction_type;
        END IF;
        
        -- Update wallet balances
        UPDATE wallet 
        SET 
            monthly_balance = v_new_monthly_balance,
            fixed_balance = v_new_fixed_balance,
            updated_at = NOW()
        WHERE wallet_id = p_wallet_id;
        
        -- Insert wallet transaction record
        INSERT INTO wallet_transaction (
            wallet_id,
            transaction_type,
            amount,
            previous_balance,
            current_balance,
            updated_at,
            source,
            remark,
            additional_info
        ) VALUES (
            p_wallet_id,
            LOWER(p_transaction_type),
            p_amount,
            v_previous_balance,
            v_new_current_balance,
            NOW(),
            p_source,
            p_remark,
            p_additional_info
        ) RETURNING transaction_id INTO v_transaction_id;
        
        RETURN v_transaction_id;
    END;
    $$ LANGUAGE plpgsql;
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS process_wallet_transaction(INTEGER, VARCHAR, FLOAT, VARCHAR, VARCHAR, VARCHAR);")
    pass
