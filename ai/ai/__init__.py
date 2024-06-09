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
    arg_parser.add_argument("prompt", type=str, help="The prompt to send to the model")
    arg_parser.add_argument("-n", type=int, required=False, default=1000, help="The maximum number of tokens to generate")
    arg_parser.add_argument("--temperature", "-t", type=float, required=False, default=0.9, help="The temperature to use when generating text")
    arg_parser.add_argument("--context", "-c", type=int, required=False, default=1024, help="The context window size to use when generating text")
    arg_parser.add_argument("--model", "-m", type=str, required=False, help="The path to the model to use. Can be set permanently with 'ai set-model <model-path>'")
    arg_parser.add_argument("--verbose", "-v", action="store_true", required=False, default=False, help="Print additional information about the request")
    arg_parser.add_argument("--interactive", "-i", action="store_true", required=False, default=False, help="Run in interactive mode")

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

    # Get piped input
    stdin = ""
    if not sys.stdin.isatty(): # If the program is running in a pipe
        stdin = sys.stdin.read().strip()
        sys.stdin = open('/dev/tty')

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
          {
              "role": "user",
              "content": args.prompt + ("\nAdditional context: '" + stdin + "'" if len(stdin)>0 else "")
          }
    ]

    if args.verbose:
         print("Full user message to to model:")
         print(messages[1]["content"])
         print()

    while True:

        stream = llm.create_chat_completion(
            messages=messages,
            max_tokens=args.n,
            stream=True,
            temperature=args.temperature,
        )

        full_response = ""
        if args.interactive:
            print("AI: ", end="", flush=True)
        for response in stream:
            response = response["choices"][0]["delta"] # type: ignore
            if "content" in response:
                content = response["content"]       # type: ignore
                full_response += content            # type: ignore
                print(content, end="", flush=True)  # type: ignore
        print()

        messages.append({"role": "system", "content": full_response})

        if not args.interactive: # simulate do-while loop
            break

        user_input = input("You: ")
        messages.append({"role": "user", "content": user_input})


if __name__ == "__main__":
    main()
