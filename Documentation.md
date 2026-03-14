# Documentation on changes Made
This section focusses on documenting the changes made for each new feature

```
Features/
├── Quotes
├── Quote Counter + New Quote Button
├── Jinja2 Templates
└── Styled UI

```

```
Issues/
├── Port 80 conflict on EC2 deployment
└── TemplateNotFound after switching to Jinja2

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

## 3. Jinja2 Templates

Replaced inline HTML strings in route handlers with Jinja2 templates. Flask includes Jinja2 by default, so no new dependencies were needed. This separates the presentation layer from the application logic, making it easier to update the UI without modifying Python code.

#### `app/templates/index.html` - new file
A single shared template used by both the `/` and `/quote` routes. It conditionally renders the quote block only when a quote is passed:
```html
<!DOCTYPE html>
<html>
<head><title>Quotes</title></head>
<body>
  <h1>{{ title }}</h1>
  <p>{{ message }}</p>

  {% if quote %}
    <blockquote>"{{ quote.text }}" - {{ quote.author }}</blockquote>
  {% endif %}

  <a href="/quote">New Quote</a>
</body>
</html>
```

- `{{ variable }}` outputs a value
- `{% if %}` conditionally renders a block
- The `quote` variable is only passed by the `/quote` route, so the home page skips the blockquote

#### `app/app.py` - modified
Replaced `jsonify` import with `render_template` and updated both routes to return templates instead of inline HTML strings:
```python
from flask import render_template
```

Home route now passes `title` and `message` as template variables:
```python
@app.route('/')
def home():
    visit_count = redis_client.incr('visit_count')
    return render_template('index.html', title='welcome', message=f'Visits: {visit_count}')
```

Quote route passes the quote object along with the counter message:
```python
@app.route('/quote')
def quote():
    q = random.choice(quotes)
    count = redis_client.incr('quote_count')
    return render_template('index.html', quote=q, message=f'Quotes generated: {count}')
```

Flask automatically looks for templates in a `templates/` directory relative to the application file - no path prefix needed.

#### `app/Dockerfile` - modified
Added a line to copy the templates directory into the container image:
```dockerfile
COPY templates/ templates/
```

Without this, the container would crash with `jinja2.exceptions.TemplateNotFound: index.html` since the template files would not exist inside the image.

---

## 4. Styled UI

Added CSS styling directly inside `index.html` to replace the unstyled default browser look with a polished, responsive design. No new files or dependencies were needed since all styles live in a `<style>` block within the template.

#### `app/templates/index.html` - modified
Rewrote the template with embedded CSS and a structured layout. The Jinja2 logic remains the same, only the surrounding HTML and styling changed:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quotes</title>
  <style>
    ...
  </style>
</head>
<body>
  <div class="container">
    <h1>{{ title }}</h1>
    <p class="message">{{ message }}</p>

    {% if quote %}
      <blockquote>
        {{ quote.text }}
        <span class="author">- {{ quote.author }}</span>
      </blockquote>
    {% endif %}

    <a href="/quote" class="btn">New Quote</a>
  </div>
</body>
</html>
```

Key style choices:
- **Layout** - Flexbox centers the content vertically and horizontally on the page. A `.container` wrapper caps the width at 600px so lines stay readable
- **Background** - Dark purple/indigo gradient (`#0f0c29` to `#302b63` to `#24243e`) gives a modern feel without needing images
- **Typography** - Georgia serif font with light weight and letter-spacing for a clean, editorial look
- **Quote block** - A large decorative opening quotation mark (`::before` pseudo-element) in semi-transparent purple, italic text, and a separated author line
- **Button** - Pill-shaped outline button (`border-radius: 50px`) with a purple glow (`box-shadow`) on hover
- **Responsive** - Viewport meta tag and percentage-based widths ensure the layout adapts to mobile screens

No changes were needed to `app.py` or the Dockerfile since no new files were added and the template filename stayed the same.

---

## Issue:

### Port 80 conflict on EC2 deployment

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

### TemplateNotFound after switching to Jinja2

After updating `app.py` to use `render_template()` instead of inline HTML strings, the app returned a 500 Internal Server Error. The Flask logs showed:

```
jinja2.exceptions.TemplateNotFound: index.html
```

**Missing COPY in Dockerfile**

The `templates/` directory was not being copied into the Docker image. Even though the template existed locally, it was absent inside the container:
```dockerfile
# Added to Dockerfile
COPY templates/ templates/
```

**Fix:** added the `COPY templates/ templates/` line to the Dockerfile, then rebuilt:

```bash
docker compose up --build
```

