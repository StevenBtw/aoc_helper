import sys
import requests
import time
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import json

# Your session cookie from adventofcode.com
SESSION_ID = ""

# Request headers with proper User-Agent
HEADERS = {
    'User-Agent': 'github.com/your-username/aoc_helper by your-email@example.com'  # TODO: Update with your info
}

# Rate limiting settings
MIN_REQUEST_INTERVAL = 15  # Minimum seconds between requests
last_request_time = 0

# Global variables for problem text
problem_data = {
    "part1": None,
    "part2": None,
    "day": None
}

def throttle_request():
    """Ensures minimum delay between requests to respect rate limits."""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last
        time.sleep(sleep_time)
    last_request_time = time.time()

class ProblemHandler(SimpleHTTPRequestHandler):
    """Handles HTTP requests for the local problem viewer."""
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('problem.html', 'r', encoding='utf-8') as f:
                content = f.read()
            self.wfile.write(content.encode())
        
        elif self.path == '/problem-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(problem_data).encode())
        
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def start_server(port=8000):
    """Starts local HTTP server for problem viewing."""
    server = HTTPServer(('localhost', port), ProblemHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

def create_html_template(day):
    """Creates HTML template for problem viewing."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Advent of Code 2024 - Day {day}</title>
    <style>
        body {{
            font-family: 'Source Code Pro', monospace;
            background-color: #0f0f23;
            color: #cccccc;
            max-width: 900px;
            margin: 0 auto;
            padding: 1em;
        }}
        h1, h2 {{
            color: #00cc00;
            text-shadow: 0 0 2px #00cc00, 0 0 5px #00cc00;
        }}
        .problem-text {{
            line-height: 1.5;
            margin: 1em 0;
        }}
        pre {{
            background-color: #10101a;
            padding: 1em;
            border-radius: 4px;
            overflow-x: auto;
        }}
        code {{
            color: #ffffff;
        }}
        #part2 {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #333340;
        }}
    </style>
</head>
<body>
    <h1>Advent of Code 2024 - Day {day}</h1>
    <div id="part1" class="problem-text"></div>
    <div id="part2" class="problem-text"></div>

    <script>
        function updateProblemText() {{
            fetch('/problem-data')
                .then(response => response.json())
                .then(data => {{
                    if (data.part1) {{
                        document.getElementById('part1').innerHTML = data.part1;
                    }}
                    if (data.part2) {{
                        document.getElementById('part2').innerHTML = data.part2;
                    }}
                }});
        }}

        // Update initially and every 5 seconds
        updateProblemText();
        setInterval(updateProblemText, 5000);
    </script>
</body>
</html>
"""
    with open('problem.html', 'w', encoding='utf-8') as f:
        f.write(html)

def fetch_with_retry(url, cookies, max_retries=float('inf')):
    """Makes HTTP GET request with retry logic and rate limiting."""
    throttle_request()  # Ensure minimum delay between requests
    retries = 0
    while True:
        try:
            response = requests.get(url, cookies=cookies, headers=HEADERS)
            if response.status_code == 200:
                return response
            print(f"Request failed with status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
        
        retries += 1
        if retries >= max_retries:
            print(f"Max retries ({max_retries}) reached. Giving up.")
            return None
        
        print(f"Retrying in {MIN_REQUEST_INTERVAL} seconds... (attempt {retries + 1})")
        time.sleep(MIN_REQUEST_INTERVAL)

def get_next_puzzle_time():
    """Returns datetime of next puzzle unlock in EST timezone."""
    url = "https://adventofcode.com/2024"
    response = fetch_with_retry(url, {'session': SESSION_ID})
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    countdown = soup.find('div', class_='countdown')
    if not countdown:
        return None

    countdown_text = countdown.get_text()
    if "unlock" not in countdown_text.lower():
        return None

    time_parts = [int(t) for t in countdown_text.split() if t.isdigit()]
    if not time_parts:
        return None

    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    target = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=est)
    if now.hour >= 0:
        target += timedelta(days=1)
    
    return target

def handle_wait_time(message, part):
    """Extracts wait time from response message and handles solution file."""
    wait_match = re.search(r'wait (\d+)s', message) or re.search(r'have (\d+)s left to wait', message)
    if wait_match:
        wait_time = int(wait_match.group(1))
        solution_file = f'solution{part}.txt'
        if os.path.exists(solution_file):
            os.remove(solution_file)
            print(f"Deleted {solution_file} - will retry in {wait_time} seconds")
        return wait_time
    return None

def submit_answer(day, part, answer):
    """Submits solution to AoC and returns (success, message)."""
    throttle_request()  # Ensure minimum delay between requests
    url = f"https://adventofcode.com/2024/day/{day}/answer"
    data = {
        'level': str(part),
        'answer': str(answer)
    }
    cookies = {'session': SESSION_ID}
    
    print(f"\nSubmitting answer for part {part}: {answer}")
    response = requests.post(url, data=data, cookies=cookies, headers=HEADERS)
    if response.status_code != 200:
        return False, "Failed to submit answer"

    soup = BeautifulSoup(response.text, 'html.parser')
    message = soup.find('article').text.strip()
    print(f"Server response: {message}")
    
    # Check for wait time
    wait_time = handle_wait_time(message, part)
    if wait_time is not None:
        return False, f"Need to wait {wait_time} seconds"
    
    if "That's the right answer" in message:
        return True, "Correct answer!"
    else:
        # Wrong answer, delete solution file
        solution_file = f'solution{part}.txt'
        if os.path.exists(solution_file):
            os.remove(solution_file)
            print(f"Deleted {solution_file} - answer was wrong")
        return False, message

def update_problem_text(day):
    """Fetches problem description and updates global problem_data."""
    base_url = f"https://adventofcode.com/2024/day/{day}"
    cookies = {'session': SESSION_ID}
    
    print(f"Fetching from {base_url}")
    response = fetch_with_retry(base_url, cookies)
    if not response:
        return False, None

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='day-desc')
    
    if articles:
        problem_data['day'] = day
        problem_data['part1'] = str(articles[0])
        if len(articles) > 1:
            problem_data['part2'] = str(articles[1])
            print("Part 2 is available!")
            create_solution_template(day, 2, str(articles[1]))
        return True, str(articles[0])
    else:
        print("Could not find problem description")
        return False, None

