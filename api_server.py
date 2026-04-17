import os
from flask import Flask, request, jsonify
from main import CodingAIAgent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
agent = CodingAIAgent()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Coding AI Agent is running"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get('code', '')
    analysis_type = data.get('analysis_type', 'general')
    result = agent.analyze_code(code, analysis_type)
    return jsonify({"result": result}), 200

@app.route('/api/debug', methods=['POST'])
def debug():
    data = request.json
    error = data.get('error', '')
    result = agent.debug_error(error)
    return jsonify({"result": result}), 200

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.json
    problem = data.get('problem', '')
    result = agent.solve_algorithm(problem)
    return jsonify({"result": result}), 200

@app.route('/api/review', methods=['POST'])
def review():
    data = request.json
    code = data.get('code', '')
    result = agent.review_code(code)
    return jsonify({"result": result}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    result = agent.chat(message)
    return jsonify({"result": result}), 200

@app.route('/api/reset', methods=['POST'])
def reset():
    agent.reset_conversation()
    return jsonify({"message": "Conversation reset"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
