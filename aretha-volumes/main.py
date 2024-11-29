from pathlib import Path
import logging
from uuid import uuid4
import tarfile
from tempfile import TemporaryDirectory
import argparse

from pathlib import Path
from timeit import default_timer


logging.basicConfig(level=logging.INFO)


class Timer:
    def __init__(self):
        self.ref = default_timer()

    @property
    def delta(self) -> float:
        return default_timer() - self.ref


def main(src: Path):
    logging.info("Tarring `%s`", src)
    with TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / f"{uuid4().hex}.tar"

        timer = Timer()
        with tarfile.open(archive_path, "a") as tar:
            tar.add(src, arcname=".")

        logging.info("Tarred `%s` in %f", src, timer.delta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)

    args = parser.parse_args()

    main(args.src)
