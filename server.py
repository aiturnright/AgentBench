"""Simple Flask web server to display AgentBench results."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def load_results(file_path: str) -> dict[str, Any]:
    """Load results from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            return {}


@app.route("/")
def index():
    """Display available result files and default view."""
    # 默认结果文件
    default_file = "results/text_generation_results.json"
    selected_file = request.args.get("file", default_file)
    
    # 获取所有结果文件
    results_dir = "results"
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
    else:
        result_files = []
    
    # 加载所选文件的结果
    results = load_results(selected_file)
    
    return render_template(
        "index.html",
        selected_file=selected_file,
        result_files=result_files,
        results=results
    )


@app.route("/api/results")
def api_results():
    """API endpoint to retrieve results data."""
    selected_file = request.args.get("file", "results/text_generation_results.json")
    results = load_results(selected_file)
    return jsonify(results)


@app.route("/api/models")
def api_models():
    """API endpoint to retrieve model names and their scores."""
    selected_file = request.args.get("file", "results/text_generation_results.json")
    results = load_results(selected_file)
    
    if "models" not in results:
        return jsonify({"models": []})
    
    model_data = []
    for model_name, model_info in results["models"].items():
        avg_score = model_info.get("average_score", 0)
        task_count = len(model_info.get("results", []))
        
        model_data.append({
            "name": model_name,
            "average_score": avg_score,
            "task_count": task_count
        })
    
    return jsonify({"models": model_data})


@app.route("/api/tasks/<path:model_name>")
def api_model_tasks(model_name):
    """API endpoint to retrieve tasks for a specific model (supporting slashes in model name)."""
    selected_file = request.args.get("file", "results/text_generation_results.json")
    results = load_results(selected_file)
    
    # 解码URL编码的模型名称
    try:
        import urllib.parse
        model_name = urllib.parse.unquote(model_name)
    except:
        pass
    
    if "models" not in results or model_name not in results["models"]:
        print(f"Model {model_name} not found in results")
        print(f"Available models: {list(results.get('models', {}).keys())}")
        return jsonify({"tasks": []})
    
    tasks = []
    for task in results["models"][model_name]["results"]:
        tasks.append({
            "task_id": task.get("task_id", ""),
            "score": task.get("score", 0),
            "comment": task.get("comment", ""),
            "model_output": task.get("model_output", "")
        })
    
    print(f"Found {len(tasks)} tasks for model {model_name}")
    return jsonify({"tasks": tasks})


