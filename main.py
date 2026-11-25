"""Worst Superpower — one line, at most 140 characters.

The entry invents a superpower and makes plain, in the same breath, why
it is useless: breathing underwater sounds heroic until the fine print
says the only water it works on is water already inside you. The power
achieves nothing — you cannot drown in water you have drunk, and you
cannot use it anywhere it would matter.

Deterministic, stdlib only, no network. Writes the line to
$MAKEFUN_OUTPUT_DIR/entry.txt atomically, asserts the 1-140 character
single-line gate, and verifies the written bytes by read-back.
"""

import os
import sys

LINE = "I can breathe underwater, but only water I've already drunk."

MAX_CHARS = 140


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"

    text = LINE
    if not (1 <= len(text) <= MAX_CHARS):
        print(f"entry is {len(text)} characters, must be 1-{MAX_CHARS}",
              file=sys.stderr)
        return 1
    if text != text.strip() or "\n" in text or "\r" in text:
        print("entry must be exactly one line with no surrounding whitespace",
              file=sys.stderr)
        return 1

    # Clean only the contents of the output dir; never remove the dir itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            for sub in os.listdir(path):
                os.remove(os.path.join(path, sub))
            os.rmdir(path)
        else:
            os.remove(path)

    target = os.path.join(out_dir, "entry.txt")
    tmp = target + ".tmp"
    data = text.encode("utf-8")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, target)

    with open(target, "rb") as fh:
        back = fh.read()
    if back != data:
        print("read-back mismatch", file=sys.stderr)
        return 1
    if back.decode("utf-8") != text:
        print("read-back mismatch after UTF-8 decode", file=sys.stderr)
        return 1
    if not (1 <= len(text) <= MAX_CHARS):
        print("read-back failed the character gate", file=sys.stderr)
        return 1
    print(f"wrote entry.txt ({len(text)} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
