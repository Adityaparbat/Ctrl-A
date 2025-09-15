#!/usr/bin/env python3
"""
Ultra-Simple Digital Rights Bot - No JavaScript needed!
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn
from simple_legal_api import answer_user_query

app = FastAPI(title="Simple Digital Rights Bot")

# Store conversation history
conversation_history = []

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main page with working form"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Digital Rights Assistant</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            input[type="text"] {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            input[type="text"]:focus {{
                border-color: #007bff;
                outline: none;
            }}
            button {{
                background: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
            }}
            button:hover {{
                background: #0056b3;
            }}
            .examples {{
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 5px;
            }}
            .examples h3 {{
                margin-bottom: 15px;
                color: #333;
            }}
            .example-btn {{
                background: #28a745;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                margin: 5px;
                cursor: pointer;
                font-size: 14px;
            }}
            .example-btn:hover {{
                background: #1e7e34;
            }}
            .response {{
                margin-top: 20px;
                padding: 20px;
                background: #e9ecef;
                border-radius: 5px;
                border-left: 4px solid #007bff;
                white-space: pre-line;
            }}
            .conversation {{
                margin-top: 20px;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background: #f8f9fa;
            }}
            .message {{
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 5px;
            }}
            .user-msg {{
                background: #007bff;
                color: white;
                text-align: right;
            }}
            .bot-msg {{
                background: white;
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Digital Rights Assistant</h1>
            
            <form method="post" action="/ask">
                <div class="form-group">
                    <label for="question">Ask your question:</label>
                    <input type="text" id="question" name="question" 
                           placeholder="What are my digital rights?" required>
                </div>
                <button type="submit">Ask Question</button>
            </form>
            
            <div class="examples">
                <h3>💡 Example Questions:</h3>
                <form method="post" action="/ask" style="display: inline;">
                    <input type="hidden" name="question" value="What are my digital rights?">
                    <button type="submit" class="example-btn">What are my digital rights?</button>
                </form>
                <form method="post" action="/ask" style="display: inline;">
                    <input type="hidden" name="question" value="What laws apply to data privacy?">
                    <button type="submit" class="example-btn">Data privacy laws</button>
                </form>
                <form method="post" action="/ask" style="display: inline;">
                    <input type="hidden" name="question" value="How do I file a complaint for online harassment?">
                    <button type="submit" class="example-btn">File harassment complaint</button>
                </form>
                <form method="post" action="/ask" style="display: inline;">
                    <input type="hidden" name="question" value="Who enforces net neutrality?">
                    <button type="submit" class="example-btn">Net neutrality enforcement</button>
                </form>
                <form method="post" action="/ask" style="display: inline;">
                    <input type="hidden" name="question" value="What regions does digital accessibility apply to?">
                    <button type="submit" class="example-btn">Digital accessibility regions</button>
                </form>
            </div>
            
            <div class="conversation">
                <h3>📝 Conversation History:</h3>
                {get_conversation_html()}
            </div>
        </div>
    </body>
    </html>
    """

def get_conversation_html():
    """Generate HTML for conversation history"""
    if not conversation_history:
        return "<p><em>No conversation yet. Ask a question above!</em></p>"
    
    html = ""
    for item in conversation_history[-10:]:  # Show last 10 messages
        if item['type'] == 'user':
            html += f'<div class="message user-msg"><strong>You:</strong> {item["text"]}</div>'
        else:
            html += f'<div class="message bot-msg"><strong>Bot:</strong> {item["text"]}</div>'
    
    return html

@app.post("/ask", response_class=HTMLResponse)
async def ask_question(question: str = Form(...)):
    """Handle form submission"""
    try:
        # Add user question to history
        conversation_history.append({
            'type': 'user',
            'text': question
        })
        
        # Get answer
        answer = answer_user_query(question)
        
        # Add bot response to history
        conversation_history.append({
            'type': 'bot',
            'text': answer
        })
        
        # Return updated page
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Digital Rights Assistant</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .form-group {{
                    margin-bottom: 20px;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }}
                input[type="text"] {{
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                    box-sizing: border-box;
                }}
                input[type="text"]:focus {{
                    border-color: #007bff;
                    outline: none;
                }}
                button {{
                    background: #007bff;
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    width: 100%;
                }}
                button:hover {{
                    background: #0056b3;
                }}
                .examples {{
                    margin-top: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 5px;
                }}
                .examples h3 {{
                    margin-bottom: 15px;
                    color: #333;
                }}
                .example-btn {{
                    background: #28a745;
                    color: white;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 3px;
                    margin: 5px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .example-btn:hover {{
                    background: #1e7e34;
                }}
                .response {{
                    margin-top: 20px;
                    padding: 20px;
                    background: #e9ecef;
                    border-radius: 5px;
                    border-left: 4px solid #007bff;
                    white-space: pre-line;
                }}
                .conversation {{
                    margin-top: 20px;
                    max-height: 400px;
                    overflow-y: auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    background: #f8f9fa;
                }}
                .message {{
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .user-msg {{
                    background: #007bff;
                    color: white;
                    text-align: right;
                }}
                .bot-msg {{
                    background: white;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Digital Rights Assistant</h1>
                
                <div class="response">
                    <strong>Question:</strong> {question}
                    <br><br>
                    <strong>Answer:</strong>
                    <br>{answer}
                </div>
                
                <form method="post" action="/ask">
                    <div class="form-group">
                        <label for="question">Ask another question:</label>
                        <input type="text" id="question" name="question" 
                               placeholder="What are my digital rights?" required>
                    </div>
                    <button type="submit">Ask Question</button>
                </form>
                
                <div class="examples">
                    <h3>💡 Example Questions:</h3>
                    <form method="post" action="/ask" style="display: inline;">
                        <input type="hidden" name="question" value="What are my digital rights?">
                        <button type="submit" class="example-btn">What are my digital rights?</button>
                    </form>
                    <form method="post" action="/ask" style="display: inline;">
                        <input type="hidden" name="question" value="What laws apply to data privacy?">
                        <button type="submit" class="example-btn">Data privacy laws</button>
                    </form>
                    <form method="post" action="/ask" style="display: inline;">
                        <input type="hidden" name="question" value="How do I file a complaint for online harassment?">
                        <button type="submit" class="example-btn">File harassment complaint</button>
                    </form>
                    <form method="post" action="/ask" style="display: inline;">
                        <input type="hidden" name="question" value="Who enforces net neutrality?">
                        <button type="submit" class="example-btn">Net neutrality enforcement</button>
                    </form>
                    <form method="post" action="/ask" style="display: inline;">
                        <input type="hidden" name="question" value="What regions does digital accessibility apply to?">
                        <button type="submit" class="example-btn">Digital accessibility regions</button>
                    </form>
                </div>
                
                <div class="conversation">
                    <h3>📝 Conversation History:</h3>
                    {get_conversation_html()}
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Error</h1>
            <p>Sorry, there was an error: {str(e)}</p>
            <a href="/">Go back</a>
        </body>
        </html>
        """

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "message": "Simple bot is running"}

if __name__ == "__main__":
    print("🤖 Starting Ultra-Simple Digital Rights Bot...")
    print("🔗 Open your browser and go to: http://localhost:8003")
    print("📝 No JavaScript needed - pure HTML forms!")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8003)