# 🎄 Advent of Code Helper

A magical helper script that takes the grunt work out of Advent of Code! No more manual copy-pasting or browser switching - just pure problem-solving fun.

## ✨ Features

- 🚀 Auto-fetches daily problems and inputs
- 📝 Creates pre-populated solution templates with test cases
- 🌐 Runs a local server to display problems (no more browser tabs!)
- 🔄 Auto-submits solutions when you save them
- ⏰ Can wait for puzzle unlock and auto-start
- 🔁 Handles rate limiting and retries automatically

## 🎯 Quick Start

1. Get your session cookie from [Advent of Code](https://adventofcode.com):
   - Log into AoC
   - Open browser dev tools (F12)
   - Go to Application/Storage > Cookies
   - Copy the `session` cookie value

2. Add your session cookie to the script:
   ```python
   SESSION_ID = "your_session_cookie_here"
   ```

3. Run the script for any day:
   ```bash
   python prep_script.py <day>
   ```

## 💫 Pro Tips

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
   alias aoc='python path/to/prep_script.py'
   ```

2. Launch next puzzle with auto-wait:
   ```bash
   aoc <day>
   ```
   The script will wait for puzzle unlock and auto-start!

## 🎮 Usage

- Force refresh content: `python prep_script.py <day> --force`
- View problems locally: Open `http://localhost:8000` after starting
- Solutions auto-submit when you save `solution1.txt` or `solution2.txt`
- Check terminal for submission results and any wait times

Happy coding! 🎄✨

