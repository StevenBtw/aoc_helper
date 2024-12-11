import re
from bs4 import BeautifulSoup

def find_best_test_case(code_blocks, text):
    """Find the most relevant test case from multiple code blocks."""
    best_block = None
    best_score = -1
    
    for block in code_blocks:
        block_text = block.text.strip()
        prev_text = block.find_previous(text=True) or ''
        next_text = block.find_next(text=True) or ''
        
        # Score this block
        score = 0
        
        # Prefer examples that are explicitly called out
        if re.search(r'example|instance|consider|for example', prev_text, re.IGNORECASE):
            score += 3
        
        # Prefer examples that are followed by explanations
        if re.search(r'produces|result|total|sum|count|distance', next_text, re.IGNORECASE):
            score += 2
        
        # Prefer longer examples as they're usually more complete
        score += len(block_text.split('\n'))
        
        if score > best_score:
            best_score = score
            best_block = block_text
    
    return best_block

def find_inline_example(text):
    """Find the best inline example in text."""
    inline_matches = re.finditer(r'["`\']((?:[^`"\']|\n){10,})["`\']', text)
    best_example = None
    for match in inline_matches:
        example = match.group(1).strip()
        if not best_example or len(example) > len(best_example):
            best_example = example
    return best_example

def find_expected_result(text):
    """Extract expected result using various patterns."""
    result_patterns = [
        # Distance/Count patterns
        (r'total distance of (\d+)', 1),
        (r'(\d+) times', 1),
        (r'would have (\d+)', 1),
        (r'total of (\d+)', 1),
        (r'(\d+) (?:stones|positions|reports|locations)', 1),
        
        # Score patterns
        (r'similarity score [^.!?]* is (\d+)', 1),
        (r'score [^.!?]* is (\d+)', 1),
        
        # Sum patterns
        (r'sum (?:is|of) (\d+)', 1),
        (r'sum of [^.!?]* is (\d+)', 1),
        (r'adds up to (\d+)', 1),
        (r'total (?:is|of) (\d+)', 1),
        (r'this is [^.!?]*?(\d+)', 1),
        (r'the sum of [^.!?]* is (\d+)', 1),
        
        # Calculation patterns
        (r'produces (?:a total of )?(\d+)', 1),
        (r'results? in (\d+)', 1),
        (r'equals? (\d+)', 1),
        (r'\(.*?=\s*(\d+)\)', 1),  # Matches (2*4 + 8*5 = 48)
        
        # Would/Will patterns
        (r'would be (\d+)', 1),
        (r'will have (\d+)', 1),
        
        # Generic patterns
        (r'answer (?:is|would be) (\d+)', 1),
        (r'result (?:is|would be) (\d+)', 1),
        (r'score (?:is|of) (\d+)', 1)
    ]
    
    for pattern, group in result_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(group)
    
    return None

def extract_test_case(problem_text):
    """Extract test case and expected result from problem text."""
    soup = BeautifulSoup(problem_text, 'html.parser')
    text = soup.get_text()
    
    # First try to find test case in <pre> blocks
    code_blocks = soup.find_all('pre')
    if code_blocks:
        test_case = find_best_test_case(code_blocks, text)
    else:
        # If no <pre> blocks, look for inline examples
        test_case = find_inline_example(text)
    
    # Find expected result
    expected_result = find_expected_result(text)
    
    return test_case, expected_result

def create_solution_template(day, part, test_case, expected_result):
    """Create solution template with test case and expected result."""
    if not test_case:
        test_case = "# No test case found in problem description"
    
    template = f"""# Advent of Code 2023 - Day {day} Part {part}

def solve(data):
    # TODO: Implement solution
    pass

def parse_input(input_text):
    return [line.strip() for line in input_text.split('\\n') if line.strip()]

# Test case
test_input = \"\"\"
{test_case}
\"\"\"
expected_result = {expected_result or 'None'}  # From problem description

# Run test case
test_data = parse_input(test_input)
test_result = solve(test_data)
print(f"Test case result: {{test_result}}")

# Verify against expected result
if expected_result is not None:
    if str(test_result) == str(expected_result):
        print("[PASS] Test case passed!")
        # Run actual input
        with open('input.txt', 'r') as f:
            input_data = parse_input(f.read())
        result = solve(input_data)
        print(f"Result: {{result}}")
        
        # Write result to solution file
        with open(f'solution{str(part)}.txt', 'w') as f:
            f.write(str(result))
    else:
        print(f"[FAIL] Test case failed! Expected {{expected_result}}, got {{test_result}}")
else:
    print("No expected result found in problem text")
    if test_result is not None:
        # Run actual input
        with open('input.txt', 'r') as f:
            input_data = parse_input(f.read())
        result = solve(input_data)
        print(f"Result: {{result}}")
        
        # Write result to solution file
        with open(f'solution{str(part)}.txt', 'w') as f:
            f.write(str(result))
"""
    return template
