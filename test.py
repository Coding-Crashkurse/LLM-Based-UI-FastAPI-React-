from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class ActionResponse(BaseModel):
    action: str = Field(description="Action to be performed")
    background_color: str = Field(description="Background color", default=None)
    animation: str = Field(description="Animation to trigger", default=None)
    text: str = Field(description="Text to change", default=None)
    sound: str = Field(description="Sound to play", default=None)
    error: str = Field(description="Error message", default=None)


class ActionRequest(BaseModel):
    action: str


# Initialize the OpenAI model with structured output
model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
structured_llm = model.with_structured_output(ActionResponse)


action = "Spiel den Moo sound ab."


action_system = """You are an action identifier. Identify the action from the user input and provide the appropriate response.
    For 'change color', set 'background_color' to 'blue'.
    For 'trigger animation', set 'animation' to 'bounce'.
    For 'change text', set 'text' to 'You changed the text!'.
    For 'play sound', set 'sound' to '/moo.mp3'.
    If the action is unknown, set 'error' to 'Unknown action'.
"""

action_prompt = ChatPromptTemplate.from_messages(
    [("system", action_system), ("human", "Action: {action}")]
)
action_chef = action_prompt | structured_llm


result = action_chef.invoke({"action": action})
print(result)
