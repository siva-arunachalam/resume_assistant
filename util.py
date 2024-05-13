from typing import Union, Dict
from collections import namedtuple
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import io
from pdf2docx import Converter


def datestamp() -> str:
    """
    Generates a datestamp in the format YYYYMMDD

    Returns: 
        str: String representing current date
    """
    return datetime.now().strftime("%Y%m%d")


def timestamp() -> str:
    """
    Generates a timestamp in the format YYYYMMDDHHMMSS

    Returns: 
        str: String representing current timestamp
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def read_content(jd: Union[str, io.BytesIO, None]) -> str:
    """
    Reads the contents of a job description file.

    Args:
    jd (BytesIO or str): Either a file handle (BytesIO) or a filename (str)

    Returns:
    str: The contents of the job description file
    """
    if isinstance(jd, str):  # if jd is a filename
        with open(jd, 'r') as file:
            return file.read()
    elif hasattr(jd, 'read'):  # if jd is a file handle
        return jd.read()
    else:
        return ""
    

def initialize_model(model_name:str) ->Union[ChatOpenAI, ChatAnthropic]:
    """
    Initializes the appropriate language model based on the model name.

    Args:
        model_name (str): The identifier for the model configuration.

    Returns:
        Union[ChatOpenAI, ChatAnthropic]: An instance of the model.

    Raises:
        ValueError: If the model name is unsupported.
    """
    ModelDetail = namedtuple('ModelDetail', ['model_name', 'model_class'])

    models: Dict[str, tuple] = {
        'gpt_35': ModelDetail('gpt-3.5-turbo-0125', ChatOpenAI),
        'gpt_4': ModelDetail('gpt-4-turbo-2024-04-09', ChatOpenAI),
        'gpt_4_0125': ModelDetail('gpt-4-0125-preview', ChatOpenAI),
        'haiku': ModelDetail('claude-3-haiku-20240307', ChatAnthropic),
        'sonnet': ModelDetail('claude-3-sonnet-20240229', ChatAnthropic),
        'llama3': ModelDetail('llama3-70b-8192', ChatGroq),
        'mistral': ModelDetail('mistral:instruct', ChatOpenAI)
    }

    ollama_base_url = ""
    ollama_api_key = ""
    temperature = 0.0
    if model_name in models:
        model_detail = models[model_name]
        model_name = model_detail.model_name
        model = model_detail.model_class
        if model_name in ['llama3:instruct', 'mistral:instruct']:
            return model(
                base_url=ollama_base_url, 
                api_key=ollama_api_key, 
                temperature=temperature, 
                model=model_name
            )
        return model(model_name=model_name, temperature=temperature)
    else:
        raise ValueError("Unsupported model name")    


from pdfminer.high_level import extract_text
def extract_text_from_pdf(pdf_file: str) -> str:
    """
    Extracts text from pdf document

    Args:
        pdf_file (str): 
    
    Returns:
        text (str): Returns text
    """
    text = extract_text(pdf_file)
    return text


from langchain_community.document_loaders import UnstructuredPDFLoader
def load_pdf_using_unstructured(pdf_file):
    loader = UnstructuredPDFLoader(pdf_file)
    data = loader.load()
    return data[0].page_content


from langchain_community.document_loaders import UnstructuredWordDocumentLoader
def load_docx_using_unstructured(docx):
    loader = UnstructuredWordDocumentLoader(docx)
    docs = loader.load()
    return docs[0].page_content


import os
def load_document_using_unstructured(fname):
    ext = os.path.splitext(fname)[1].lower()
    # print(f"fname: {fname}")
    # print(f"ext: {ext}")

    try:
        if ext == '.pdf':
            try:
                text = load_pdf_using_unstructured(fname)
            except KeyError as e:
                print(f"KeyError encountered: {e}")
                print("Trying other methods...")
                text = extract_text_from_pdf(fname)
        elif ext == '.docx':
            text = load_docx_using_unstructured(fname)
        elif ext == '.txt':
            text = open(fname, 'r').read()
        else:
            raise NotImplementedError("The file extension is not supported.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  

    return text
