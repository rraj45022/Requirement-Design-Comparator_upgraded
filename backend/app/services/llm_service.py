import os
from typing import List, Dict, Optional
from openai import OpenAI
from pydantic import BaseModel
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the project root directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not found")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
    def generate_improved_feedback(self, 
                                 parsed_requirements: List[str], 
                                 parsed_design: List[str], 
                                 semantic_analysis: List[Dict]) -> str:
        """Generate improved feedback using LLM with structured semantic analysis."""
        
        # Calculate summary statistics
        total_requirements = len(parsed_requirements)
        total_design_items = len(parsed_design)
        covered_requirements = sum(1 for r in semantic_analysis if r["coverage"] == "Present")
        missing_requirements = sum(1 for r in semantic_analysis if r["coverage"] == "Missing")
        
        # Build detailed analysis
        detailed_analysis = []
        for item in semantic_analysis:
            req_analysis = {
                "requirement": item["requirement"],
                "status": item["coverage"],
                "similarity_score": item["similarity_score"],
                "matched_design_items": item.get("matched_design_items", []),
                "issue": item.get("issue", "")
            }
            detailed_analysis.append(req_analysis)
        
        prompt = f"""
        You are an expert software architect analyzing the alignment between requirements and design documents.
        
        SUMMARY:
        - Total Requirements: {total_requirements}
        - Total Design Items: {total_design_items}
        - Requirements Covered: {covered_requirements}
        - Requirements Missing: {missing_requirements}
        - Coverage Percentage: {(covered_requirements/total_requirements)*100:.1f}% if total_requirements > 0 else 0
        
        PARSED REQUIREMENTS:
        {json.dumps(parsed_requirements, indent=2)}
        
        PARSED DESIGN ELEMENTS:
        {json.dumps(parsed_design, indent=2)}
        
        SEMANTIC ANALYSIS RESULTS:
        {json.dumps(detailed_analysis, indent=2)}
        
        Based on the semantic analysis above, provide:
        
        1. **Executive Summary**: Brief overview of the alignment quality
        2. **Detailed Gap Analysis**: Specific requirements that are missing or poorly addressed in the design
        3. **Design Coverage**: Which design elements effectively address which requirements
        4. **Priority Recommendations**: 
           - High priority: Critical missing requirements
           - Medium priority: Requirements with partial coverage
           - Low priority: Minor gaps or improvements
        5. **Actionable Next Steps**: Specific recommendations for design improvements
        
        Format your response in a clear, structured way with actionable insights. Use markdown formatting for better readability.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a software architecture expert specializing in requirements analysis and design validation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating feedback: {str(e)}"
    
    def chat_conversation(self, 
                         message: str, 
                         conversation_history: List[ChatMessage],
                         context: Dict = None) -> str:
        """Handle conversational chat with context."""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant for software requirements and design analysis. You have access to the current analysis context and can answer questions about requirements, design, and recommendations."}
        ]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add context if provided
        if context:
            context_str = f"\nCurrent Analysis Context: {json.dumps(context, indent=2)}"
            message = message + context_str
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error in chat: {str(e)}"

# Global instance
llm_service = None

def get_llm_service():
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
