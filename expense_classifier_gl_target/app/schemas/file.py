from pydantic import BaseModel

class FileResponse(BaseModel):
    message: str
    filename: str
