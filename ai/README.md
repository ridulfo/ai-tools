# ai

A local LLM-based command line program. It takes a prompt as an argument and can operate on what it reads from stdin (piped).

## Example

`wget -qO- nicolo.se | ai -m model.gguf "What does it say in on this website?"`

> This website appears to be a personal portfolio and blog website of an individual named Nicolo. The website has several sections, including "about", "thoughts", "blog", and "projects". The homepage lists these categories in a navigation menu.

## Getting started
1. Obtain a model following [these instructions](https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#obtaining-and-using-the-facebook-llama-2-model).
2. Install using the following command. It pip-installs from this repository's ai directory.
```bash
pip install -U git+https://github.com/ridulfo/ai-tools@main#subdirectory=ai
```
> [!NOTE]
> To uninstall just run
> ```bash
> pip uninstall ai
> ```

3. (optional) To not have to specify the model path every time, you can set it using `ai set-model path/to/model`. 

## Usage

```
ai -h
usage: ai [-h] [-n N]  [-h] [-n N] [--temperature TEMPERATURE] [--context CONTEXT] [--model MODEL] [--verbose] [--interactive] prompt

positional arguments:
  prompt                The prompt to send to the model

options:
  -h, --help            show this help message and exit
  -n N                  The maximum number of tokens to generate
  --temperature TEMPERATURE, -t TEMPERATURE
                        The temperature to use when generating text
  --context CONTEXT, -c CONTEXT
                        The context window size to use when generating text
  --model MODEL, -m MODEL
                        The path to the model to use. Can be set permanently with 'ai set-model <model-path>'
  --verbose, -v         Print additional information about the request
  --interactive, -i     Run in interactive mode```

## Bonus

There is a [bonus script](ai/web2md) that takes a url as its first argument and returns a simplified markdown version of it. This can be used to fetch a website and then give the content to `ai`.

**Usage:**
`./web2md https://nicolo.se | ai -m model.gguf "What does it say in on this website?"`
