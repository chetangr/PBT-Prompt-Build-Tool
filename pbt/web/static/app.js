// PBT Studio - Interactive Web UI

// Global state
let currentComparison = null;
let variableCount = 0;
let ws = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    setupEventListeners();
    loadSavedState();
    initWebSocket();
});

// Setup event listeners
function setupEventListeners() {
    // Temperature slider
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    temperatureSlider.addEventListener('input', (e) => {
        temperatureValue.textContent = e.target.value;
    });

    // Auto-detect variables in prompt
    const promptInput = document.getElementById('prompt-input');
    promptInput.addEventListener('input', detectVariables);

    // Save state on change
    promptInput.addEventListener('change', saveState);
    document.getElementById('expected-output').addEventListener('change', saveState);
}

// Load available models from API
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        const modelSelector = document.querySelector('.model-selector');
        modelSelector.innerHTML = '';
        
        data.models.forEach(model => {
            const label = document.createElement('label');
            label.className = 'model-checkbox';
            label.innerHTML = `
                <input type="checkbox" value="${model.id}" ${['claude', 'gpt-4', 'gpt-3.5-turbo'].includes(model.id) ? 'checked' : ''}>
                <span>${model.name}</span>
            `;
            modelSelector.appendChild(label);
        });
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

// Detect variables in prompt template
function detectVariables() {
    const prompt = document.getElementById('prompt-input').value;
    const variablePattern = /\{\{(\w+)\}\}/g;
    const detectedVars = new Set();
    
    let match;
    while ((match = variablePattern.exec(prompt)) !== null) {
        detectedVars.add(match[1]);
    }
    
    // Get current variables
    const currentVars = new Set();
    document.querySelectorAll('.variable-item input[type="text"]').forEach(input => {
        currentVars.add(input.value);
    });
    
    // Add new detected variables
    detectedVars.forEach(varName => {
        if (!currentVars.has(varName)) {
            addVariable(varName);
        }
    });
}

