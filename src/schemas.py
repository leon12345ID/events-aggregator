from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PlaceSchema(BaseModel):
    id: UUID
    name: str
    city: str
    address: str | None = None
    seats_pattern: str | None = None

class EventDetailSchema(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    place: PlaceSchema

class TicketCreate(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str

class TicketResponse(BaseModel):
    ticket_id: str
