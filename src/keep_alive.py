import os
import signal
import subprocess
import sys
import threading
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "class-assistant-bot"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    port = int(os.getenv("PORT", "8000"))
    # Use threaded=True to avoid blocking
    app.run(host="0.0.0.0", port=port, threaded=True)

def start_bot_process():
    # Start the bot as a subprocess so Flask stays in this process (web service)
    python = sys.executable or "python"
    # Get the directory where keep_alive.py is located (should be src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # main.py is in the same directory as keep_alive.py
    main_py_path = os.path.join(script_dir, "main.py")
    cmd = [python, main_py_path]
    # Forward stdout/stderr so we can see bot logs in Render
    proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return proc

def main():
    # Start bot subprocess
    bot_proc = start_bot_process()

    # Start flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    def handle_signal(sig, frame):
        try:
            bot_proc.terminate()
        except Exception:
            pass
        try:
            bot_proc.wait(timeout=5)
        except Exception:
            try:
                bot_proc.kill()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Wait for bot process to exit and propagate its exit code
    try:
        rc = bot_proc.wait()
        # If bot exits, exit this process too
        sys.exit(rc)
    except KeyboardInterrupt:
        handle_signal(None, None)

if __name__ == "__main__":
    main()
