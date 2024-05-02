#! env/bin/python3

import sys
from llama_cpp import Llama
import argparse
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'ai-tool-model-path.txt')

def set_model(model_path: str):
    with open(CONFIG_FILE, 'w') as f:
        f.write(model_path)
    print("Created config file at:", CONFIG_FILE)
    print("Model path set to:", model_path)
    print("You can now use the 'ai' command to interact with the model.")
    sys.exit(0)

def main():
    if len(sys.argv) == 3 and sys.argv[1] == "set-model":
        set_model(sys.argv[2])

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("prompt", type=str)
    arg_parser.add_argument("-n", type=int, required=False, default=1000)
    arg_parser.add_argument("--temperature", "-t", type=float, required=False, default=0.9)
    arg_parser.add_argument("--context", "-c", type=int, required=False, default=1024)
    arg_parser.add_argument("--model", "-m", type=str, required=False)
    arg_parser.add_argument("--verbose", "-v", action="store_true", required=False, default=False)

    args = arg_parser.parse_args()

    # Read model path from config file if not provided as an argument
    if not args.model and os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            args.model = f.read().strip()
    if not args.model:
        print("No model specified. Use 'ai set-model <model-path>' to set the model path, or provide it with the -m flag.")
        sys.exit(1)

    llm = Llama(
        model_path=args.model,
        verbose=False,
        use_mmap=False,
        use_mlock=True,
        n_ctx=args.context,
    )

    stdin = ""
    if not sys.stdin.isatty(): # If the program is running in a pipe
        stdin = sys.stdin.read().strip()

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
          {
              "role": "user",
              "content": args.prompt + ("\nAdditional context: '" + stdin + "'" if len(stdin)>0 else "")
          }
    ]

    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=args.n,
        stream=True,
        temperature=args.temperature,
    )

    if args.verbose:
        print("Full user message to to model:")
        print(messages[1]["content"])
        print()


    for response in stream:
        response = response["choices"][0]["delta"] # type: ignore
        if "content" in response:
            print(response["content"], end="", flush=True) # type: ignore
    print()


if __name__ == "__main__":
    main()
