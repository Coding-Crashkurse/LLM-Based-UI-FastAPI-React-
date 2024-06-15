from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActionRequest(BaseModel):
    action: str


@app.post("/perform-action")
async def perform_action(action_request: ActionRequest):
    action = action_request.action.lower()
    response = {"action": action}

    if action == "change color":
        response["background_color"] = "blue"
    elif action == "trigger animation":
        response["animation"] = "bounce"
    elif action == "change text":
        response["text"] = "You changed the text!"
    elif action == "play sound":
        print("play sound")
        response["sound"] = "/moo.mp3"
    else:
        response["error"] = "Unknown action"

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
