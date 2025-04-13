from pydantic import BaseModel


class TaskPayload(BaseModel):
    action: str
    total_files: int
