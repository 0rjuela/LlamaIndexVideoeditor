from llama_index.core import AgentRunner
from utils.math_utils import extract_math_concepts

class ResearchAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4")
        
    def identify_problem(self, query: str) -> dict:
        """Extracts core math concepts from user input"""
        concepts = extract_math_concepts(query)
        return {
            "problem": query,
            "concepts": "linear algebra",  # e.g. ["linear algebra", "matrix inversion"]
            "difficulty": "intermediate"
        }