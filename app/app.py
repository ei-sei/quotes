from flask import Flask
import redis
import os
import json
import random

app = Flask(__name__)

# Read Redis connection details from environment variables
# Second argument is the default value if the env variable is not set
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', '6379'))  # cast to int - Redis client expects a number, not a string

# Connect to Redis
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

print(f"Connecting to Redis at {redis_host}:{redis_port}")

with open('quotes.json') as f:
    quotes = json.load(f)

# Route for the home page
@app.route('/')
def home():
    visit_count = redis_client.incr('visit_count')
    return f'''
        <h4>Welcome to my quote generator!</h4>
        <a href="/quote"><button>Generate a quote</button></a>
        <br><br>Counter: {visit_count}
    '''

@app.route('/quote')
def quote():
    q = random.choice(quotes)
    count = redis_client.incr('quote_count')
    
    return f'"{q["text"]}"<br>- {q["author"]}<br><br>Global total quotes generated: {count}<br><a href="/quote"><button>New Quote</button></a>'

# Only runs when executed directly (not when imported or run via a WSGI server)
# 0.0.0.0 makes the app reachable from outside the container
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

