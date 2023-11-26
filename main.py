import sys

from io import StringIO
from contextlib import redirect_stdout
from llama_cpp import Llama

preconfigured_prompts = {
  "bitcoin": {
    "current": "Can you get the current price of Bitcoin?"
  },
  "ethereum": {
    "current": "Can you get the current price of Ethereum?"
  },
  "ticker": {
    "current": 'Using the yfinance package, get TICKER stock and print .["currentPrice"], written in python',
    "previous_seven_days": 'Using the yfinance package, get TICKER stock and print .history(period="7d")["Close"], written in python'
  }
}

if len(sys.argv) < 2:
  print("Please enter the location of a large language model")
  exit()

if len(sys.argv) < 3:
  print("Please type a comma separated lists of options: e.g. 'bitcoin,current'")
  exit()

path_to_large_language_model = sys.argv[1]
options = sys.argv[2]

pieces = options.split(",")
if len(pieces) != 2:
  print("Please type a comma separated lists of options: e.g. 'bitcoin,current'")
  exit()

type = pieces[0].lower()
date = pieces[1].lower()

ticker = ""
if type.startswith("ticker="):
  ticker = f"{type}".replace("ticker=","")
  type = "ticker"

prompt = preconfigured_prompts.get(f'{type}',{}).get(f'{date}', None)

if ticker != "":
  prompt = prompt.replace("TICKER", ticker)

if prompt is None:
  print(f"Error: Exiting as no prompt found for: {options}")
  exit()

llm = Llama(
  model_path=f"{path_to_large_language_model}",
  chat_format="llama-2",
  n_ctx=2048,
  verbose=False
)

print("Attempting to generate code...\n")

output = llm.create_chat_completion(
  messages=[
    {
      "role": "system",
      "content": "You are Fortuna. Fortuna is a useful assistant who writes Python code to answer questions. She keeps the code as short as possible and doesn't read from user input"
    },
    {
      "role": "user",
      "content": f"{prompt}"
    }
  ]
)

choices = output.get('choices', None)
if (choices is None) or len(choices) < 1:
  print("Failure, unable to generate code. Exiting...")
  exit()

first = choices[0]

message = first.get('message', None)
if (message is None) or len(message) < 1:
  print("Response is illegible. Exiting...")
  exit()

content = message.get('content', None)
if content is None:
  print("No content detected. Exiting...")
  exit()

if content.endswith("```") and '```python\n' in content:
  python_code = content.split('```python\n')[1].split("```")[0]
  print(python_code)

  # AI safety. Warning to user. Do not press y if the AI is trying to do unsafe things.
  if input("^ PYTHON DETECTED ABOVE, RUN IT? (y/n)").lower() == 'y':
    my_stdout = StringIO()
    try:
      with redirect_stdout(my_stdout):
        exec(python_code)
      result = my_stdout.getvalue()
      print(result)
    except Exception as e:
      print(f'The following error occurred:\n\n{e}')
