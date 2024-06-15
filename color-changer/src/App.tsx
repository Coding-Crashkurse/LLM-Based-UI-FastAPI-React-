import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [backgroundColor, setBackgroundColor] = useState("white");
  const [text, setText] = useState("");
  const [animation, setAnimation] = useState("");
  const [sound, setSound] = useState<HTMLAudioElement | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [isRequestPending, setIsRequestPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );

  useEffect(() => {
    // Initialize MediaRecorder
    const initMediaRecorder = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        const recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);

        recorder.ondataavailable = async (event) => {
          const blob = new Blob([event.data], { type: "audio/wav" });

          const formData = new FormData();
          formData.append("file", blob, "voice-input.wav");

          setIsRequestPending(true);

          try {
            const response = await axios.post(
              "http://localhost:8000/perform-action",
              formData,
              {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
              }
            );
            const data = response.data;

            if (data.background_color) {
              setBackgroundColor(data.background_color);
            }
            if (data.animation) {
              setAnimation(data.animation);
              setTimeout(() => setAnimation(""), 1000); // Reset animation after 1 second
            }
            if (data.text) {
              setText(data.text);
            }
            if (data.sound) {
              const audio = new Audio(data.sound);
              setSound(audio);
              audio.play();
            }
            if (data.error) {
              console.error(data.error);
            }
          } catch (error) {
            console.error("There was an error!", error);
          } finally {
            setIsRequestPending(false);
          }
        };

        recorder.onerror = (event) => {
          console.error("Recording error:", event);
          setIsRecording(false);
        };
      } catch (err) {
        console.error("Error accessing media devices.", err);
        setError("Error accessing media devices.");
      }
    };

    initMediaRecorder();
  }, []);

  const handleStartApp = () => {
    const audio = new Audio("intro.mp3");
    setSound(audio);
    audio.play().catch((error) => {
      console.error("Audio play failed:", error);
    });
    setIsModalOpen(false);
  };

  const handleVoiceInput = () => {
    if (mediaRecorder && !isRecording) {
      mediaRecorder.start();
      setIsRecording(true);
      setError(null);

      // Automatically stop recording after 5 seconds (adjust as needed)
      setTimeout(() => {
        mediaRecorder.stop();
        setIsRecording(false);
      }, 5000);
    }
  };

  return (
    <div
      style={{
        backgroundColor,
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100vw",
        margin: 0,
      }}
    >
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Welcome to the App</h2>
            <button onClick={handleStartApp}>Start App</button>
          </div>
        </div>
      )}
      {!isModalOpen && (
        <div id="root" className={animation ? `animate-${animation}` : ""}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
            }}
          >
            <button
              type="button"
              onClick={handleVoiceInput}
              style={{
                width: "50%",
                padding: "10px",
                fontSize: "16px",
                cursor: "pointer",
                backgroundColor: isRecording ? "#d9534f" : "#5cb85c",
                color: "white",
                border: "none",
                borderRadius: "5px",
                marginBottom: "10px",
              }}
              disabled={isRequestPending}
            >
              {isRequestPending
                ? "...request is currently handled by AI"
                : isRecording
                ? "Recording..."
                : "Chat with UI"}
            </button>
          </div>
          {error && (
            <div style={{ color: "red", marginTop: "20px" }}>{error}</div>
          )}
          <div style={{ marginTop: "20px", fontSize: "24px", color: "black" }}>
            {text}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
