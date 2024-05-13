from typing import Optional, List
from langchain.pydantic_v1 import BaseModel, Field


class Address(BaseModel):
    """Address of a Person"""
    address_line1: Optional[str] = Field(default=None ,description="Address Line 1")
    address_line2: Optional[str] = Field(default=None ,description="Address Line 2")
    city: Optional[str] = Field(default=None ,description="Name of the city")
    state: Optional[str] = Field(default=None ,description="Abbreviation for state")
    zipcode: Optional[str] = Field(default=None ,description="Zip code") 


class Candidate(BaseModel):
    """Candidate name and contact information"""
    fullname: Optional[str] = Field(default=None, description="Name of the person")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone Number")
    address: Optional[Address] = Field(default=None, description="Candidate's address")


class ProfessionalSummary(BaseModel):
    """Professional summary as presented in the resume by the candidate. Appears as Summary, Executive Summary, Abstract, or Professional Summary in the resume"""
    summary: Optional[str] = Field(default=None, description="Executive or Professional summary")


class Skill(BaseModel):
    """Canidate skill"""
    skill: Optional[str] = Field(default=None, description="Candidates's skill")


class Skills(BaseModel):
    """List of candidates skill within a category"""
    category: Optional[str] = Field(default=None, description="Skills category")
    skills: Optional[List[Skill]]


class CandidateSkills(BaseModel):
    """List of candidate skills organized by category"""
    candidate_skills: Optional[List[Skills]]


class Degree(BaseModel):
    """Degree pursued, or completed"""
    school: Optional[str] = Field(default=None, description="Name of school, college or university")
    degree: Optional[str] = Field(default=None, description="Name of the Degree")
    specialization: Optional[str] = Field(default=None, description="Specialization")
    year_graduated: Optional[str] = Field(default=None, description="Year graduated")
    month_graduated: Optional[str] = Field(default=None, description="Month graduated")

class Education(BaseModel):
    """Degree pursued, or completed"""
    education: List[Optional[Degree]] = Field(default=None, description="List of degrees obtained")


class ToolUsed(BaseModel):
    """Tool used at the work place"""
    tool_name: Optional[str] = Field(default=None, description="Name of the tool used")
    tool_version: Optional[str] = Field(default=None, description="Version number of the tool used")


class Experience(BaseModel):
    """Professional Experience in a company worked"""
    company: Optional[str] = Field(default=None, description="Company name")
    location: Optional[str] = Field(default=None, description="Company location city, state and country")
    role: Optional[str] = Field(default=None, description="Role or Designation")
    start_year: Optional[str] = Field(default=None, description="Year started")
    start_month: Optional[str] = Field(default=None, description="Month started")
    end_year: Optional[str] = Field(default=None, description="Year Ended")
    end_month: Optional[str] = Field(default=None, description="Month Ended")
    current_job: Optional[bool] = Field(default=None, description="True if experience is current else False")
    experience_detail: Optional[str] = Field(default=None, description="Work experience in this company")
    tools_used: Optional[List[ToolUsed]] = Field(default=None, description="Tools used at this company")


class ProfessionalExperience(BaseModel):
    """List of all all companies where the candidate worked along with experience in each"""
    experiences: List[Optional[Experience]] = Field(default=None, description="Listing of all experiences")


class Certification(BaseModel):
    """Professional Certification pursued or obtained"""
    certification_name: Optional[str] = Field(default=None, description="Certification name")
    year_certified: Optional[str] = Field(default=None, description="Year certified")
    month_certified: Optional[str] = Field(default=None, description="Month certified")


class Certifications(BaseModel):
    """List of all Professional Certifications pursued or obtained"""
    Certitications: List[Optional[Certification]] = Field(default=None, description="List of all Certifications")


class Training(BaseModel):
    """Professional Training completed"""
    company: Optional[str] = Field(default=None, description="Name of school, institution, or online academic program")
    training: Optional[str] = Field(default=None, description="Name of the training program")
    year_completed: Optional[str] = Field(default=None, description="Year completed")
    month_completed: Optional[str] = Field(default=None, description="Month completed")


class ProfessionalTraining(BaseModel):
    """List of all Professional Training completed"""
    company: Optional[str] = Field(default=None, description="Name of school, institution, or online academic program")
    training: Optional[str] = Field(default=None, description="Name of the training program")
    year_completed: Optional[str] = Field(default=None, description="Year completed")
    month_completed: Optional[str] = Field(default=None, description="Month completed")


class OverallResumeSummary(BaseModel):
    """LLM generated summary in the style of a third person describing candidate's name, educational, and professional experience and accomplishments based on contents presentd in the resume. Limit the summary to approximately 300 words."""
    summary:Optional[str] = Field(
        default=None, description="Summary of the resume"
    )


class AllResumeContents(BaseModel):
    """
    All content in the resume including:
        candidate's name, contact information
        professional summary
        education
        skills
        professional experience
        professional training
        certifications
        overall resume summary
    """
    candidate: Candidate
    candidate_summary: ProfessionalSummary
    education: Education
    skills: Skills
    experience: ProfessionalExperience
    training: ProfessionalTraining
    certifications: Certifications
    overall_summary: OverallResumeSummary 
    

