// State Management
let conversationHistory = [];
let currentPlanId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    autoResizeTextarea();
});

// New Chat
function newChat() {
    conversationHistory = [];
    currentPlanId = null;
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('userInput').value = '';
    document.getElementById('deadlineInput').value = '';
    document.getElementById('constraintsInput').value = '';
}

// Set Prompt from Example
function setPrompt(text) {
    document.getElementById('userInput').value = text;
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('userInput').focus();
}

// Toggle Optional Inputs
function toggleOptions() {
    const optionalInputs = document.getElementById('optionalInputs');
    const toggleText = document.getElementById('optionsToggleText');
    
    if (optionalInputs.style.display === 'none') {
        optionalInputs.style.display = 'flex';
        toggleText.textContent = '- Hide deadline & constraints';
    } else {
        optionalInputs.style.display = 'none';
        toggleText.textContent = '+ Add deadline & constraints';
    }
}

// Handle Enter Key
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage(event);
    }
}

// Auto-resize Textarea
function autoResizeTextarea() {
    const textarea = document.getElementById('userInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
}

// Send Message
async function sendMessage(event) {
    event.preventDefault();
    
    const userInput = document.getElementById('userInput');
    const goal = userInput.value.trim();
    
    if (!goal) return;
    
    // Get optional inputs
    const deadline = document.getElementById('deadlineInput').value.trim() || null;
    const constraintsInput = document.getElementById('constraintsInput').value.trim();
    const constraints = constraintsInput ? constraintsInput.split(',').map(c => c.trim()) : null;
    
    // Hide welcome screen
    document.getElementById('welcomeScreen').style.display = 'none';
    
    // Add user message
    addMessage('user', goal);
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    // Show loading
    addLoadingMessage();
    
    try {
        // Call Python backend
        const response = await fetch('http://localhost:5000/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goal: goal,
                deadline: deadline,
                constraints: constraints
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate plan');
        }
        
        const plan = await response.json();
        
        // Remove loading message
        removeLoadingMessage();
        
        // Display plan
        displayPlan(plan);
        
        // Save to history
        saveToHistory(goal, plan);
        
    } catch (error) {
        removeLoadingMessage();
        addMessage('assistant', `Error: ${error.message}. Make sure the backend server is running.`, true);
    } finally {
        sendBtn.disabled = false;
    }
}

// Add Message to Chat
function addMessage(role, content, isError = false) {
    const messagesDiv = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const avatarEmoji = role === 'user' ? '👤' : '🤖';
    const roleName = role === 'user' ? 'You' : 'Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar ${role}">${avatarEmoji}</div>
            <div class="role">${roleName}</div>
        </div>
        <div class="message-content ${isError ? 'error-message' : ''}">
            ${content}
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// Add Loading Message
function addLoadingMessage() {
    const messagesDiv = document.getElementById('messages');
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message loading-message';
    loadingDiv.id = 'loadingMessage';
    
    loadingDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar assistant">🤖</div>
            <div class="role">Assistant</div>
        </div>
        <div class="loading">
            <span>Generating plan with Ollama</span>
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    
    messagesDiv.appendChild(loadingDiv);
    scrollToBottom();
}

// Remove Loading Message
function removeLoadingMessage() {
    const loadingMsg = document.getElementById('loadingMessage');
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Display Plan
function displayPlan(plan) {
    if (plan.error) {
        addMessage('assistant', `Error: ${plan.error}\nDetails: ${plan.details || 'N/A'}`, true);
        return;
    }
    
    const messagesDiv = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const planHTML = generatePlanHTML(plan);
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar assistant">🤖</div>
            <div class="role">Assistant</div>
        </div>
        <div class="message-content">
            ${planHTML}
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// Generate Plan HTML
function generatePlanHTML(plan) {
    const meta = plan.meta || {};
    const hasCycle = meta.hasCycle ? '<div style="color: var(--warning); margin-bottom: 12px;">⚠️ Warning: Dependency cycle detected!</div>' : '';
    
    let html = `
        <div class="plan-output">
            ${hasCycle}
            <div class="plan-header">
                <div class="plan-title">📋 ${meta.goal || 'Task Plan'}</div>
                <div class="plan-meta">
                    ${meta.deadline ? `<div class="meta-item">⏰ Deadline: ${meta.deadline}</div>` : ''}
                    <div class="meta-item">🤖 Model: ${meta.model || 'N/A'}</div>
                    <div class="meta-item">📅 ${new Date(meta.generatedAt).toLocaleString()}</div>
                </div>
            </div>
    `;
    
    // Tasks
    if (plan.tasks && plan.tasks.length > 0) {
        html += `
            <div class="tasks-section">
                <div class="section-title">📝 Tasks (${plan.tasks.length})</div>
        `;
        
        plan.tasks.forEach(task => {
            html += `
                <div class="task-card">
                    <div class="task-header">
                        <div class="task-id">${task.id}</div>
                        <div class="task-title">${task.title}</div>
                        <div class="task-estimate">
                            ⏱️ ${task.estimateDays || 'N/A'} days
                        </div>
                    </div>
                    <div class="task-description">${task.description || 'No description provided'}</div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // Dependencies
    if (plan.dependencies && plan.dependencies.length > 0) {
        html += `
            <div class="dependencies-section">
                <div class="section-title">🔗 Dependencies (${plan.dependencies.length})</div>
                <div class="dependency-graph">
        `;
        
        plan.dependencies.forEach(dep => {
            html += `<div class="dependency-item">${dep.from} → ${dep.to}</div>`;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Assumptions
    if (plan.assumptions && plan.assumptions.length > 0) {
        html += `
            <div class="list-section">
                <div class="section-title">💭 Assumptions</div>
        `;
        
        plan.assumptions.forEach(assumption => {
            html += `<div class="list-item">• ${assumption}</div>`;
        });
        
        html += `</div>`;
    }
    
    // Risks
    if (plan.risks && plan.risks.length > 0) {
        html += `
            <div class="list-section">
                <div class="section-title">⚠️ Risks</div>
        `;
        
        plan.risks.forEach(risk => {
            const severity = risk.severity || 'medium';
            html += `
                <div class="list-item risk-item ${severity}">
                    <div>
                        <span class="risk-severity ${severity}">${severity}</span>
                        <strong>${risk.title}</strong>
                        ${risk.mitigation ? `<div style="margin-top: 8px; color: var(--text-muted);">Mitigation: ${risk.mitigation}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // Reasoning
    if (plan.reasoning) {
        html += `
            <div class="section-title">💡 Reasoning</div>
            <div class="reasoning-section">${plan.reasoning}</div>
        `;
    }
    
    html += `</div>`;
    
    return html;
}

// Scroll to Bottom
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

// Save to History
function saveToHistory(goal, plan) {
    const historyItem = {
        id: Date.now(),
        goal: goal,
        plan: plan,
        timestamp: new Date().toISOString()
    };
    
    // Load existing history
    let history = JSON.parse(localStorage.getItem('planHistory') || '[]');
    
    // Add new item at the beginning
    history.unshift(historyItem);
    
    // Keep only last 10 items
    history = history.slice(0, 10);
    
    // Save back
    localStorage.setItem('planHistory', JSON.stringify(history));
    
    // Reload history display
    loadHistory();
}

// Load History
function loadHistory() {
    const history = JSON.parse(localStorage.getItem('planHistory') || '[]');
    const historyList = document.getElementById('historyList');
    
    if (history.length === 0) {
        historyList.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; padding: 12px;">No history yet</div>';
        return;
    }
    
    historyList.innerHTML = '';
    
    history.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.textContent = item.goal;
        historyItem.title = item.goal;
        historyItem.onclick = () => loadHistoryItem(item);
        historyList.appendChild(historyItem);
    });
}

// Load History Item
function loadHistoryItem(item) {
    newChat();
    addMessage('user', item.goal);
    displayPlan(item.plan);
}
