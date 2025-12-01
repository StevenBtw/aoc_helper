# Archived

https://github.com/henriupton99/AdventOfCode/tree/main
is a better maintained alternative. 

# 🎄 Advent of Code Helper
One of the challenges of OaC is to break the problem down into smaller manageble parts. One easy "problem" that is the same for each day is copying the input, creating a test case based on the problem text and copy paste submitting solutions. This helper script takes the boring stuff out of Advent of Code. No more manual copy-pasting or browser switching just full problem-solving focus. This will probably also significantly speed up your submissions. 

##  Features
- Auto-fetches daily problems and inputs
- Creates pre-populated solution templates with test cases
- Runs a local server to display problems (no more browser tabs!)
- Auto-submits solutions when you save them
- Can wait for puzzle unlock and auto-start
- Handles rate limiting and retries automatically (15s minimum between requests)
- Follows AoC automation guidelines with proper User-Agent
- Smart test case extraction with pattern matching
- Extensible problem text processing for better readability or summarisation

## Quick Start
1. Get your session cookie from [Advent of Code](https://adventofcode.com):
   - Log into AoC
   - Open browser dev tools (F12)
   - Go to Application/Storage > Cookies
   - Copy the `session` cookie value

2. Add your session cookie and contact info to the script:
   ```python
   SESSION_ID = "your_session_cookie_here"
   HEADERS = {
       'User-Agent': 'github.com/your-username/aoc_helper by your-email@example.com'
   }
   ```

3. Run the script for any day:
   ```bash
   python main.py <day>
   ```

## Pro Tips
### Auto-Run Solutions on Save
1. Install the "Run on Save" VSCode extension
2. Add this to your VSCode settings.json:
   ```json
   {
       "emeraldwalk.runonsave": {
           "commands": [
               {
                   "match": "solution[12]_day\\d+\\.py$",
                   "cmd": "python ${file}"
               }
           ]
       }
   }
   ```

Now your solutions will automatically run and submit whenever you save! 🚀

### Speed Run Setup
1. Create a terminal alias for quick starts:
   ```bash
   # Add to your .bashrc or .zshrc
   alias aoc='python path/to/main.py'
   ```

2. Launch next puzzle with auto-wait:
   ```bash
   aoc <day>
   ```
   The script will wait for puzzle unlock and auto-start!

## 🎮 Usage
- Force refresh content: `python main.py <day> --force`
- View problems locally: Open `http://localhost:8000` after starting
- Solutions auto-submit when you save `solution1.txt` or `solution2.txt`
- Check terminal for submission results and any wait times
- Enhance your problem viewer with custom logic in `problem_text_processor.py`
- Extend test case extraction patterns in `test_case_extractor.py`
- Extend the solution scripts that are generated with your favorite libraries for even less typing

Happy coding! 🎄
