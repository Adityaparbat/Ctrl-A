#!/usr/bin/env python3
"""
Fixed Web Interface for Digital Rights Bot
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
from simple_legal_api import answer_user_query

app = FastAPI(title="Digital Rights Bot Interface")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Digital Rights Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 800px;
                padding: 40px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            
            .chat-container {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                min-height: 400px;
                max-height: 500px;
                overflow-y: auto;
                border: 2px solid #e9ecef;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 15px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .user-message {
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            .bot-message {
                background: white;
                color: #333;
                border: 1px solid #dee2e6;
                margin-right: auto;
            }
            
            .input-container {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            .question-input {
                flex: 1;
                padding: 15px;
                border: 2px solid #dee2e6;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .question-input:focus {
                border-color: #007bff;
            }
            
            .ask-button {
                background: #007bff;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
                min-width: 80px;
            }
            
            .ask-button:hover {
                background: #0056b3;
            }
            
            .ask-button:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            
            .example-questions {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 15px;
            }
            
            .example-questions h3 {
                color: #333;
                margin-bottom: 15px;
            }
            
            .example-btn {
                background: #28a745;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 20px;
                margin: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            
            .example-btn:hover {
                background: #1e7e34;
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 10px;
            }
            
            .status {
                text-align: center;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-weight: bold;
            }
            
            .status.connected {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Digital Rights Assistant</h1>
                <p>Ask me anything about your digital rights, laws, and how to file complaints</p>
            </div>
            
            <div id="status" class="status connected">
                ✅ Connected - Ready to help!
            </div>
            
            <div id="error" class="error"></div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    👋 Hello! I'm your Digital Rights Assistant. I can help you understand:
                    <br><br>
                    • Your digital rights and freedoms<br>
                    • Applicable laws and regulations<br>
                    • How to file complaints<br>
                    • Enforcement authorities<br>
                    • Regional differences<br><br>
                    What would you like to know?
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="questionInput" class="question-input" 
                       placeholder="Ask me about your digital rights...">
                <button type="button" class="ask-button" id="askButton">
                    Ask
                </button>
            </div>
            
            <div class="loading" id="loading">
                🤔 Thinking...
            </div>
            
            <div class="example-questions">
                <h3>💡 Try these example questions:</h3>
                <button type="button" class="example-btn" data-question="What are my digital rights?">
                    What are my digital rights?
                </button>
                <button type="button" class="example-btn" data-question="What laws apply to data privacy?">
                    Data privacy laws
                </button>
                <button type="button" class="example-btn" data-question="How do I file a complaint for online harassment?">
                    File complaint for harassment
                </button>
                <button type="button" class="example-btn" data-question="Who enforces net neutrality?">
                    Net neutrality enforcement
                </button>
                <button type="button" class="example-btn" data-question="What regions does digital accessibility apply to?">
                    Digital accessibility regions
                </button>
            </div>
        </div>
        
        <script>
            // Debug function
            function debug(message) {
                console.log('[DEBUG]', message);
            }
            
            // Show error message
            function showError(message) {
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                }, 5000);
            }
            
            // Main ask function
            async function askQuestion() {
                debug('askQuestion called');
                
                const input = document.getElementById('questionInput');
                const button = document.getElementById('askButton');
                const loading = document.getElementById('loading');
                const chatContainer = document.getElementById('chatContainer');
                
                const question = input.value.trim();
                debug('Question: ' + question);
                
                if (!question) {
                    showError('Please enter a question!');
                    return;
                }
                
                try {
                    // Disable input and show loading
                    input.disabled = true;
                    button.disabled = true;
                    button.textContent = 'Asking...';
                    loading.style.display = 'block';
                    
                    // Add user message to chat
                    addMessage(question, 'user');
                    input.value = '';
                    
                    debug('Sending request to /ask');
                    
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });
                    
                    debug('Response status: ' + response.status);
                    
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    
                    const data = await response.json();
                    debug('Response data: ' + JSON.stringify(data));
                    
                    // Add bot response to chat
                    if (data.answer) {
                        addMessage(data.answer, 'bot');
                    } else {
                        addMessage('Sorry, I could not process your question. Please try again.', 'bot');
                    }
                    
                } catch (error) {
                    debug('Error: ' + error.message);
                    showError('Error: ' + error.message);
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                } finally {
                    // Re-enable input and hide loading
                    input.disabled = false;
                    button.disabled = false;
                    button.textContent = 'Ask';
                    loading.style.display = 'none';
                    input.focus();
                }
            }
            
            // Add message to chat
            function addMessage(text, type) {
                debug('Adding message: ' + type);
                
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                // Convert markdown-style formatting to HTML
                text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                text = text.replace(/\n/g, '<br>');
                
                messageDiv.innerHTML = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            // Handle Enter key
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    debug('Enter key pressed');
                    event.preventDefault();
                    askQuestion();
                }
            }
            
            // Initialize event listeners
            function initializeEventListeners() {
                debug('Initializing event listeners');
                
                // Ask button click
                const askButton = document.getElementById('askButton');
                if (askButton) {
                    askButton.addEventListener('click', function(e) {
                        debug('Ask button clicked');
                        e.preventDefault();
                        askQuestion();
                    });
                } else {
                    showError('Ask button not found!');
                }
                
                // Input keypress
                const questionInput = document.getElementById('questionInput');
                if (questionInput) {
                    questionInput.addEventListener('keypress', handleKeyPress);
                } else {
                    showError('Question input not found!');
                }
                
                // Example buttons
                const exampleButtons = document.querySelectorAll('.example-btn');
                exampleButtons.forEach(button => {
                    button.addEventListener('click', function(e) {
                        debug('Example button clicked: ' + this.dataset.question);
                        e.preventDefault();
                        const question = this.dataset.question;
                        if (question) {
                            document.getElementById('questionInput').value = question;
                            askQuestion();
                        }
                    });
                });
                
                debug('Event listeners initialized');
            }
            
            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', function() {
                debug('DOM loaded, initializing...');
                initializeEventListeners();
                
                // Focus on input
                const input = document.getElementById('questionInput');
                if (input) {
                    input.focus();
                }
                
                debug('Initialization complete');
            });
            
            // Fallback for older browsers
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializeEventListeners);
            } else {
                initializeEventListeners();
            }
        </script>
    </body>
    </html>
    """

@app.post("/ask")
async def ask_question(request: Request):
    """Handle questions from the web interface"""
    try:
        data = await request.json()
        question = data.get("question", "")
        if not question:
            return {"answer": "Please provide a question."}
        
        answer = answer_user_query(question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"I encountered an error: {str(e)}"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Fixed web interface is running"}

if __name__ == "__main__":
    print("🌐 Starting Fixed Digital Rights Bot Web Interface...")
    print("🔗 Open your browser and go to: http://localhost:8002")
    print("📱 Mobile-friendly interface with debug logging")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)