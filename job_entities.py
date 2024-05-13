from typing import Optional, List
from langchain.pydantic_v1 import BaseModel, Field


class JobTitle(BaseModel):
    """Title of the job or role"""
    jobtitle: Optional[str] = Field(default=None, description="Job title")


class Opportunity(BaseModel):
    """Description of the job opportunity"""
    opportunity: Optional[str] = Field(default=None, description="Opportunity description")


class Qualification(BaseModel):
    """Qualification for the job opportunity"""
    qualification: Optional[str] = Field(default=None, description="qualification for the job")


class MandatoryQualifications(BaseModel):
    """Mandatory Qualifications for the job opportunity. This is the list of all mandatory qualifications."""
    mandatory_qualifications: Optional[List[Qualification]] = Field(
        default=None, description="list of mandatory qualifications"
    )


class OptionalQualifications(BaseModel):
    """Optional (nice to have) Qualifications for the job opportunity. This is the lis of all optional qualifications."""
    optional_qualifications: Optional[List[Qualification]] = Field(
        default=None, description="list of optional qualifications"
    )


class ClearanceRequirement(BaseModel):
    """Security Clearance requirement for the job"""
    clearance: Optional[str] = Field(default=None, description="Name of clearance e.g. Secret, Top Secret, TS, SCI")
    additional_attributes: Optional[str] = Field(default=None, description="Additional attributes like polygraph")


class ToolExperience(BaseModel):
    """Experience required per tool. Tool can be a programing language, database, framework, etc."""
    tool: Optional[str] = Field(default=None, description="Name of the tool. e.g Java, SQL, Oracle, RedShift, EMR, or Airflow")
    version: Optional[str] = Field(default=None, description="Version of the tool")
    number_of_years: Optional[int] = Field(default=None, description="Number of years of experience required")
    mandatory: Optional[bool] = Field(default=None, description="True if mandatory else False")


class ProfessionalExperienceWithTools(BaseModel):
    """List of tools and required experience. If multiple tools are listed in a single line, ensure to create one ToolExperience per tool."""
    professional_tool_experiences:Optional[List[ToolExperience]] = Field(
        default=None, description="List of tools and experiences required"
    )


class JobDescriptionSummary(BaseModel):
    """Summary in third person and under 300 words, detailing the job description. This summary should highlight essential qualifications, including educational background, experience, certifications required, and any necessary clearances."""
    summary:Optional[str] = Field(
        default=None, description="Job Description Summary"
    )


class CompleteJobProfile(BaseModel):
    """Complete Job Profile containing JobTitle, Opportunity, MandatoryQualification, OptionalQualifications, ProfessionalExperienceWithTools and JobDescriptionSummary"""
    jobtitle: Optional[JobTitle]
    opportunity: Optional[Opportunity]
    mandatory_qualifications: Optional[MandatoryQualifications]
    optional_qualifications: Optional[OptionalQualifications]
    professional_experience_with_tools: Optional[ProfessionalExperienceWithTools]
    clearance_requirement: Optional[ClearanceRequirement]
    job_description_summary: Optional[JobDescriptionSummary]