// Add a variable input
function addVariable(name = '') {
    const container = document.getElementById('variables-container');
    const variableId = `var-${variableCount++}`;
    
    const variableItem = document.createElement('div');
    variableItem.className = 'variable-item';
    variableItem.id = variableId;
    variableItem.innerHTML = `
        <input type="text" placeholder="Variable name" value="${name}" ${name ? 'readonly' : ''}>
        <input type="text" placeholder="Variable value">
        <button onclick="removeVariable('${variableId}')" title="Remove variable">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(variableItem);
}

// Remove a variable
function removeVariable(id) {
    document.getElementById(id).remove();
}

// Compare models
async function compareModels() {
    // Get input values
    const prompt = document.getElementById('prompt-input').value;
    const expectedOutput = document.getElementById('expected-output').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('max-tokens').value);
    
    // Get selected models
    const selectedModels = [];
    document.querySelectorAll('.model-checkbox input:checked').forEach(checkbox => {
        selectedModels.push(checkbox.value);
    });
    
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }
    
    if (selectedModels.length === 0) {
        alert('Please select at least one model');
        return;
    }
    
    // Get variables
    const variables = {};
    document.querySelectorAll('.variable-item').forEach(item => {
        const inputs = item.querySelectorAll('input[type="text"]');
        if (inputs[0].value && inputs[1].value) {
            variables[inputs[0].value] = inputs[1].value;
        }
    });
    
    // Show loading state
    showLoadingState(selectedModels);
    
    try {
        // Use WebSocket for streaming if connected
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                prompt,
                models: selectedModels,
                variables,
                expected_output: expectedOutput,
                temperature,
                max_tokens: maxTokens
            }));
        } else {
            // Fallback to REST API
            const response = await fetch('/api/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt,
                    models: selectedModels,
                    variables,
                    expected_output: expectedOutput,
                    temperature,
                    max_tokens: maxTokens
                })
            });
            
            const data = await response.json();
            displayResults(data);
        }
    } catch (error) {
        console.error('Comparison failed:', error);
        alert('Failed to compare models. Please try again.');
        hideLoadingState();
    }
}

// Show loading state
function showLoadingState(models) {
    document.getElementById('loading-state').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('metrics-summary').style.display = 'none';
    document.getElementById('recommendations').style.display = 'none';
    document.getElementById('result-actions').style.display = 'none';
    
    // Show progress for each model
    const progressDiv = document.getElementById('loading-progress');
    progressDiv.innerHTML = models.map(model => 
        `<div id="progress-${model}">⏳ ${model}: Waiting...</div>`
    ).join('');
}

// Hide loading state
function hideLoadingState() {
    document.getElementById('loading-state').style.display = 'none';
}

// Display comparison results
function displayResults(data) {
    currentComparison = data;
    hideLoadingState();
    
    // Show result actions
    document.getElementById('result-actions').style.display = 'flex';
    
    // Display model responses
    const container = document.getElementById('results-container');
    container.innerHTML = '<div class="model-results"></div>';
    const modelResults = container.querySelector('.model-results');
    
    data.models.forEach(model => {
        const scoreClass = model.score >= 8 ? 'score-high' : 
                          model.score >= 6 ? 'score-medium' : 'score-low';
        
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card';
        modelCard.innerHTML = `
            <div class="model-card-header">
                <div>
                    <span class="model-name">${model.model}</span>
                    ${model.score ? `<span class="score-badge ${scoreClass}">${model.score.toFixed(1)}/10</span>` : ''}
                </div>
                <div class="model-stats">
                    <span class="stat-item"><i class="fas fa-clock"></i> ${model.response_time.toFixed(2)}s</span>
                    <span class="stat-item"><i class="fas fa-coins"></i> $${model.cost.toFixed(4)}</span>
                    <span class="stat-item"><i class="fas fa-file-alt"></i> ${model.tokens} tokens</span>
                </div>
            </div>
            <div class="model-card-body">
                <div class="output-text">${escapeHtml(model.output)}</div>
                ${model.evaluation ? renderEvaluation(model.evaluation) : ''}
            </div>
        `;
        modelResults.appendChild(modelCard);
    });
    
    // Display metrics summary
    displayMetricsSummary(data.models);
    
    // Display recommendations
    displayRecommendations(data.recommendations);
}

// Render evaluation details
function renderEvaluation(evaluation) {
    return `
        <div class="evaluation-details">
            <h4>Evaluation Details</h4>
            <div class="evaluation-metrics">
                ${Object.entries(evaluation).map(([key, value]) => `
                    <div class="metric-item">
                        <div class="metric-label">${formatMetricName(key)}</div>
                        <div class="metric-value">${(value * 100).toFixed(0)}%</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Display metrics summary
function displayMetricsSummary(models) {
    const metricsDiv = document.getElementById('metrics-summary');
    metricsDiv.style.display = 'block';
    
    // Calculate average metrics
    const avgResponseTime = models.reduce((sum, m) => sum + m.response_time, 0) / models.length;
    const totalCost = models.reduce((sum, m) => sum + m.cost, 0);
    const avgTokens = models.reduce((sum, m) => sum + m.tokens, 0) / models.length;
    const avgScore = models.filter(m => m.score).reduce((sum, m) => sum + m.score, 0) / 
                     models.filter(m => m.score).length || 0;
    
    const metricsGrid = metricsDiv.querySelector('.metrics-grid');
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <h4>Avg Response Time</h4>
            <div class="value">${avgResponseTime.toFixed(2)}s</div>
        </div>
        <div class="metric-card">
            <h4>Total Cost</h4>
            <div class="value">$${totalCost.toFixed(4)}</div>
        </div>
        <div class="metric-card">
            <h4>Avg Tokens</h4>
            <div class="value">${avgTokens.toFixed(0)}</div>
        </div>
        ${avgScore > 0 ? `
        <div class="metric-card">
            <h4>Avg Score</h4>
            <div class="value">${avgScore.toFixed(1)}/10</div>
        </div>
        ` : ''}
    `;
}

// Display recommendations
function displayRecommendations(recommendations) {
    const recsDiv = document.getElementById('recommendations');
    recsDiv.style.display = 'block';
    
    const recsCards = recsDiv.querySelector('.recommendation-cards');
    recsCards.innerHTML = Object.entries(recommendations).map(([category, model]) => {
        const icon = {
            'best_quality': 'fa-trophy',
            'best_speed': 'fa-bolt',
            'best_cost': 'fa-dollar-sign',
            'balanced': 'fa-balance-scale'
        }[category] || 'fa-star';
        
        const title = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        return `
            <div class="recommendation-card ${category === 'balanced' ? 'best' : ''}">
                <h4><i class="fas ${icon}"></i> ${title}</h4>
                <div class="model">${model}</div>
            </div>
        `;
    }).join('');
}

// Export results
async function exportResults(format) {
    if (!currentComparison) return;
    
    if (format === 'json') {
        const dataStr = JSON.stringify(currentComparison, null, 2);
        downloadFile('comparison.json', dataStr, 'application/json');
    } else if (format === 'markdown') {
        const markdown = generateMarkdown(currentComparison);
        downloadFile('comparison.md', markdown, 'text/markdown');
    }
}

// Generate markdown report
function generateMarkdown(data) {
    let md = `# Model Comparison Report\n\n`;
    md += `**Date**: ${new Date(data.timestamp).toLocaleString()}\n\n`;
    md += `## Prompt\n\`\`\`\n${data.prompt}\n\`\`\`\n\n`;
    
    if (Object.keys(data.variables).length > 0) {
        md += `## Variables\n`;
        Object.entries(data.variables).forEach(([key, value]) => {
            md += `- **${key}**: ${value}\n`;
        });
        md += `\n`;
    }
    
    md += `## Results\n\n`;
    data.models.forEach(model => {
        md += `### ${model.model}\n`;
        md += `- **Response Time**: ${model.response_time.toFixed(2)}s\n`;
        md += `- **Tokens**: ${model.tokens}\n`;
        md += `- **Cost**: $${model.cost.toFixed(4)}\n`;
        if (model.score) {
            md += `- **Score**: ${model.score.toFixed(1)}/10\n`;
        }
        md += `\n**Output:**\n\`\`\`\n${model.output}\n\`\`\`\n\n`;
    });
    
    md += `## Recommendations\n`;
    Object.entries(data.recommendations).forEach(([category, model]) => {
        const title = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        md += `- **${title}**: ${model}\n`;
    });
    
    return md;
}

// Download file
function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Save prompt
function savePrompt() {
    document.getElementById('save-prompt-modal').style.display = 'block';
}

// Confirm save prompt
async function confirmSavePrompt() {
    const name = document.getElementById('prompt-name').value;
    const description = document.getElementById('prompt-description').value;
    const prompt = document.getElementById('prompt-input').value;
    const expectedOutput = document.getElementById('expected-output').value;
    
    if (!name) {
        alert('Please enter a prompt name');
        return;
    }
    
    // Get variables
    const variables = {};
    document.querySelectorAll('.variable-item').forEach(item => {
        const inputs = item.querySelectorAll('input[type="text"]');
        if (inputs[0].value && inputs[1].value) {
            variables[inputs[0].value] = inputs[1].value;
        }
    });
    
    // Get selected models
    const models = [];
    document.querySelectorAll('.model-checkbox input:checked').forEach(checkbox => {
        models.push(checkbox.value);
    });
    
    try {
        const response = await fetch('/api/prompts/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                description,
                prompt,
                variables,
                models,
                expected_output: expectedOutput
            })
        });
        
        if (response.ok) {
            closeModal('save-prompt-modal');
            alert('Prompt saved successfully!');
        } else {
            const error = await response.json();
            alert(`Failed to save prompt: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Failed to save prompt:', error);
        alert(`Failed to save prompt: ${error.message}`);
    }
}

// Show saved prompts
async function showSavedPrompts() {
    try {
        const response = await fetch('/api/prompts');
        const data = await response.json();
        
        // TODO: Display saved prompts in a modal
        console.log('Saved prompts:', data.prompts);
        alert('Saved prompts feature coming soon!');
    } catch (error) {
        console.error('Failed to load saved prompts:', error);
    }
}

// Show history
async function showHistory() {
    try {
        const response = await fetch('/api/history?limit=20');
        const data = await response.json();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        data.history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.onclick = () => loadHistoryItem(item);
            historyItem.innerHTML = `
                <div class="history-meta">
                    <span>${new Date(item.timestamp).toLocaleString()}</span>
                    <span>${item.models.length} models</span>
                </div>
                <div class="history-prompt">${item.prompt}</div>
            `;
            historyList.appendChild(historyItem);
        });
        
        document.getElementById('history-modal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Load history item
function loadHistoryItem(item) {
    closeModal('history-modal');
    displayResults(item);
}

// Show settings
function showSettings() {
    alert('Settings feature coming soon!');
}

// Load example
function loadExample() {
    document.getElementById('prompt-input').value = `Summarize the following text in {{num_sentences}} sentences:

{{text}}

Focus on the key points and maintain the original tone.`;
    
    // Add example variables
    document.getElementById('variables-container').innerHTML = '';
    addVariable('num_sentences');
    addVariable('text');
    
    // Set example values
    setTimeout(() => {
        const inputs = document.querySelectorAll('.variable-item input[type="text"]');
        inputs[1].value = '3';
        inputs[3].value = 'Artificial intelligence is rapidly transforming industries worldwide. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions that were previously impossible. This technological revolution is creating new opportunities while also raising important questions about privacy, employment, and the future of human-machine interaction.';
    }, 100);
    
    document.getElementById('expected-output').value = 'Artificial intelligence and machine learning are revolutionizing industries by processing large datasets to identify patterns and make unprecedented predictions. This transformation brings significant opportunities but also raises concerns about privacy, job displacement, and human-machine relationships. The rapid advancement of AI technology is fundamentally changing how businesses operate and society functions.';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Save state to localStorage
function saveState() {
    const state = {
        prompt: document.getElementById('prompt-input').value,
        expectedOutput: document.getElementById('expected-output').value,
        temperature: document.getElementById('temperature').value,
        maxTokens: document.getElementById('max-tokens').value
    };
    localStorage.setItem('pbt-studio-state', JSON.stringify(state));
}

// Load saved state
function loadSavedState() {
    const savedState = localStorage.getItem('pbt-studio-state');
    if (savedState) {
        const state = JSON.parse(savedState);
        document.getElementById('prompt-input').value = state.prompt || '';
        document.getElementById('expected-output').value = state.expectedOutput || '';
        document.getElementById('temperature').value = state.temperature || '0.7';
        document.getElementById('max-tokens').value = state.maxTokens || '1000';
        document.getElementById('temperature-value').textContent = state.temperature || '0.7';
        
        // Detect variables
        detectVariables();
    }
}

// Initialize WebSocket connection
function initWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws`;
    ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'model_start') {
            const progressDiv = document.getElementById(`progress-${data.model}`);
            if (progressDiv) {
                progressDiv.innerHTML = `⏳ ${data.model}: Processing...`;
            }
        } else if (data.type === 'model_complete') {
            const progressDiv = document.getElementById(`progress-${data.model}`);
            if (progressDiv) {
                progressDiv.innerHTML = `✅ ${data.model}: Complete`;
            }
            
            // Update results incrementally
            if (!currentComparison) {
                currentComparison = {
                    models: [],
                    timestamp: new Date().toISOString()
                };
            }
            currentComparison.models.push(data.response);
            
            // Re-render results
            displayResults(currentComparison);
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMetricName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}