import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def facial_prediction(derived_result):
    mode = os.environ.get("ML_MODE", "mock").lower()
    service_url = os.environ.get("FACIAL_ML_SERVICE_URL", "").strip()
    if mode == "http" and service_url:
        try:
            request = Request(service_url, data=json.dumps(derived_result).encode(), headers={"Content-Type": "application/json"})
            with urlopen(request, timeout=float(os.environ.get("ML_SERVICE_TIMEOUT", "3"))) as response:
                result = json.loads(response.read())
            if not isinstance(result, dict):
                raise ValueError("facial service returned a non-object")
            return result
        except (OSError, URLError, ValueError, TimeoutError):
            pass
    return derived_result
