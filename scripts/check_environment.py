import sys
import platform
import json
import urllib.request
import urllib.error

OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL_NAME = "gemma3:4b"

print("Python version:", sys.version.split()[0])
print("Operating system:", platform.system(), platform.release())

try:
    with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
except (urllib.error.URLError, TimeoutError):
    print("Ollama: NOT responding. Gemma tests will be skipped.")
    sys.exit(0)
except ValueError:
    print("Ollama: answered, but the reply was not readable JSON.")
    sys.exit(0)

model_names = [m.get("name") for m in data.get("models", [])]
print("Ollama: responding")
print("Models found:", model_names)

if MODEL_NAME in model_names:
    print(MODEL_NAME, ": FOUND")
else:
    print(MODEL_NAME, ": NOT FOUND")