
import threading
import time
import uvicorn
import webview
import requests
from main import app


def start_api():
    """Runs the FastAPI server in a background thread.

    The server is started using Uvicorn on host 127.0.0.1 and port 8000.
    """
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)


def wait_for_server(url: str, timeout: int = 10) -> bool:
    """Waits until the FastAPI server becomes available.

    It repeatedly sends HTTP requests to the specified URL until
    the server responds with a 200 status code or the timeout is reached.

    Args:
        url (str): The server URL to check.
        timeout (int, optional): Maximum waiting time in seconds.
            Defaults to 10.

    Returns:
        bool: True if the server is available, False otherwise.
    """
    for _ in range(timeout * 10):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()

    if wait_for_server("http://127.0.0.1:8000"):
        webview.create_window("Tiendo", "http://127.0.0.1:8000")
        webview.start()
    else:
        print("Error: FastAPI server did not start in time.")
