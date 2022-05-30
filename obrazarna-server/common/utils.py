import random


def check_attributes(obj, attrs):
    """
    Vrati True, pokud vsechny atributy z `attrs` jsou v objektu `obj` definovany
    a maji nenulovou hodnotu.
    """
    for attr in attrs:
        if hasattr(obj, attr) and getattr(obj, attr, None):
            continue
        return False
    return True


def get_least_used(counts):
    """
    Ze zadaneho slovniku cetnosti ({id1: count1, id2: count2, ...}) vrati to ID,
    ktere se vyskytuje nejmene casto (pokud je takovych vic, tak vybere nahodne
    nektere z nich).
    """
    out = {}
    lowest = None
    for id_, count in counts.items():
        if lowest is None or count < lowest:
            lowest = count
        if count not in out:
            out[count] = []
        out[count].append(id_)

    return random.choice(out[lowest]) if lowest is not None else None


def dict_subset(data, keys):
    """
    Vrati novy slovnik, pouze s klici `keys`.
    """
    return {k: data[k] for k in keys}
