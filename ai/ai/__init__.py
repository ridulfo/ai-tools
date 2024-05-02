#! env/bin/python3

import sys
from llama_cpp import Llama
import argparse


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("prompt", type=str)
    arg_parser.add_argument("-n", type=int, required=False, default=1000)
    arg_parser.add_argument(
        "--temperature", "-t", type=float, required=False, default=0.9
    )
    arg_parser.add_argument("--context", "-c", type=int, required=False, default=1024)
    # TODO add default model
    arg_parser.add_argument("--model", "-m", type=str, required=True)
    arg_parser.add_argument(
        "--verbose", "-v", action="store_true", required=False, default=False
    )

    args = arg_parser.parse_args()

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
