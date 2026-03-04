from flask import Flask
import redis
import os  # lets us read environment variables set by Docker

app = Flask(__name__)

# Read Redis connection details from environment variables
# Second argument is the default value if the env variable is not set
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', '6379'))  # cast to int - Redis client expects a number, not a string

# Connect to Redis
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

print(f"Connecting to Redis at {redis_host}:{redis_port}")  # logs to container output - useful for debugging

# Route for the home page - returns a welcome message with a link to the counter
@app.route('/')
def home():
    return '''
        <h4>Welcome to Flask + Redis!</h4>
        <a href="/count"><button>Go to Counter</button></a>
    '''

# Route for the counter - every visit increments the count in Redis
@app.route('/count')
def count():
    # INCR atomically increments 'visit_count' by 1 and returns the new value
    # If the key doesn't exist yet, Redis creates it starting at 0 before incrementing
    visit_count = redis_client.incr('visit_count')
    return f'Visit count: {visit_count}'

# Only runs when executed directly (not when imported or run via a WSGI server)
# 0.0.0.0 makes the app reachable from outside the container
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

