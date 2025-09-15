async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  // Show user message
  addMessage("user", userMessage);
  inputField.value = "";

  try {
    // Send request to Ollama server
    const response = await fetch("http://127.0.0.1:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "gpt-oss", // change model name if needed
        prompt: userMessage,
        stream: false
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const botMessage = data.response || "⚠️ No response from model.";
    addMessage("bot", botMessage);

  } catch (error) {
    console.error("Error:", error);
    addMessage("bot", "⚠️ Error: Could not connect to Ollama server.");
  }
}

// Utility: append message to chat window
function addMessage(sender, text) {
  const messagesDiv = document.getElementById("messages");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message");
  messageDiv.innerHTML = `<span class="${sender}">${sender}:</span> ${text}`;
  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
