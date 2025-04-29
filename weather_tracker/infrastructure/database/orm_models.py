from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)


class LocationORM(Base):
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[Decimal] = mapped_column(nullable=False)
    longitude: Mapped[Decimal] = mapped_column(nullable=False)

    __table_args__ = (UniqueConstraint("latitude", "longitude", name="unique_lat_long"),)


class UserLocationORM(Base):
    __tablename__ = "user_locations"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.id"), primary_key=True)
