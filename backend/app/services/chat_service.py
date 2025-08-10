import uuid
from typing import Dict, List, Optional
from datetime import datetime
import json
from .llm_service import get_llm_service, ChatMessage

class ConversationStore:
    """In-memory conversation store (replace with database in production)"""
    
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def create_conversation(self) -> str:
        """Create a new conversation and return ID."""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        """Add a message to a conversation."""
        if conversation_id not in self.conversations:
            return False
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self.conversations[conversation_id].append(message)
        return True
    
    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        """Get all messages in a conversation."""
        return self.conversations.get(conversation_id, [])
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get conversation summary."""
        messages = self.get_conversation(conversation_id)
        return {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "created_at": messages[0].timestamp if messages else None,
            "last_message": messages[-1].timestamp if messages else None
        }

class ChatService:
    def __init__(self):
        self.conversation_store = ConversationStore()
        self.llm_service = get_llm_service()
        self.analysis_context: Dict[str, Dict] = {}
    
    def start_conversation(self, analysis_context: Dict = None) -> str:
        """Start a new conversation with optional analysis context."""
        conversation_id = self.conversation_store.create_conversation()
        
        if analysis_context:
            self.analysis_context[conversation_id] = analysis_context
            
        # Add welcome message
        welcome_msg = "Hello! I'm here to help you analyze your requirements and design documents. Feel free to ask questions about the analysis, gaps, or recommendations."
        self.conversation_store.add_message(conversation_id, "assistant", welcome_msg)
        
        return conversation_id
    
    def send_message(self, conversation_id: str, message: str) -> Dict:
        """Send a message and get response."""
        if conversation_id not in self.conversation_store.conversations:
            raise ValueError("Invalid conversation ID")
        
        # Add user message
        self.conversation_store.add_message(conversation_id, "user", message)
        
        # Get conversation history
        history = self.conversation_store.get_conversation(conversation_id)
        
        # Get analysis context if available
        context = self.analysis_context.get(conversation_id)
        
        # Generate response
        try:
            response = self.llm_service.chat_conversation(
                message=message,
                conversation_history=history[:-1],  # Exclude current message
                context=context
            )
            
            # Add assistant response
            self.conversation_store.add_message(conversation_id, "assistant", response)
            
            return {
                "response": response,
                "conversation_id": conversation_id,
                "message_count": len(history) + 1
            }
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.conversation_store.add_message(conversation_id, "assistant", error_msg)
            return {
                "response": error_msg,
                "conversation_id": conversation_id,
                "message_count": len(history) + 1
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get formatted conversation history."""
        messages = self.conversation_store.get_conversation(conversation_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
    
    def get_conversations_list(self) -> List[Dict]:
        """Get list of all conversations."""
        conversations = []
        for conv_id in self.conversation_store.conversations.keys():
            summary = self.conversation_store.get_conversation_summary(conv_id)
            conversations.append(summary)
        return conversations

# Global instance
chat_service = ChatService()

def get_chat_service():
    return chat_service
