import os
import sys


def _ensure_backend_on_path() -> None:
    # Allow tests to import the package from backend/src
    repo_root = os.path.dirname(os.path.abspath(__file__))
    backend_src = os.path.join(repo_root, "..", "backend", "src")
    backend_src = os.path.normpath(backend_src)
    if backend_src not in sys.path:
        sys.path.insert(0, backend_src)


_ensure_backend_on_path()