if __name__ == "__main__":
    # 确保templates目录存在
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    # 确保results目录存在
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # 创建默认模板
    template_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentBench 评估结果展示</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header Styles */
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        /* File Selection */
        .file-selector {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .file-selector select {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            background: white;
            cursor: pointer;
        }
        
        /* Models Overview */
        .models-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .model-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }
        
        .model-card h3 {
            color: #667eea;
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        
        .model-card .score {
            font-size: 2rem;
            font-weight: 700;
            color: #4CAF50;
            margin: 10px 0;
        }
        
        .model-card .task-count {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }
        
        .view-details {
            display: inline-block;
            padding: 8px 15px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }
        
        .view-details:hover {
            background: #5a6fd8;
        }
        
        /* Task Details */
        .task-details {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .task-details h3 {
            color: #667eea;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }
        
        .task-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .task-table th,
        .task-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .task-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .task-table tr:hover {
            background: #f8f9fa;
        }
        
        .score-cell {
            font-weight: 600;
            color: #4CAF50;
        }
        
        .score-cell.low {
            color: #f44336;
        }
        
        .score-cell.medium {
            color: #ff9800;
        }
        
        .score-cell.high {
            color: #4CAF50;
        }
        
        /* Model Output Section */
        .model-output {
            margin-top: 20px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            color: #333;
            max-height: 300px;
            overflow-y: auto;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .models-overview {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                text-align: center;
            }
            
            h1 {
                font-size: 1.5rem;
            }
        }
        
        /* Loading Spinner */
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Error Message */
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #ef5350;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>AgentBench 评估结果展示</h1>
            <p>AI 模型文本生成能力评估系统</p>
        </div>
    </header>
    
    <div class="container">
        <!-- File Selector -->
        <div class="file-selector">
            <label for="resultFile">选择结果文件：</label>
            <select id="resultFile" onchange="loadFile(this.value)">
                {% for file in result_files %}
                    <option value="results/{{ file }}" {% if 'results/' + file == selected_file %}selected{% endif %}>{{ file }}</option>
                {% endfor %}
            </select>
        </div>
        
        <!-- Loading Indicator -->
        <div id="loading" style="display: none;">
            <div class="spinner"></div> 加载中...
        </div>
        
        <!-- Error Message -->
        <div id="error" class="error-message" style="display: none;"></div>
        
        <!-- Models Overview -->
        <div class="models-overview" id="modelsOverview">
            {% if results and 'models' in results %}
                {% for model_name, model_info in results['models'].items() %}
                    <div class="model-card">
                        <h3>{{ model_name }}</h3>
                        <div class="score">
                            {% set avg_score = model_info.get('average_score', 0) %}
                            {{ "%.1f" % avg_score }}/10
                        </div>
                        <div class="task-count">
                            任务数：{{ model_info.get('results', []) | length }}
                        </div>
                        <a href="#" class="view-details" onclick="viewModelTasks('{{ model_name }}'); return false;">
                            查看任务详情
                        </a>
                    </div>
                {% endfor %}
            {% else %}
                <div class="error-message">
                    没有找到评估结果数据。请确保已运行评估任务。
                </div>
            {% endif %}
        </div>
        
        <!-- Task Details Container -->
        <div id="taskDetails" style="display: none;">
            <div class="task-details">
                <h3 id="taskDetailsTitle">任务详情</h3>
                <div id="taskTableContainer">
                    <table class="task-table">
                        <thead>
                            <tr>
                                <th>任务ID</th>
                                <th>得分</th>
                                <th>任务内容</th>
                            </tr>
                        </thead>
                        <tbody id="taskTableBody">
                            <!-- 任务数据将动态插入这里 -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 加载所选文件的结果
        function loadFile(filePath) {
            const url = `/?file=${encodeURIComponent(filePath)}`;
            window.location.href = url;
        }
        
        // 查看模型任务详情
        function viewModelTasks(modelName) {
            const file = document.getElementById('resultFile').value;
            const url = `/api/tasks/${encodeURIComponent(modelName)}?file=${encodeURIComponent(file)}`;
            
            showLoading();
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    displayTaskDetails(modelName, data['tasks']);
                })
                .catch(error => {
                    hideLoading();
                    showError(`加载任务数据失败: ${error}`);
                });
        }
        
        // 显示任务详情
        function displayTaskDetails(modelName, tasks) {
            const container = document.getElementById('taskDetails');
            const title = document.getElementById('taskDetailsTitle');
            const tableBody = document.getElementById('taskTableBody');
            
            title.textContent = `${modelName} - 任务详情`;
            
            tableBody.innerHTML = '';
            
            tasks.forEach(task => {
                const row = tableBody.insertRow();
                const taskIdCell = row.insertCell(0);
                const scoreCell = row.insertCell(1);
                const contentCell = row.insertCell(2);
                
                taskIdCell.textContent = task['task_id'];
                
                // 设置得分颜色
                const score = task['score'];
                let scoreClass = 'score-cell';
                if (score < 5) {
                    scoreClass += ' low';
                } else if (score < 8) {
                    scoreClass += ' medium';
                } else {
                    scoreClass += ' high';
                }
                scoreCell.textContent = score;
                scoreCell.className = scoreClass;
                
                // 显示任务内容摘要
                const content = task['model_output'];
                const summary = content.length > 200 ? content.substring(0, 200) + '...' : content;
                contentCell.textContent = summary;
            });
            
            container.style.display = 'block';
            container.scrollIntoView({ behavior: 'smooth' });
        }
        
        // 显示加载指示器
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        // 隐藏加载指示器
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        // 显示错误信息
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
    """
    
    # 确保模板目录和模板文件存在
    template_dir = "templates"
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    template_path = os.path.join(template_dir, "index.html")
    if not os.path.exists(template_path):
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content.strip())
    



if __name__ == "__main__":
    # 确保results目录存在
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # 启动Flask服务器
    print("=" * 50)
    print("AgentBench 评估结果展示服务器")
    print("=" * 50)
    print()
    print("服务器正在启动...")
    print(f"访问地址: http://localhost:5000")
    print()
    print("功能特性:")
    print("- 显示评估结果概览")
    print("- 查看模型详细评分")
    print("- 任务详情展示")
    print("- 支持多结果文件切换")
    print()
    print("按 Ctrl+C 停止服务器")
    
    # 启动服务器
    app.run(debug=True, host="0.0.0.0", port=5000)