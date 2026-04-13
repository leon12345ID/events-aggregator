import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=True)
    seats_pattern = Column(String, nullable=True)

    events = relationship("Event", back_populates="place")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    event_time = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    number_of_visitors = Column(Integer, default=0)

    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    place = relationship("Place", back_populates="events")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_ticket_id = Column(String, unique=True, nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    seat = Column(String, nullable=False)


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id = Column(Integer, primary_key=True, default=1)
    last_sync_time = Column(DateTime, nullable=True)
    last_changed_at = Column(String, nullable=True)
    sync_status = Column(String, default="idle")
