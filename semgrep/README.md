# Semantic grep

- Local semantic search
- Local "database"
- Low code complexity
- Sub 300 lines of code

Because of the sensitive nature of personal files, the number of lines of code will be kept low in order for the project to easily be audited and understood.

The text splitter is still in development. At the moment only markdown files are supported.

## Installation
To install or update semgrep use the following command. It pip-installs from this repository's semgrep directory.
```bash
pip install -U git+https://github.com/ridulfo/ai-tools@main#subdirectory=semgrep
```
To uninstall just run
```bash
pip uninstall semgrep
```


## Usage

```
semgrep -h
usage: Semantic grep [-h] [--path PATH] [-k K] [--index-path INDEX_PATH] [-v] [--no-update] query

A semantic document search

positional arguments:
  query                 The search query.

options:
  -h, --help            show this help message and exit
  --path, -p PATH       The directory to search.
  -k, --top-k K         Return only the top K matches
  --index-path, -i INDEX_PATH
                        Where to store the index
  -v, --verbose         Show debug output
  --no-update           Use existing index without re-indexing files. If no index is found, will exit with 1
```

**Example**

`semgrep "search query" --path document-directory -k 4`

## How it works

### First time
1. Create an empty index by recursively finding all files and hashing their content. The hash-digest will be used as key in the index.
2. For every file, segment and embed the documents
3. Save a cache of the index in the search directory for future searches
4. Run vector similarity search on the embeddings
5. Display the matches

### Other times (when a cache is already present in the search directory)

1. Look for a cached index
2. If the update flag is raised
	1. Create an empty index by recursively finding all files and hashing their content.
	2. For the files that have not changed, move over the embeddings from the cache.
	3. Embed the files that have changed.
3. Save a cache of the index in the search directory for future searches
4. Run vector similarity search on the embeddings
5. Display the matches
