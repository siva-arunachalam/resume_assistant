from typing import Union, IO, Dict, Any
from textwrap import dedent
import json

from langchain.prompts import ChatPromptTemplate
from util import initialize_model, timestamp, read_content


class AssessResume:
    """
    Conducts assessment of a resume for a given job description
    """
    def __init__(self, resume: Union[str, Dict], job_description: Union[str, Dict], model_name):
        """
        Iniitializes AssessResume

        Args:
            resume (str): Parsed resume
            job_description (str): Parsed job description
            model_name (str): LLM model to use
        """
        self.prompt = self._create_prompt()
        self.resume_content = resume
        self.job_content = job_description
        self.model = initialize_model(model_name)


    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Creates a prompt template

        Args: 
            None
        
        Returns:
            ChatPromptTemplate: Chat prompt template configured to use resume and job description as template variables 
        """
        return ChatPromptTemplate.from_messages(
            messages=[
                (
                    "system", 
                    dedent(
                        """
                        You are a highly skilled resume sourcer with extensive experience in screening candidates for technology roles within the high-tech industry. You are provided with key information from a candidate's resume and a job description in JSON format. Your task is to assess the suitability of the resume for the role using a carefully designed rubric.
                        Data Format:
                        - Job Description: Contains fields like job opportunity, required education, skills, certifications, mandatory and optional experience, and clearance requirements.
                        - Resume Content: Includes candidate contact information, location, skills, professional experience, tools used, certifications, training, education, and clearance status.
                        
                        RESUME CONTENT: {resume_content}
                        JOB DESCRIPTION CONTENT: {job_content}

                        Scoring Rubric:
                        1. Education: Score 5 if the candidate meets the education requirement, otherwise 0.
                        2. Mandatory Experience: Calculate score as (number of requirements met / total requirements) * 10.
                        3. Optional Experience: Calculate score as (number of optional items met / total optional items) * 5.
                        4. Tools: Score as (number of tools met / total tools listed) * 5.
                        5. Certifications: Score as (number of certifications met / total certifications listed) * 5.
                        6. Clearance: Score 5 if the candidate meets the clearance requirement, otherwise 0.
                        7. For categories not listed in the job description, assign the full score available for that category.
                        8. Sum the scores and convert the total to a percentage of 35.
                        9. If the information in the job description or resume is insufficient for a reliable assessment, note this in your summary.
                        10. Provide a detailed analysis for each category, the score obtained, and a final summary of the candidate's match to the job requirements. For each line item within the category, provide your reasoning on how the candidate matches or otherwise. Highlight if any mandatory requirements are not met, as this will disqualify the candidate.
                        11. Include your recommendation on whether to proceed with considering the candidate for the role.

                        Note: Ensure all calculations and data handling are done accurately, taking into account the structured nature of JSON data inputs.
                        """
                    )
                )
            ]
        )


    def assess(self):
        """
        Executes the assessment to determine how well the resume matched job requirements.

        Args:
            None
        
        Returns:
            object: Returns response from LLM
        """
        chain = self.prompt | self.model 
        input = {
            "job_content": self.job_content,
            "resume_content": self.resume_content
        }
        response = chain.invoke(input=input)
        return response.content

