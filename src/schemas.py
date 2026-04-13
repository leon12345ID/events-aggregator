
from pydantic import BaseModel


class TicketCreate(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str

class TicketResponse(BaseModel):
    ticket_id: str
