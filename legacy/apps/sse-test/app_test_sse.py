"""
Test SSE functionality in isolation
"""
from flask import Flask, Response, send_file
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('test_sse_simple.html')

@app.route('/test-sse')
def test_sse():
    def generate():
        # Send initial connection
        yield f"data: {json.dumps({'event': 'connected', 'message': 'SSE stream started'})}\n\n"

        # Send 10 test messages, one per second
        for i in range(1, 11):
            time.sleep(1)
            yield f"data: {json.dumps({'event': 'test', 'message': f'Test message {i}'})}\n\n"

        # Send done signal
        yield f"data: {json.dumps({'event': 'done', 'message': 'Test complete'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
