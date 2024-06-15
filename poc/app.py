from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import shutil
import os
from dotenv import load_dotenv

load_dotenv()


class ActionResponse(BaseModel):
    """Responsible for triggering action based on user input"""

    action: str = Field(description="Action to be performed")
    background_color: str = Field(description="Background color", default=None)
    animation: str = Field(description="Animation to trigger", default=None)
    text: str = Field(description="Text to change", default=None)
    sound: str = Field(description="Sound to play", default=None)
    error: str = Field(description="Error message", default=None)


class ActionRequest(BaseModel):
    action: str


client = OpenAI()
model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
structured_llm = model.with_structured_output(ActionResponse)

action_system = """You are an action identifier. Identify the action from the user input and provide the appropriate response.
For 'change color', set 'background_color' to input of the user.
For 'trigger animation', set 'animation' to the input of the user.
For 'change text', set 'text' to the input of the user.
For 'play sound', set 'sound' to user input. Cat = cat.mp3, Cow = cow.mp3, Dog = dog.mp3.
If the action is unknown, set 'error' to 'Unknown action'.
"""

action_prompt = ChatPromptTemplate.from_messages(
    [("system", action_system), ("human", "Action: {action}")]
)
action_chef = action_prompt | structured_llm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/perform-action", response_model=ActionResponse)
async def perform_action(file: UploadFile = File(...)):
    print("FILE:", file)

    try:
        file_path = f"./uploaded_files/{file.filename}"

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        transcription_text = transcription.text
        print(f"Transcription: {transcription_text}")

        result = action_chef.invoke({"action": transcription_text})
        print("Action triggered:", result)

        # Optionally remove the file after processing
        os.remove(file_path)

        return result
    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
