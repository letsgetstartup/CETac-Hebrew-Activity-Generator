from pydantic import BaseModel, Field
from typing import List, Optional

# --- Request Model ---
class QuestionInput(BaseModel):
    id: int
    text: str

class AdaptContentRequest(BaseModel):
    original_text: str = Field(..., description="The original Hebrew text to simplify")
    original_questions: List[QuestionInput] = Field(..., description="List of original questions to scaffold")
    student_needs: Optional[str] = Field("general_difficulty", description="Specific need: dyslexia, adhd, etc.")

# --- Response Model ---
class GlossaryItem(BaseModel):
    term: str
    definition: str

class ScaffoldedQuestion(BaseModel):
    original_id: int
    hint: str
    cognitive_support: str

class AdaptedContentResponse(BaseModel):
    simplified_text: str
    glossary: List[GlossaryItem]
    scaffolded_questions: List[ScaffoldedQuestion]
