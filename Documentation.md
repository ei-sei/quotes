# Documentation on changes Made
This section focusses on documenting the changes made for each new feature

```
Features/
├── Quotes
├── (placeholder)
└── (placeholder)

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
Add the imports needed to read the JSON file, select a random quote, and return a proper JSON response:
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
