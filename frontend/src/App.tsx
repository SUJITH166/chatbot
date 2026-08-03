import { useState } from "react";
import "./App.css";

function App() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL;
    
  const askQuestion = async () => {
 console.log("entered askQuestion 1")
    if (!question) return;

    setLoading(true);

    try {
      console.log("entered try 2")
      const response = await fetch(
        `${API_URL}/ask`,
        
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