def fetch_input(day, force=False):
    """Downloads input file for given day if not already cached."""
    if os.path.exists('input.txt') and not force:
        print("Input already exists, skipping...")
        return True

    input_url = f"https://adventofcode.com/2024/day/{day}/input"
    cookies = {'session': SESSION_ID}
    
    print(f"Fetching from {input_url}")
    response = fetch_with_retry(input_url, cookies)
    if not response:
        return False

    with open('input.txt', 'w') as f:
        f.write(response.text.strip())
    return True

def extract_test_case(problem_text):
    """Extracts first code block from problem description as test case."""
    soup = BeautifulSoup(problem_text, 'html.parser')
    code_blocks = soup.find_all('pre')
    if code_blocks:
        return code_blocks[0].text.strip()
    return None

def create_solution_template(day, part, problem_text):
    """Creates Python solution template with extracted test case."""
    test_case = extract_test_case(problem_text)
    if not test_case:
        test_case = "# No test case found in problem description"

    template = f"""# Advent of Code 2024 - Day {day} Part {part}

def solve(data):
    # TODO: Implement solution
    pass

def parse_input(input_text):
    return [line.strip() for line in input_text.split('\\n') if line.strip()]

# Test case
test_input = \"\"\"
{test_case}
\"\"\"

# Run test case
test_data = parse_input(test_input)
test_result = solve(test_data)
print(f"Test case result: {{test_result}}")

# If test case passes, run actual input
if test_result is not None:
    with open('input.txt', 'r') as f:
        input_data = parse_input(f.read())
    result = solve(input_data)
    print(f"Result: {{result}}")
    
    # Write result to solution file
    with open(f'solution{part}.txt', 'w') as f:
        f.write(str(result))
"""

    filename = f'solution{part}_day{day}.py'
    with open(filename, 'w') as f:
        f.write(template)
    print(f"Created {filename}")

