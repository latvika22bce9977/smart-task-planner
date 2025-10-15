"""
Flask API server for Smart Task Planner frontend
Connects the web UI to the Ollama-based planner
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from planner import TaskPlanner
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for frontend requests

# Initialize planner
planner = TaskPlanner(model="llama3:latest")


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)"""
    return send_from_directory('.', path)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "model": planner.model
    })


@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    """Generate a task plan from user input"""
    try:
        data = request.json
        
        # Extract parameters
        goal = data.get('goal')
        deadline = data.get('deadline')
        constraints = data.get('constraints')
        
        if not goal:
            return jsonify({
                "error": "Goal is required",
                "details": "Please provide a goal"
            }), 400
        
        # Generate plan
        plan = planner.generate_plan(
            goal=goal,
            deadline=deadline,
            constraints=constraints
        )
        
        return jsonify(plan)
        
    except Exception as e:
        return jsonify({
            "error": "Failed to generate plan",
            "details": str(e)
        }), 500


@app.route('/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    try:
        import subprocess
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            
            return jsonify({
                "models": models,
                "current": planner.model
            })
        else:
            return jsonify({
                "error": "Failed to list models",
                "details": result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": "Failed to list models",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SMART TASK PLANNER - SERVER STARTING")
    print("=" * 60)
    print(f"\n✅ Server URL: http://localhost:5000")
    print(f"🤖 LLM Model: {planner.model}")
    print(f"\n💡 Open your browser and go to: http://localhost:5000")
    print(f"\n⚠️  Press Ctrl+C to stop the server\n")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
