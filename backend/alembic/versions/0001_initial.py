"""initial schema: tour, booking

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tour",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False, server_default="0"),
        sa.Column("available_slots", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tour_country", "tour", ["country"])
    op.create_index("ix_tour_price", "tour", ["price"])
    op.create_index("ix_tour_start_date", "tour", ["start_date"])

    op.create_table(
        "booking",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("tour_id", sa.Uuid(), nullable=False),
        sa.Column("user_name", sa.String(), nullable=False),
        sa.Column("user_email", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("num_people", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="confirmed"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tour_id"], ["tour.id"]),
    )
    op.create_index("ix_booking_tour_id", "booking", ["tour_id"])
    op.create_index("ix_booking_user_email", "booking", ["user_email"])


def downgrade() -> None:
    op.drop_index("ix_booking_user_email", table_name="booking")
    op.drop_index("ix_booking_tour_id", table_name="booking")
    op.drop_table("booking")
    op.drop_index("ix_tour_start_date", table_name="tour")
    op.drop_index("ix_tour_price", table_name="tour")
    op.drop_index("ix_tour_country", table_name="tour")
    op.drop_table("tour")
