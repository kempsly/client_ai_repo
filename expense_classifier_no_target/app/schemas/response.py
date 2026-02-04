from pydantic import BaseModel

class PredictionResponse(BaseModel):
    gl_account_number: str
    confidence_score: float
    alternative_gl_account_number: str
    reasoning: str
