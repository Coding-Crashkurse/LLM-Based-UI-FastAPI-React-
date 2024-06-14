from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()


# Define the response model
class ActionResponse(BaseModel):
    """Responsible for triggering action based on user input"""

    action: str = Field(description="Action to be performed")
    background_color: str = Field(description="Background color", default=None)
    animation: str = Field(description="Animation to trigger", default=None)
    text: str = Field(description="Text to change", default=None)
    sound: str = Field(description="Sound to play", default=None)
    error: str = Field(description="Error message", default=None)


# Define the request model
class ActionRequest(BaseModel):
    action: str


# Initialize the OpenAI model with structured output
model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
structured_llm = model.with_structured_output(ActionResponse)

# Define the system prompt
action_system = """You are an action identifier. Identify the action from the user input and provide the appropriate response.
For 'change color', set 'background_color' to input of the user.
For 'trigger animation', set 'animation' to 'bounce'.
For 'change text', set 'text' to the input of the user.
For 'play sound', set 'sound' to '/moo.mp3'.
If the action is unknown, set 'error' to 'Unknown action'.
"""

action_prompt = ChatPromptTemplate.from_messages(
    [("system", action_system), ("human", "Action: {action}")]
)
action_chef = action_prompt | structured_llm

# Create the FastAPI app
app = FastAPI()

# CORS configuration to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/perform-action")
async def perform_action(action_request: ActionRequest):
    action = action_request.action
    result = action_chef.invoke({"action": action})
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
