def count_distintc_items(l: list[str]):
    r: dict[str, int] = {}
    for v in l:
        r[v] = r.get(v, 0) + 1
    return r


def trigrams_split(s: str) -> list[str]:
    res = []
    wlist = s.split(" ")
    offset = 0
    for word in wlist:
        res.extend([(word[x : x + 3], offset + x) for x in range(len(word) - 2)])
        offset += len(word) + 1  # space

    return res


def trigrams(s: str):
    print(f"source: '{s}'")

    trg = trigrams_split(s)
    print(trg)

    counted = count_distintc_items(trg)
    print(f"counted: {counted}")


if __name__ == "__main__":
    trigrams("mama mylla ramooo1")
    trigrams("mama mylla ramoooooo1 ram")
