#! env/bin/python3
import argparse
import hashlib
import logging
import os
import pickle
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logger = logging.getLogger(__name__)

INDEX_FILE_NAME = ".semgrep-index"
HEADING_RE = re.compile(r"^(#+)\s")


@dataclass
class FileState:
    mtime: float
    hash: str


@dataclass
class Index:
    state: Dict[Path, FileState]
    embeddings: Dict[Path, List[np.ndarray]]


def hash_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def has_changed(path: Path, stored_file_state: FileState) -> bool:
    current_mtime = path.stat().st_mtime
    if current_mtime == stored_file_state.mtime:
        return False  # fast path, no need to hash
    return hash_file(path) != stored_file_state.hash  # mtime changed, verify with hash


@dataclass
class Section:
    text: str
    children: List["Section"] = field(default_factory=list)

    @property
    def level(self) -> int:
        m = HEADING_RE.match(self.text)
        return len(m.group(1)) if m else 0

    def append(self, child: "Section"):
        self.children.append(child)


def build_tree(text: str) -> Section:
    CHAPTER_RE = re.compile(r"(?=^#+\s)", re.MULTILINE)
    parts = CHAPTER_RE.split(text)

    root = Section(text="")
    stack = [root]

    for part in parts:
        node = Section(text=part)

        while len(stack) > 1 and stack[-1].level >= node.level:
            stack.pop()
        stack[-1].append(node)
        stack.append(node)

    return root


def walk(section: Section) -> List[str]:
    """Collect chunks from tree - each section alone and with children."""
    chunks = []

    def full_text(section: Section) -> str:
        parts = [section.text] + [full_text(c) for c in section.children]
        return "\n".join(filter(None, parts))

    def _walk(section: Section):
        chunks.append(section.text)
        if section.children:
            chunks.append(full_text(section))
        for child in section.children:
            _walk(child)

    chunks.append(full_text(section))
    for child in section.children:
        _walk(child)

    return chunks


def embed_file(path: Path, model: SentenceTransformer) -> List[np.ndarray]:
    text = path.read_text()
    root = build_tree(text)
    chunks = walk(root)
    return list(model.encode(chunks, show_progress_bar=False))


def save_index(index_path, index):
    with open(index_path, "wb") as f:
        pickle.dump(index, f)


def load_index(index_path):
    with open(index_path, "rb") as f:
        return pickle.load(f)


def search(
    model: SentenceTransformer,
    index: Index,
    query: str,
    n: int = 1,
):
    query_embedding = model.encode([query])[0]

    distances: Dict[Path, Tuple[float, int]] = {}
    for path, embeddings in tqdm(index.embeddings.items(), "Searching..."):
        if not embeddings:
            continue
        best_score = 0.0
        best_chapter = 0
        for chapter_idx, chapter_embedding in enumerate(embeddings):
            score = float(1 - cosine(query_embedding, chapter_embedding))
            if score > best_score:
                best_score = score
                best_chapter = chapter_idx
        distances[path] = (best_score, best_chapter)

    sorted_distances = sorted(distances.items(), key=lambda x: x[1][0], reverse=True)

    for filename, distance in sorted_distances[:n]:
        text = filename.read_text()
        root = build_tree(text)
        chunks = walk(root)
        chapter_idx = distance[1]
        if chapter_idx < len(chunks):
            print(f"{filename} with score {distance[0]}")
            print(chunks[chapter_idx], end="\n\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Semantic grep", description="A semantic document search"
    )

    parser.add_argument("query", type=str, help="The search query.")

    parser.add_argument(
        "--path", "-p", help="The directory to search.", default=".", type=str
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=None,
        metavar="K",
        help="Return only the top K matches",
    )

    parser.add_argument(
        "--index-path",
        "-i",
        help="Where to store the index",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show debug output"
    )

    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Use existing index without re-indexing files. If no index is found, will exit with 1",
    )
    return parser


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(message)s",  # plain, no "INFO:root:" prefix
    )


def main():
    args = build_parser().parse_args()
    setup_logging(args.verbose)

    if not args.index_path:
        args.index_path = args.path
    index_path = os.path.join(args.index_path, INDEX_FILE_NAME)
    index_exists = os.path.exists(index_path)

    if index_exists:
        logger.debug(f"Index exists at {index_path}. Updating it.")
        index = load_index(index_path)
    elif args.no_update:
        logger.error(f"No index found at {index_path} and --no-update passed")
        exit(1)
    else:
        logger.debug(f"No index found at {index_path}. Generating one...")
        index = Index(state={}, embeddings={})

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2", local_files_only=True
    )
    all_files = list(Path(args.path).rglob("*.md"))
    all_file_set = set(all_files)

    to_reindex = []
    for path in all_files:
        if path not in index.state:
            index.state[path] = FileState(
                mtime=path.stat().st_mtime, hash=hash_file(path)
            )
            to_reindex.append(path)
        elif has_changed(path, index.state[path]):
            to_reindex.append(path)

    logger.debug(f"{len(to_reindex)} files to reindex")

    for path in list(index.state.keys()):
        if path not in all_file_set:
            del index.state[path]
            index.embeddings.pop(path, None)

    for i, path in enumerate(tqdm(to_reindex, "Indexing...")):
        logger.debug(f"Re-embedding {path}")
        index.embeddings[path] = embed_file(path, model)
        index.state[path] = FileState(mtime=path.stat().st_mtime, hash=hash_file(path))
        if (i + 1) % 10 == 0:
            save_index(index_path, index)

    if to_reindex:
        save_index(index_path, index)

    search(model, index, args.query, args.top_k or 1)


if __name__ == "__main__":
    main()
