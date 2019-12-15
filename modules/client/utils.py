from PIL import Image
from io import BytesIO

from typing import Dict, List, Any


def print_table(table: Dict[str, List[Any]]):
    cols = []
    lengths = []

    for key in table.keys():
        length = len(key)
        for item in table.get(key):
            item_len = len(str(item))
            if item_len > length:
                length = item_len
        cols.append(key)
        lengths.append(length)

    for key, length in zip(cols, lengths):
        print(("{:<" + str(length) + "} ").format(key), end="")
    print()
    for key, length in zip(cols, lengths):
        print(f"{'=' * length} ", end="")
    print()

    for items in zip(*[items[1] for items in table.items()]):
        for i in range(len(items)):
            print(("{:<" + str(lengths[i]) + "} ").format(items[i]), end="")
        print()


def show_image(buffer: bytes, title: str):
    with BytesIO(buffer) as b:
        b.seek(0)
        frame: Image.Image = Image.open(b)
        frame.show(title)
