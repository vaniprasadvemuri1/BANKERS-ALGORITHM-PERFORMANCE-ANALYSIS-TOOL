from flask import Flask, request, render_template_string, redirect
import subprocess
import os
import json
import datetime
import re

app = Flask(__name__)

HISTORY_FILE = 'history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    # Keep last 50 entries
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-50:], f, indent=2)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Banker's Algorithm Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/9.4.3/mermaid.min.js"></script>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #f0f2f5; color: #1a1a1a; }
        h1 { margin: 0 0 1.5rem 0; font-size: 1.5rem; color: #2d3748; border-bottom: 2px solid #e1e4e8; padding-bottom: 1rem; }
        .card { background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .row { display: flex; gap: 20px; }
        .col { flex: 1; }
        input[type="number"] { padding: 0.5rem; border: 1px solid #cbd5e0; border-radius: 4px; width: 80px; margin-right: 1rem; }
        button { padding: 0.5rem 1rem; border: none; border-radius: 4px; font-weight: 500; cursor: pointer; transition: all 0.2s; margin-right: 10px; }
        button:hover { opacity: 0.9; }
        .btn-primary { background: #3182ce; color: white; }
        .btn-secondary { background: #e2e8f0; color: #4a5568; }
        .btn-danger { background: #fff5f5; color: #c53030; border: 1px solid #feb2b2; }
        pre { background: #2d3748; color: #edf2f7; padding: 1rem; border-radius: 6px; overflow-x: auto; font-family: 'Menlo', 'Monaco', monospace; font-size: 0.9rem; }
        label { font-weight: 600; margin-right: 0.5rem; color: #4a5568; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        th { text-align: left; border-bottom: 2px solid #e2e8f0; padding: 0.75rem; color: #4a5568; background: #f7fafc; }
        td { border-bottom: 1px solid #e2e8f0; padding: 0.75rem; }
        .mermaid { text-align: center; }
    </style>
    <script>
        mermaid.initialize({ startOnLoad: true, securityLevel: 'loose', theme: 'default' });
    </script>
</head>
<body>
    <h1>Banker's Algorithm Performance Analysis</h1>
    <p>Real-time performance metrics from your local system.</p>
    
    <div class="card">
        <form method="get" action="/">
            <p><strong>Manual Configuration:</strong></p>
            <div>
                <label>Processes (P):</label>
                <input type="number" name="p" value="{{ p }}" min="1" required>
                
                <label>Resources (R):</label>
                <input type="number" name="r" value="{{ r }}" min="1" required>
                
                <button type="submit">Run Analysis</button>
                <a href="/"><button type="button" class="btn-secondary">Clear Current Result</button></a>
                <a href="/reset"><button type="button" class="btn-danger">Reset History</button></a>
            </div>
        </form>
    </div>

    {% if output %}
    <div class="card">
        <h3>Current Run Result</h3>
        <pre>{{ output }}</pre>
    </div>
    {% endif %}

    {% if mermaid_graph %}
    <div class="card">
        <h3>Resource Allocation Graph (Visual)</h3>
        <div class="mermaid">
            {{ mermaid_graph | safe }}
        </div>
    </div>
    {% endif %}

    <div class="row">
        <div class="col card">
            <h3>CPU Time Comparison (Seconds)</h3>
            <canvas id="cpuChart"></canvas>
        </div>
        <div class="col card">
            <h3>Memory Usage Comparison (Bytes)</h3>
            <canvas id="memChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h3>Historical Data</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Time</th>
                    <th>Processes</th>
                    <th>Resources</th>
                    <th>CPU Time (s)</th>
                    <th>Memory (Bytes)</th>
                </tr>
            </thead>
            <tbody>
                {% for item in history|reverse %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ item.timestamp }}</td>
                    <td>{{ item.p }}</td>
                    <td>{{ item.r }}</td>
                    <td>{{ "%.6f"|format(item.cpu) }}</td>
                    <td>{{ item.memory }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
        const history = {{ history | tojson | safe }};
        const labels = history.map((item, index) => `Run ${index + 1} (P=${item.p}, R=${item.r})`);
        const cpuData = history.map(item => item.cpu);
        const memData = history.map(item => item.memory);

        if (document.getElementById('cpuChart')) {
            new Chart(document.getElementById('cpuChart'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'CPU Time (s) [Log Scale]',
                        data: cpuData,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { type: 'logarithmic', beginAtZero: false } },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.parsed.y.toFixed(6) + ' s';
                                }
                            }
                        }
                    }
                }
            });
        }

        if (document.getElementById('memChart')) {
            new Chart(document.getElementById('memChart'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Memory (Bytes) [Log Scale]',
                        data: memData,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { type: 'logarithmic', beginAtZero: false } }
                }
            });
        }
    </script>
</body>
</html>
"""

def parse_rag_to_mermaid(output_text):
    # Use a Left-to-Right graph with styled nodes
    graph = ["graph LR"]
    graph.append("classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;")
    graph.append("classDef resource fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,rx:5,ry:5;")
    
    lines = output_text.split('\n')
    count = 0
    for line in lines:
        m1 = re.search(r'R(\d+)\s+--\((\d+)\)-->\s+P(\d+)', line)
        if m1:
            # Resource -> Process (Allocation)
            graph.append(f"    R{m1.group(1)}(R{m1.group(1)}) -->|{m1.group(2)}| P{m1.group(3)}[P{m1.group(3)}]")
            graph.append(f"    class P{m1.group(3)} process")
            graph.append(f"    class R{m1.group(1)} resource")
            count += 1
            
        m2 = re.search(r'P(\d+)\s+--\((\d+)\)-->\s+R(\d+)', line)
        if m2:
            # Process -> Resource (Request) - Dashed line
            graph.append(f"    P{m2.group(1)}[P{m2.group(1)}] -.->|{m2.group(2)}| R{m2.group(3)}(R{m2.group(3)})")
            graph.append(f"    class P{m2.group(1)} process")
            graph.append(f"    class R{m2.group(3)} resource")
            count += 1
            
    if count == 0:
        return None
    return "\n".join(graph)

@app.route('/reset')
def reset():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return redirect('/')

@app.route('/')
def home():
    p = request.args.get('p', default=100, type=int)
    r = request.args.get('r', default=50, type=int)
    
    history = load_history()
    output = ""
    mermaid_graph = None
    
    # Only run analysis if parameters are explicitly in the query string (user submission)
    if 'p' in request.args and 'r' in request.args:
        # Compile C program
        if not os.path.exists('./bankers') or os.path.getmtime('bankers.c') > os.path.getmtime('bankers'):
            os.system("gcc bankers.c -o bankers")
        
        try:
            cmd = ['./bankers', '3', str(p), str(r)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                mermaid_graph = parse_rag_to_mermaid(output)
                
                lines = output.strip().split('\n')
                if len(lines) >= 1:
                    data_line_str = lines[-1]
                    data_line = data_line_str.split()
                    if len(data_line) >= 4 and data_line[0].isdigit():
                        record = {
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "p": int(data_line[0]),
                        "r": int(data_line[1]),
                        "cpu": float(data_line[2]) if float(data_line[2]) > 0 else 0.000001,
                        "memory": int(data_line[3])
                    }
                    history.append(record)
                    save_history(history)
            else:
                output = result.stderr
        except Exception as e:
            output = f"Error: {str(e)}"

    return render_template_string(HTML_TEMPLATE, p=p, r=r, output=output, history=history, mermaid_graph=mermaid_graph)

if __name__ == '__main__':
    print("Starting Web Server on port 8080...")
    app.run(host='0.0.0.0', port=8080)
