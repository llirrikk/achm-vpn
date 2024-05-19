import os
from contextlib import contextmanager


@contextmanager
def temporary_file(content, *, filename="temp_file"):
    try:
        with open(filename, "wb") as f:
            f.write(content)
        yield filename
    finally:
        os.remove(filename)
