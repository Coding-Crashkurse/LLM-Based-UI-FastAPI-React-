import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [backgroundColor, setBackgroundColor] = useState("white");
  const [text, setText] = useState("Hello, World!");
  const [animation, setAnimation] = useState(false);
  const [sound, setSound] = useState<HTMLAudioElement | null>(null);

  const handleChange = (event: any) => {
    setInput(event.target.value);
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8000/perform-action",
        { action: input }
      );
      const data = response.data;

      if (data.background_color) {
        setBackgroundColor(data.background_color);
      }
      if (data.animation) {
        setAnimation(true);
        setTimeout(() => setAnimation(false), 1000); // Reset animation after 1 second
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
      }}
    >
      <div id="root" className={animation ? "animate" : ""}>
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
          }}
        >
          <input
            type="text"
            value={input}
            onChange={handleChange}
            placeholder="Enter an action"
            style={{
              width: "50%",
              padding: "10px",
              fontSize: "16px",
              marginBottom: "10px",
            }}
          />
          <button
            type="submit"
            style={{
              width: "50%",
              padding: "10px",
              fontSize: "16px",
              cursor: "pointer",
              backgroundColor: "#007BFF",
              color: "white",
              border: "none",
              borderRadius: "5px",
              marginBottom: "10px",
            }}
          >
            Submit
          </button>
        </form>
        <div style={{ marginTop: "20px", fontSize: "24px", color: "black" }}>
          {text}
        </div>
      </div>
    </div>
  );
}

export default App;
