import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class CodingAIAgent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history = []
    
    def analyze_code(self, code, analysis_type="general"):
        """Analyze code for bugs, security, or performance issues"""
        prompt = f"Analyze this code for {analysis_type} issues:\n\n{code}"
        return self._send_message(prompt)
    
    def debug_error(self, error):
        """Debug an error and provide root cause analysis"""
        prompt = f"Debug this error and provide root cause analysis:\n\n{error}"
        return self._send_message(prompt)
    
    def solve_algorithm(self, problem):
        """Solve an algorithm problem"""
        prompt = f"Solve this algorithm problem:\n\n{problem}"
        return self._send_message(prompt)
    
    def review_code(self, code):
        """Review code for quality and optimization"""
        prompt = f"Review this code for quality and optimization:\n\n{code}"
        return self._send_message(prompt)
    
    def chat(self, message):
        """General coding assistance via chat"""
        return self._send_message(message)
    
    def _send_message(self, user_message):
        """Send message to Claude and maintain conversation history"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def run_cli(self):
        """Run interactive CLI"""
        print("🤖 Coding AI Agent (Claude)")
        print("Commands: analyze, debug, solve, review, chat, exit\n")
        
        while True:
            command = input("CodingAIAgent> ").strip().lower()
            
            if command == "exit":
                print("Goodbye!")
                break
            elif command == "analyze":
                code = input("Enter code to analyze: ")
                analysis_type = input("Analysis type (bug/security/performance/general): ")
                result = self.analyze_code(code, analysis_type)
                print(f"\n{result}\n")
            elif command == "debug":
                error = input("Enter error message: ")
                result = self.debug_error(error)
                print(f"\n{result}\n")
            elif command == "solve":
                problem = input("Enter algorithm problem: ")
                result = self.solve_algorithm(problem)
                print(f"\n{result}\n")
            elif command == "review":
                code = input("Enter code to review: ")
                result = self.review_code(code)
                print(f"\n{result}\n")
            elif command == "chat":
                message = input("Enter your question: ")
                result = self.chat(message)
                print(f"\n{result}\n")
            else:
                print("Unknown command. Try: analyze, debug, solve, review, chat, exit\n")

if __name__ == "__main__":
    agent = CodingAIAgent()
    agent.run_cli()
