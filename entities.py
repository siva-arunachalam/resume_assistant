from typing import Optional, List
from langchain.pydantic_v1 import BaseModel, Field
from resume_entities import AllResumeContents
from job_entities import CompleteJobProfile

class ReflectionOuput(BaseModel):
    review: str = Field(default="n/a", description="Review of the parsed object as to how well it aligns with the expected format")
    recommendations: str = Field(default="n/a", description="Actionable recommendations formatted as a bulleted list for making necessary changes to align with original formatting instructions and improvement if needed for any attribute. Use examples as needed.")
    feedback: str = Field(default="n/a", description="'perfect' if no changes are required, or 'needs work' otherwise")

