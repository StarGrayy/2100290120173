from flask import Flask, jsonify
import requests
from collections import deque
import time

app = Flask(__name__)
WINDOW_SIZE = 10
numbers_deque = deque(maxlen=WINDOW_SIZE)

URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/random'
}

BEARER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE3MjIyNzY3LCJpYXQiOjE3MTcyMjI0NjcsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImY2NjY2YzAyLTZiOTItNGNjZC05OTQ4LTFmMmNkMDY0NmNlZCIsInN1YiI6InN3YXRpLjIxMjVjczEwNTZAa2lldC5lZHUifSwiY29tcGFueU5hbWUiOiJQbHVzaGVzRm9yWW91IiwiY2xpZW50SUQiOiJmNjY2NmMwMi02YjkyLTRjY2QtOTk0OC0xZjJjZDA2NDZjZWQiLCJjbGllbnRTZWNyZXQiOiJMWWZ5TmRKRFBseXNqUnlVIiwib3duZXJOYW1lIjoiU3dhdGkgTWlzaHJhIiwib3duZXJFbWFpbCI6InN3YXRpLjIxMjVjczEwNTZAa2lldC5lZHUiLCJyb2xsTm8iOiIyMTAwMjkwMTIwMTczIn0.ZvX03GyvuDSZXmebeNXc6J8GHEPKcgQn3tOwVFatdy8'

def fetch_numbers(url):
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}'
    }
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=0.5)
        if time.time() - start_time > 0.5:
            return []
        response.raise_for_status()
        return response.json().get('numbers', [])
    except (requests.exceptions.RequestException, ValueError):
        return []

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    if number_id not in URLS:
        return jsonify({"error": "Invalid number ID"}), 400
    
    url = URLS[number_id]
    new_numbers = fetch_numbers(url)
    
    if not new_numbers:
        return jsonify({"error": "Failed to fetch numbers"}), 500
    
    prev_state = list(numbers_deque)
    unique_new_numbers = list(set(new_numbers))
    numbers_deque.extend(unique_new_numbers)
    
    curr_state = list(numbers_deque)
    avg = sum(curr_state) / len(curr_state) if curr_state else 0
    
    response = {
        "windowPrevState": prev_state,
        "windowCurrState": curr_state,
        "numbers": unique_new_numbers,
        "avg": round(avg, 2)
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=5000)
