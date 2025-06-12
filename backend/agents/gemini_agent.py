import google.generativeai as genai
from datetime import datetime
from typing import Optional

class GeminiAgent:
    def __init__(self, api_key: str, name: str, personality: str):
        """Initialize a Gemini agent with a specific personality."""
        self.name = name
        self.personality = personality
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        
    async def generate_response(self, message: str) -> str:
        """Generate a response to the given message."""
        try:
            # Create a prompt that includes the agent's personality
            prompt = f"""
            You are {self.name}, an AI agent with the following personality: {self.personality}
            Respond to this message in a conversational way, staying in character:
            Message: {message}
            
            Keep your response concise (2-3 sentences max).
            """
            
            response = await self.chat.send_message_async(prompt)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "agent": self.name,
                "message": response.text,
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "agent": self.name,
                "message": f"Error generating response: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_name(self) -> str:
        """Return the agent's name."""
        return self.name 