# 🚀 Smart Task Planner

AI-powered task planning tool with a beautiful ChatGPT-like interface. Breaks down goals into actionable tasks with timelines using local Ollama LLM.

## ✨ Features

- 💬 **ChatGPT-like Web Interface** - Beautiful, modern dark theme UI
- 🤖 **Local Ollama Integration** - Completely offline, no API keys needed
- 📋 **Smart Task Breakdown** - Detailed tasks with time estimates
- 🔗 **Dependency Mapping** - Automatic task relationship detection
- ⚠️ **Risk Assessment** - Identifies potential issues and mitigations
- 💾 **Plan History** - Saves recent plans in browser
- 🎨 **Responsive Design** - Works on desktop and mobile

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running
3. At least one Ollama model pulled (e.g., `llama3`)

### Install Ollama

**Windows:** Download from [ollama.com](https://ollama.com/download)

**Pull a model:**
```bash
ollama pull llama3
```

Check available models:
```bash
ollama list
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python server.py
```

You'll see:
```
🚀 Starting Smart Task Planner API Server
📍 Server: http://localhost:5000
🤖 Model: llama3:latest
```

### 3. Open Your Browser

Go to: **http://localhost:5000**

That's it! 🎉

## 💡 How to Use

1. **Enter your goal** in the chat input
   - Example: "Launch a product in 2 weeks"
   
2. **Optional:** Click "+ Add deadline & constraints"
   - Deadline: "2 weeks" or "2025-12-31"
   - Constraints: "team of 2, limited budget"

3. **Click Send** and wait for Ollama to generate your plan

4. **Review your plan:**
   - ✅ Tasks with time estimates
   - 🔗 Task dependencies
   - 💭 Assumptions
   - ⚠️ Risks and mitigations
   - 💡 Reasoning

## 🎨 Example Prompts

Try these in the interface:

- "Launch a product in 2 weeks"
- "Organize a conference for 200 people in 3 months"
- "Learn Python and build a web app in 6 months"
- "Plan a marketing campaign with $10k budget"

## 📁 Project Structure

```
lalith/
├── planner.py          # Ollama integration & planning logic
├── server.py           # Flask API server
├── index.html          # Web interface
├── styles.css          # Beautiful dark theme
├── script.js           # Frontend logic
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚙️ Configuration

Edit `server.py` to change the model:

```python
planner = TaskPlanner(model="llama3:latest", temperature=0.3)
```

## 🐛 Troubleshooting

### "Model not found" error
```bash
ollama pull llama3
ollama list
```

### Port 5000 already in use
Edit `server.py` and change the port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Can't connect to server
- Make sure server is running
- Go to http://localhost:5000
- Check browser console (F12) for errors

## 🎯 Use Cases

- Product Launches
- Event Planning
- Learning Goals
- Project Management
- Personal Planning

## 📄 License

MIT

---

**Made with ❤️ using Ollama**
