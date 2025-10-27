from pydantic import BaseModel

class ScheduleRequest(BaseModel):
    prompt: str
