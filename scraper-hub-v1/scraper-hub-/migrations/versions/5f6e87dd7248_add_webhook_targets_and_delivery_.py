"""Add webhook targets and delivery attempts

Revision ID: 5f6e87dd7248
Revises: e0be562ba886
Create Date: 2026-04-17 14:40:11.696936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f6e87dd7248'
down_revision: Union[str, None] = 'e0be562ba886'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "webhook_targets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("secret", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
    )

    delivery_status_enum = sa.Enum("pending", "success", "failed", "dead_letter", name="deliverystatus")
    delivery_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "webhook_delivery_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("webhook_targets.id"), nullable=False),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("extracted_records.id"), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", delivery_status_enum, nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("webhook_delivery_attempts")
    op.drop_table("webhook_targets")
    sa.Enum(name="deliverystatus").drop(op.get_bind(), checkfirst=True)
