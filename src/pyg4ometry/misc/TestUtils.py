import hashlib as _hl


def md5_file(fname):
    hash_md5 = _hl.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