def monitor_solutions(day):
    """Monitors and submits solutions as they become available."""
    part1_submitted = False
    part2_submitted = False
    
    while not (part1_submitted and part2_submitted):
        try:
            # Check for part 1 solution
            if not part1_submitted and os.path.exists('solution1.txt'):
                with open('solution1.txt', 'r') as f:
                    answer = f.read().strip()
                success, message = submit_answer(day, 1, answer)
                print(f"Part 1 submission result: {message}")
                if success:
                    part1_submitted = True
                    # Update problem text to get part 2
                    update_problem_text(day)
                elif "wait" in message.lower():
                    wait_match = re.search(r'wait (\d+)s', message) or re.search(r'have (\d+)s left to wait', message)
                    if wait_match:
                        wait_time = int(wait_match.group(1))
                        if os.path.exists('solution1.txt'):
                            os.remove('solution1.txt')
                            print(f"Deleted solution1.txt - will retry in {wait_time} seconds")
                        time.sleep(wait_time + 1)  # Add 1 second buffer
            
            # Check for part 2 solution
            if part1_submitted and not part2_submitted and os.path.exists('solution2.txt'):
                with open('solution2.txt', 'r') as f:
                    answer = f.read().strip()
                success, message = submit_answer(day, 2, answer)
                print(f"Part 2 submission result: {message}")
                if success:
                    part2_submitted = True
                elif "wait" in message.lower():
                    wait_match = re.search(r'wait (\d+)s', message) or re.search(r'have (\d+)s left to wait', message)
                    if wait_match:
                        wait_time = int(wait_match.group(1))
                        if os.path.exists('solution2.txt'):
                            os.remove('solution2.txt')
                            print(f"Deleted solution2.txt - will retry in {wait_time} seconds")
                        time.sleep(wait_time + 1)  # Add 1 second buffer
            
            time.sleep(1)  # Check every second
            
        except Exception as e:
            print(f"Error in monitor_solutions: {e}")
            time.sleep(1)  # Wait a bit on error

def fetch_aoc_content(day, force=False):
    """Sets up problem environment and starts solution monitoring."""
    print("Creating HTML template...")
    create_html_template(day)
    
    print("Starting local server...")
    server = start_server()
    
    print("Fetching problem text...")
    result, problem_text = update_problem_text(day)
    if not result:
        return False
    
    print("Fetching input...")
    if not fetch_input(day, force):
        return False
    
    print("Creating solution template...")
    create_solution_template(day, 1, problem_text)
    
    print("Starting solution monitor...")
    monitor_thread = threading.Thread(target=monitor_solutions, args=(day,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_script.py <day> [--force]")
        sys.exit(1)
    
    try:
        day = int(sys.argv[1])
        if day < 1 or day > 25:
            print("Day must be between 1 and 25")
            sys.exit(1)
    except ValueError:
        print("Day must be a number")
        sys.exit(1)
    
    force = "--force" in sys.argv
    
    # Check next puzzle time
    next_puzzle = get_next_puzzle_time()
    if next_puzzle:
        now = datetime.now(pytz.timezone('US/Eastern'))
        wait_time = (next_puzzle - now).total_seconds() - 1  # minus 1 second
        if wait_time > 0:
            print(f"Waiting {wait_time:.0f} seconds for next puzzle...")
            time.sleep(wait_time)
    
    print(f"Fetching content for day {day}...")
    if fetch_aoc_content(day, force):
        print("Successfully fetched content!")
        print("\nLocal server running at http://localhost:8000")
        print("\nMonitoring for solutions in solution1.txt and solution2.txt")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)
