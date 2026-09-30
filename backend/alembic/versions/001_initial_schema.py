"""Initial schema — all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(200), nullable=True),
        sa.Column("profile_picture", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("role", sa.Enum("user", "admin", name="userrole"), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("google_id", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    # tourist_places
    op.create_table(
        "tourist_places",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("city", sa.String(150), nullable=False),
        sa.Column("state", sa.String(150), nullable=True),
        sa.Column("country", sa.String(150), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=True),
        sa.Column("opening_hours", sa.String(200), nullable=True),
        sa.Column("entry_fee", sa.Float(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_indoor", sa.Boolean(), nullable=True),
        sa.Column("estimated_duration_hours", sa.Float(), nullable=True),
        sa.Column("best_time_to_visit", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # hotels
    op.create_table(
        "hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("city", sa.String(150), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("star_rating", sa.Integer(), nullable=True),
        sa.Column("user_rating", sa.Float(), nullable=True),
        sa.Column("price_per_night", sa.Float(), nullable=False),
        sa.Column("amenities", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("website", sa.String(300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # restaurants
    op.create_table(
        "restaurants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("city", sa.String(150), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("cuisine", sa.String(200), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("price_range", sa.String(50), nullable=True),
        sa.Column("avg_cost_for_two", sa.Float(), nullable=True),
        sa.Column("opening_hours", sa.String(200), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # reviews
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("hotel_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("restaurant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["place_id"], ["tourist_places.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hotel_id"], ["hotels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # user_preferences
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interests", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("preferred_transport", sa.Enum("car","bike","walk","public","flight", name="transportmode"), nullable=True),
        sa.Column("preferred_hotel_rating", sa.Integer(), nullable=True),
        sa.Column("max_budget_per_day", sa.Float(), nullable=True),
        sa.Column("travel_style", sa.String(50), nullable=True),
        sa.Column("preferred_cuisine", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("preferred_travel_time", sa.String(50), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # trips
    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("start_location", sa.String(300), nullable=False),
        sa.Column("end_location", sa.String(300), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("travel_days", sa.Integer(), nullable=True),
        sa.Column("budget", sa.Float(), nullable=True),
        sa.Column("transport_mode", sa.Enum("car","bike","walk","public","flight", name="transportmode"), nullable=True),
        sa.Column("group_size", sa.Integer(), nullable=True),
        sa.Column("status", sa.Enum("draft","active","completed","cancelled", name="tripstatus"), nullable=True),
        sa.Column("itinerary", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("total_cost", sa.Float(), nullable=True),
        sa.Column("is_saved", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # user_history
    op.create_table(
        "user_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["place_id"], ["tourist_places.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_history")
    op.drop_table("trips")
    op.drop_table("user_preferences")
    op.drop_table("reviews")
    op.drop_table("restaurants")
    op.drop_table("hotels")
    op.drop_table("tourist_places")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS tripstatus")
    op.execute("DROP TYPE IF EXISTS transportmode")
    op.execute("DROP TYPE IF EXISTS userrole")
