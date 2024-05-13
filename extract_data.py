import operator
import re
import json
from typing import TypedDict, List, Annotated, Sequence, Dict, Any, Union
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from entities import ReflectionOuput


class AgentState(TypedDict):
    text: str
    pydantic_class: BaseModel
    messages: Annotated[Sequence[BaseMessage], operator.add]
    num_validation_attempts: int
    parsed_object: BaseModel
    validation_status: str
    max_validation_attempts: int
    reflection_status: str


class InformationExtractor:
    """A class for extracting information from text using LLMs"""

    def __init__(self, pydantic_class: BaseModel, max_validation_attempts: int = 5):
        """
        Initializes the InformationExtractor.

        Args:
            pydantic_class (BaseModel): 
                class that defines elements and the structure of the information to be extracted
            max_validation_attempts (int, optional): 
                maximum number of validation attempts allowed. Defaults to 5.
        """
        self.pydantic_class = pydantic_class
        self.max_validation_attempts = max_validation_attempts
        self.wf = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the workflow for extracting, validating and reviewing the task output.

        Returns:
            StateGraph: compiled workflow.
        """
        g = StateGraph(AgentState)
        g.add_node("prompt", self._invoke_prompt)
        g.add_node("generate", self._generate)
        g.add_node("validate", self._validate)
        g.add_node("reflect", self._reflect)
        g.add_edge("prompt", "generate")
        g.add_edge("generate", "validate")
        g.add_conditional_edges(
            "validate",
            self._should_generate,
            {
                "end": END,
                "generate": "generate",
                "reflect": "reflect"
            }
        )
        g.add_conditional_edges(
            "reflect",
            self._should_end,
            {
                "end": END,
                "generate": "generate",
            }
        )
        g.set_entry_point("prompt")
        return g.compile()
    

    def _invoke_prompt(self, state: AgentState) -> Dict[str, Any]:
        """
        Invokes the prompt template for extracting information.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            Dict[str, Any]: dictionary containing the updated state.
        """
        print("** invoke_prompt **")
        parser = PydanticOutputParser(pydantic_object=state['pydantic_class'])
        template = ChatPromptTemplate.from_messages(
            messages=[
                ("system", "You are provided with TEXT. Your task is to extract information from TEXT and format as per FORMAT_INSTRUCTIONS provided."),
                ("human", "TEXT:\n\n{text}\n\n FORMAT_INSTRUCTIONS: {format_instructions}\nMake sure to process each item as per the instruction. Pay special attention to the nested structures and ensure your formatting follows instructions 100%.")
            ]
        )
        input = {
            'text': state['text'],
            'format_instructions': parser.get_format_instructions()
        }
        response = template.invoke(input=input)
        return {"messages": response.messages, "validation_status": "fail", "num_validation_attempts": 0, "reflection_status": "n/a"}


    def _generate(self, state: AgentState) -> Dict[str, Any]:
        """
        Generates the extracted information using an LLM.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            Dict[str, Any]: dictionary containing the updated state.
        """
        num_validation_attempts = state['num_validation_attempts'] + 1
        print(f"** generate ATTEMPT #: {num_validation_attempts} **")
        reflection_status = state["reflection_status"]
        validation_status = state["validation_status"]

        print(f"validation_status: {validation_status}")
        print(f"reflection_status: {reflection_status}")

        messages = state['messages']
        # llm = AzureChatOpenAI(model="gpt-3.5-turbo-0613", api_version="2024-03-01-preview", azure_deployment="sa001gpt35turbo0613", temperature=0.0)
        # llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        response = llm.invoke(messages)
        return {"messages": [response], "num_validation_attempts": num_validation_attempts}

    
    def _extract_json_content(self, text):
        # Regex to extract content, handling optional backticks and 'json' literal, with possible preceding text
        pattern = r'```json\s*(.*?)```|```(.*?)```|(.+)'
        match = re.search(pattern, text, re.DOTALL)
        json_text = None
        if match:
            # Return the first non-None group that captures the desired content
             json_text = next((m for m in match.groups() if m is not None), None)
        if not json_text:
            print(f"json extraction failed for text:\n{text}")
            raise ValueError
        return json_text


    def _validate(self, state: AgentState) -> Dict[str, Any]:
        """
        Validates the extracted information against the Pydantic model.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            Dict[str, Any]: dictionary containing the updated state.
        """
        print("** validate **")
        last_message = state['messages'][-1]
        num_validation_attempts = state['num_validation_attempts']
        reflection_status = state["reflection_status"]
        validation_status = state["validation_status"]

        print(f"num_validation_attempts: {num_validation_attempts}")
        print(f"validation_status: {validation_status}")
        print(f"reflection_status: {reflection_status}")

        try:
            # print(f"last_message.content:\n{last_message.content}")
            # json_text = re.findall(r'```json\s*(.*)```', last_message.content, re.DOTALL)[0]
            # print(f"json_text: \n{json_text}")
            # obj = state['pydantic_class'](**json.loads(json_text))
            
            json_text = self._extract_json_content(last_message.content)
            print(f"json_text:\n{json_text}")
            obj = state['pydantic_class'](**json.loads(json_text))
        except Exception as e:
            print(e)
            message = HumanMessage(f"Error parsing JSON: {e}\n Address these errors.")
            return {'messages': [message], "validation_status": "fail", "reflection_status": reflection_status}
        return {'validation_status': "pass", 'parsed_object': obj}


    def _reflect(self, state: AgentState) -> Dict[str, Any]:
        """
        Reflects on the extracted information and provides feedback.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            Dict[str, Any]: dictionary containing the updated state.
        """
        print("** reflect **")
        messages = state['messages']
        num_validation_attempts = state['num_validation_attempts']
        reflection_status = state["reflection_status"]
        validation_status = state["validation_status"]

        print(f"num_validation_attempts: {num_validation_attempts}")
        print(f"validation_status: {validation_status}")
        print(f"reflection_status: {reflection_status}")

        # reflect_llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
        reflect_llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        reflect_parser = PydanticOutputParser(pydantic_object=ReflectionOuput)
        reflect_prompt = ChatPromptTemplate.from_messages(
            messages=[
                messages[0], # system message for 'generate'
                messages[1], # human mesage for generate
                ("human", """Review the parsed object: ```{parsed_object}``` and provide your recommendations. Format your response based on this format instructions: {format_instructions}""")
            ]
        )
        chain = reflect_prompt | reflect_llm | reflect_parser
        input = {
            "format_instructions": reflect_parser.get_format_instructions(),
            "parsed_object": state['parsed_object'].json()
        }
        response = chain.invoke(input)
        print(f"reflect_response: {response}")

        review = response.review
        recommendations = response.recommendations
        feedback = response.feedback
        
        if feedback == 'perfect':
            reflection_status = 'completed'
        else:
            reflection_status = 'needs work'
        human_message = HumanMessage(content=f"Review:\n{review}\nRecommendations: {recommendations}", type="human")
        return {"messages": [human_message], "reflection_status": reflection_status}


    def _should_generate(self, state: AgentState) -> str:
        """
        Determines whether to rerun generate to address parse exceptions.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            str: next action to take ("end", "generate", or "reflect").
        """
        print("** should_generate **")
        num_validation_attempts = state['num_validation_attempts']
        validation_status = state["validation_status"]
        reflection_status = state["reflection_status"]
        max_validation_attempts = state["max_validation_attempts"]

        print(f"num_validation_attempts: {num_validation_attempts}")
        print(f"validation_status: {validation_status}")
        print(f"reflection_status: {reflection_status}")
        print(f"max_validation_attempts: {max_validation_attempts}")

        if num_validation_attempts >= max_validation_attempts:
            print("attempts exceeded max_attempts")
            print("-- finish | E N D --")
            return "end"

        if validation_status == 'pass':
            if reflection_status == 'completed':
                print("-- finish | E N D --")
                return "end"
            else:
                print("-- reflect --")
                return "reflect"

        print("-- generate --")
        return "generate"


    def _should_end(self, state: AgentState) -> str:
        """
        Determines whether to end the workflow after reflection.

        Args:
            state (AgentState): current state of the agent.

        Returns:
            str: next action to take ("end" or "generate").
        """
        print("** should_end **")
        num_validation_attempts = state['num_validation_attempts']
        validation_status = state["validation_status"]
        reflection_status = state["reflection_status"]
        max_validation_attempts = state["max_validation_attempts"]

        print(f"num_validation_attempts: {num_validation_attempts}")
        print(f"validation_status: {validation_status}")
        print(f"reflection_status: {reflection_status}")
        print(f"max_validation_attempts: {max_validation_attempts}")

        if reflection_status == "needs work":
            print("-- generate --")
            return "generate"

        print("-- finish | E N D --")
        return "end"


    def extract_information(self, text: str) -> Union[BaseModel, None]:
        """
        Extracts information from the given text using the workflow.

        Args:
            text (str): input text to extract information from.

        Returns:
            Union[BaseModel, None]: parsed Pydantic object if successful, None otherwise.
        """
        input = {
            "text": text,
            "pydantic_class": self.pydantic_class,
            "messages": [],
            "num_validation_attempts": 0,
            "max_validation_attempts": self.max_validation_attempts
        }
        response = self.wf.invoke(input)
        return response.get('parsed_object')