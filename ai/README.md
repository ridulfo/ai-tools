# ai

A local LLM-based command line program. It takes a prompt as an argument and can operate on what it reads from stdin (piped).

## Example

`wget -qO- nicolo.se | ai -m model.gguf "What does it say in on this website?"`

> This website appears to be a personal portfolio and blog website of an individual named Nicolo. The website has several sections, including "about", "thoughts", "blog", and "projects". The homepage lists these categories in a navigation menu.

## Getting started

Obtain a model following [these instructions](https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#obtaining-and-using-the-facebook-llama-2-model).

## Usage

```
ai -h
usage: ai [-h] [-n N] [--temperature TEMPERATURE] [--context CONTEXT] [--model MODEL] [--verbose] prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  -n N
  --temperature TEMPERATURE, -t TEMPERATURE
  --context CONTEXT, -c CONTEXT
  --model MODEL, -m MODEL
  --verbose, -v
```

## Bonus

There is a [bonus script](ai/web2md) that takes a url as its first argument and returns a simplified markdown version of it. This can be used to fetch a website and then give the content to `ai`.

**Usage:**
`./web2md https://nicolo.se | ai -m model.gguf "What does it say in on this website?"`
