import os
import random
import sys
from sys import argv
from typing import Literal


def padded_number_str(n: int):
    return f"{n:09d}"


def get_cache_filename(filename: str):
    return filename.lower().replace(".", "_") + ".fortune_cache"


def maybe_make_cache(filename: str, cache_filename: str, force: bool = False):
    if force:  # oh gotta be careful with this!
        os.remove(cache_filename)

    if os.path.exists(cache_filename):
        if os.path.getmtime(filename) < os.path.getmtime(cache_filename):
            return False

    with open(filename, "r", encoding="utf-8") as input_f:
        with open(cache_filename, "w", encoding="utf-8") as output_f:
            # for line in input_f:  # skip empty lines at the top
            #     if line.strip():
            #         break
            #     fstart_offset += len(line)

            # fend_offset = fstart_offset

            # read line by line and split by '%' on a single line
            # 1. fortunes might be multiline
            # 2. there might be multiple consecutive lines of '%' (aka fortunes can be empty)

            # fortune_str = ""

            mode: Literal["content", "skip"] = "content"
            line = input_f.readline()

            # start/end offsets for fortune in file `filename`
            fortune_start = 0
            file_read_position = 0

            while True:
                # print(f"line: {line!r}")

                file_read_position += len(line)

                if mode == "skip":
                    if line == "":  # EOF
                        break

                    if line.strip() == "%":
                        line = input_f.readline()
                        continue

                    if not line.strip():
                        line = input_f.readline()
                        continue

                    mode = "content"
                    fortune_start = file_read_position - len(line)

                if mode == "content":
                    # EOF or separator
                    if line == "" or line.strip() == "%":
                        fortune_end = file_read_position - len(line)

                        # debug only
                        # print(f"{fortune_start, fortune_end}")

                        # debug only
                        # print(f"{len(fortune_str)} -> {fortune_str}\n\n")
                        # fortune_str = ""

                        output_f.write(f"{fortune_start},{fortune_end}\n")

                        if line == "":  # handled last fortune, we're at EOF
                            break

                        mode = "skip"

                    # actual content
                    else:
                        # debug only
                        # fortune_str += line

                        # nothing to do so far, we've recorded fortune_start already
                        pass

                line = input_f.readline()

    # update the fortune count

    return True


def get_fortunes_with_cache(filename: str, cache_filename: str):
    random_fortune_offsets = (0, 0)
    with open(cache_filename, "r", encoding="utf-8") as cache_f:
        lines = cache_f.readlines()
        rnd = random.randint(0, len(lines) - 1)
        # print(f"rnd = {rnd}")
        offsets = lines[rnd].strip().split(",")
        # print(f"line = {offsets}")
        random_fortune_offsets = (int(offsets[0]), int(offsets[1]))

    with open(filename, "r", encoding="utf-8") as f:
        f.seek(random_fortune_offsets[0], os.SEEK_SET)
        buf = f.read(random_fortune_offsets[1] - random_fortune_offsets[0])

        print(buf.strip())  # cut trailing whitespace and newlines


if __name__ == "__main__":
    if len(argv) < 2:
        print("expected 1 argument, filename")
        sys.exit(1)

    filename = argv[1]
    if not os.path.exists(filename):
        print(f"file does not exist: {filename}")
        sys.exit(1)

    cache_filename = get_cache_filename(filename)

    maybe_make_cache(filename, cache_filename)

    try:
        get_fortunes_with_cache(filename, cache_filename)
    except OSError as e:
        print(f"error reading file {filename}: {e}")
    except BaseException as e:  # python errors or cache is invalid
        print(f"some internal error: {e}, will rebuild the cache and try again")
        pass

    maybe_make_cache(filename, cache_filename, force=True)
    get_fortunes_with_cache(filename, cache_filename)
