# Documentation on changes Made
This section focusses on documenting the changes made for each new feature

```
Features/
├── Quotes
├── Quote Counter + New Quote Button
└── (placeholder)

```

```
Issues/
└── Port 80 conflict on EC2 deployment

```

---

## 1. Quotes

#### `app/quotes.json` - new file
A dedicated file to store all quotes outside of the application code, making them easy to edit without touching Python.
```json
[
  {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
  {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
  {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"}
]
```

#### `app/app.py` - modified
Added the imports needed to read the JSON file, select a random quote, and return a proper JSON response:
```python
import json
import random
from flask import Flask, jsonify
```


Opens `quotes.json`, reads its contents, and converts it into a Python list stored in `quotes`. This runs once at container startup so it isn't re-read on every request:
```python
with open('quotes.json') as f:
    quotes = json.load(f)
```

New route that picks a random quote from the loaded list and returns it as a JSON response:
```python
@app.route('/quote')
def quote():
    q = random.choice(quotes)
    return jsonify(q)
# If you want to return as string instead: 
#   return f'"{q["text"]}" — {q["author"]}'
```

#### `app/Dockerfile` - modified
Without this line, `quotes.json` would not be included in the Docker image and the app would crash on startup when trying to open the file:
```dockerfile
COPY quotes.json .
```

---

## 2. Quote Counter + New Quote Button

#### `app/app.py` - modified
Increments a `quote_count` key in Redis each time `/quote` is called and returns the total alongside the quote. A "New Quote" button is included in the response so the user can request another quote without going back to the home page:
```python
@app.route('/quote')
def quote():
    q = random.choice(quotes)
    count = redis_client.incr('quote_count')
    return f'"{q["text"]}"<br>- {q["author"]}<br><br>Quotes generated: {count}<br><a href="/quote"><button>New Quote</button></a>'
```

`quote_count` is a separate Redis key from `visit_count` — they track independently and do not affect each other.

Changed the default route to generate a quote instead of count button
```py
    return '''
        <h4>Welcome to Flask + Redis!</h4>
        <a href="/quote"><button>Generate a quote</button></a>
    '''
```

Removed `/count` path and modified home route, counter now increments on each visit
```py
@app.route('/')
def home():
    visit_count = redis_client.incr('visit_count')
    return f'''
        <h4>Welcome to my quote generator!</h4>
        <a href="/quote"><button>Generate a quote</button></a>
        <br>Counter: {visit_count}
    '''
```
---

## Issue: Port 80 conflict on EC2 deployment

After pulling the repository and running `docker compose up --build` on EC2, the following error appeared:

```
Error response from daemon: failed to set up container networking: driver failed programming
external connectivity on endpoint nginx-lb: failed to bind host port 0.0.0.0:80/tcp: address already in use
```

The message `failed to bind host port 0.0.0.0:80/tcp: address already in use` indicates port 80 was already occupied on the host. Running the following confirmed nginx was the process using it:

```bash
sudo ss -tlnp | grep :80
```

Nginx had been installed and configured directly on the EC2 instance previously and was still running, blocking Docker from binding port 80 for the nginx container.

**Fix:** Stop and disable the host nginx service, then redeploy:

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
docker compose up -d
```

---