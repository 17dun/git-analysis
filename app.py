import os
import subprocess
import sys
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/start')
def start_analysis():
    name = request.args.get('name')
    
    if not name:
        return jsonify({'error': 'Missing name parameter'}), 400
    
    try:
        result = subprocess.run(
            [sys.executable, 'start.py', name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Analysis failed',
                'stderr': result.stderr
            }), 500
        
        output_path = result.stdout.strip()
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({
                'error': 'Output file not found',
                'stdout': result.stdout,
                'stderr': result.stderr
            }), 500
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(output_path),
            'content': content
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Analysis timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
