import streamlit as st
from datetime import datetime
import os
import json
from assess import AssessResume
from extract_data import InformationExtractor
from resume_entities import AllResumeContents
from entities import CompleteJobProfile, AllResumeContents
from util import load_document_using_unstructured


def save_file(uploaded_file: object) -> None:
    """
    Saves the uploaded files in a folder locally
    
    Args:
    uploaded_file(UploadedFile): The uploaded file object

    Returns: None
    """
    filename = f"{runs_dir}/{uploaded_file.name}"
    os.makedirs(runs_dir, exist_ok=True)
    with open(filename, "wb") as f:
        f.write(uploaded_file.getvalue())


def display_contents(contents):
    """
    Displays the extracted contents in a text box
    Args:
        contents (dict): The extracted contents
    Returns: None
    """
    formatted_contents = json.dumps(contents, indent=4)
    st.text_area("Summary:", value=formatted_contents, height=400)


def extract_contents(content_type, filename):
    if content_type == "resume":
        pydantic_class = AllResumeContents
    elif content_type == "jd":
        pydantic_class = CompleteJobProfile
    else:
        return ValueError
    extractor = InformationExtractor(pydantic_class=pydantic_class)
    text = load_document_using_unstructured(fname=filename)
    # st.write(f"{content_type}:\n{text}")
    return extractor.extract_information(text)


def model_name_from_selection(model_selection: str) -> str:
    """
    Returns model name for a given model_selection

    Args:
        model_selection (str): Selected model 
    
    Returns:
        model_name (str): model_name
    """
    model_dict = {
        "GPT 3.5": "gpt_35",
        "GPT 4 Preview": "gpt_4_0125",
        "GPT 4": "gpt_4",
        "GPT 4o": "gpt_4o",
        "Haiku": "haiku",
        "Sonnet": "sonnet",
        "Llama 3": "llama3",
        "Mistral 7B": "mistral"
    }
    return model_dict[model_selection]


st.set_page_config(
    page_title="Resume Assessment", 
    page_icon=":file_folder:", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("Resume Match Analysis for a Role")
with st.sidebar:
    resume = st.file_uploader("Upload Candidate's Resume")
    jd = st.file_uploader("Upload Job Description")
    model_for_parsing = st.radio(
        "Select a model to parse documents:", 
        options=["GPT 3.5", "GPT 4", "GPT 4o"], 
        horizontal=True, 
        index=0
    )
    parsing_model_name = model_name_from_selection(model_for_parsing)
    model_for_assessment = st.radio(
        "Select a model to assess candidate qualification:", 
        options=["GPT 3.5", "GPT 4", "GPT 4o"], 
        horizontal=True, 
        index=1
    )
    assessment_model_name = model_name_from_selection(model_for_assessment)
    kickoff = st.button("Process")


if kickoff and resume and jd:
    st.session_state.resume = resume
    st.session_state.jd = jd
    # st.write(f"resume.name: {resume.name}")
    # st.write(f"jd.name: {jd.name}")

    runs_dir = f"data/runs"
    st.session_state.resume_filename = f"{runs_dir}/{resume.name}"
    st.session_state.jd_filename = f"{runs_dir}/{jd.name}"
    save_file(resume)
    save_file(jd)

    resume_content = extract_contents("resume", st.session_state.resume_filename)    
    jd_content = extract_contents("jd", st.session_state.jd_filename)
    # st.write(f"jd_content: {jd_content}")
    # st.write(f"resume_content: {resume_content}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Resume")
        display_contents(resume_content.overall_summary.summary)

    with col2:
        st.subheader("Job Description")
        display_contents(jd_content.job_description_summary.summary)

    assessment = AssessResume(resume_content.dict(), jd_content.dict(), model_name=assessment_model_name)
    assessment_response = assessment.assess()
    st.subheader("Assessment")
    st.markdown(assessment_response)
