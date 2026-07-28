import { useState } from "react";
import "./App.css";

function App() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);


  const askQuestion = async () => {

    if (!question) return;

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question,
          }),
        }
      );


      const data = await response.json();

      setAnswer(data.answer);

    } catch (error) {

      console.log(error);
      setAnswer("Error connecting to backend");

    }

    setLoading(false);
  };


  return (
    <div className="container">

      <h1>
        PDF Chatbot
      </h1>


      <div className="chat-box">

        <input
          type="text"
          placeholder="Ask something about your PDF..."
          value={question}
          onChange={(e)=>setQuestion(e.target.value)}
        />


        <button onClick={askQuestion}>
          Ask
        </button>

      </div>


      {loading && (
        <p>
          Searching PDF...
        </p>
      )}


      <div className="answer">

        <h3>
          Answer:
        </h3>

        <p>
          {answer}
        </p>

      </div>


    </div>
  );
}


export default App;


