import time
import requests
from prometheus_client import start_http_server, Gauge

# Prometheus metric
CONFIDENCE_GAUGE = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from the ML API'
)

# The app runs on NodePort 32500
APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5  # seconds


def fetch_confidence():
    try:
        response = requests.get(APP_URL, timeout=4)
        response.raise_for_status()
        data = response.json()
        return float(data.get("confidence", 1.0))
    except Exception:
        return 1.0


if __name__ == "__main__":
    # Start Prometheus HTTP server on port 8000
    start_http_server(8000)
    print("Exporter running on port 8000. Polling every 5s...")
    while True:
        confidence = fetch_confidence()
        CONFIDENCE_GAUGE.set(confidence)
        print(f"[{time.strftime('%H:%M:%S')}] confidence={confidence:.4f}")
        time.sleep(POLL_INTERVAL)
