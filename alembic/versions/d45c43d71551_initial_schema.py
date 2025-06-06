"""Initial schema

Revision ID: d45c43d71551
Revises: d0e798b3441e
Create Date: 2025-06-05 12:19:31.284369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd45c43d71551'
down_revision: Union[str, None] = 'd0e798b3441e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan', sa.Column('value', sa.Float(), nullable=True))
    op.drop_column('plan', 'cost')
    op.drop_column('plan_feature', 'quantity')
    op.drop_column('plan_feature', 'is_deductable')
    op.drop_column('plan_feature', 'value')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan_feature', sa.Column('value', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('plan_feature', sa.Column('is_deductable', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('plan_feature', sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('plan', sa.Column('cost', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('plan', 'value')
    # ### end Alembic commands ###
