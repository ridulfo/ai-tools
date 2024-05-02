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

    additional_context = ""
    if not sys.stdin.isatty():
        additional_context = "Additional context:\n" + sys.stdin.read()

    prompt = f"""<|im_start|>system
You are a helpful assistant<|im_end|>
<|im_start|>user
{args.prompt}
{additional_context}
<|im_end|>
<|im_start|>assistant
"""

    llm = Llama(
        model_path=args.model,
        verbose=False,
        use_mmap=False,
        use_mlock=True,
        n_ctx=args.context,
    )

    output = llm(
        prompt,
        max_tokens=args.n,
        stream=True,
        stop="<|im_end|>",
        temperature=args.temperature,
    )

    if args.verbose:
        print(prompt)

    for o in output:
        token = o["choices"][0]["text"]  # type: ignore
        print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
