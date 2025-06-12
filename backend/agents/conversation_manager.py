from typing import Dict, List, Optional
from .gemini_agent import GeminiAgent
import asyncio
from datetime import datetime
import json

class ConversationManager:
    def __init__(self, max_turns: int = 10):
        """Initialize the conversation manager."""
        self.agents: Dict[str, GeminiAgent] = {}
        self.conversation_history: List[dict] = []
        self.max_turns = max_turns
        self.current_turn = 0
        self.active_conversation = False
        
    def add_agent(self, agent: GeminiAgent):
        """Add an agent to the conversation."""
        self.agents[agent.get_name()] = agent
        
    def get_conversation_history(self) -> List[dict]:
        """Get the conversation history."""
        return self.conversation_history
    
    async def start_conversation(self, initial_prompt: str):
        """Start a new conversation between agents."""
        if len(self.agents) < 2:
            raise ValueError("Need at least 2 agents for a conversation")
            
        self.active_conversation = True
        self.current_turn = 0
        self.conversation_history = []
        
        # Get the agents as a list for easy turn management
        agent_list = list(self.agents.values())
        current_message = initial_prompt
        
        while self.active_conversation and self.current_turn < self.max_turns:
            current_agent = agent_list[self.current_turn % 2]
            
            # Generate response from current agent
            response = await current_agent.generate_response(current_message)
            
            # Add to conversation history
            self.conversation_history.append(response)
            
            # Update for next turn
            current_message = response["message"]
            self.current_turn += 1
            
            # Yield the response for WebSocket transmission
            yield response
            
            # Add a small delay to make the conversation more natural
            await asyncio.sleep(1)
            
        self.active_conversation = False
        
    def stop_conversation(self):
        """Stop the current conversation."""
        self.active_conversation = False
        
    def export_conversation(self) -> str:
        """Export the conversation history as a formatted string."""
        output = []
        for message in self.conversation_history:
            output.append(
                f"[{message['timestamp']}] {message['agent']}: {message['message']}"
            )
        return "\n".join(output) 