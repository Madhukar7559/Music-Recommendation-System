import os;
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(script_dir)
app = Flask(__name__, template_folder=template_dir, static_folder='static')

@app.route('/sse')
def sse():
    def generate():
        while True:
            # Generate an event
            event_data = "Event data: {}".format(time.time())

            # Send the event as SSE format
            yield "data: {}\n\n".format(event_data)

            # Delay for some time before sending the next event
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)