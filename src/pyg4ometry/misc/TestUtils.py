import hashlib as _hl
import subprocess as _sp
import difflib as _dl
import filecmp as _fc
import subprocess as _sp


def md5_file(fname):
    hash_md5 = _hl.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def diffFiles(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        diff = _dl.unified_diff(f1.readlines(), f2.readlines())

        same = True
        for line in diff:
            print(line)
            same = False

        return same


def compareFilesWithAssert(file1, file2):
    print("compare", file1, file2)
    if file1 is not None and file2 is not None:
        diff = _fc.cmp(file1, file2, shallow=False)
        print("compare", diff)
        if not diff:
            assert diffFiles(file1, file2)


def compareNumericallyWithAssert(file1, file2):
    if file1 is not None and file2 is not None:
        r = _sp.run(
            ["numdiff", "-s", ", \n", "-a", "1e-6", str(file1), str(file2)],
            capture_output=True,
        )

        output = r.stdout.decode("utf-8")

        if output.find("equal") != -1:
            pass
        else:
            print(output)

        assert output.find("equal") != -1


def compareMeshInfo(meshInfo1, meshInfo2):
    for k in meshInfo1:
        if type(meshInfo1[k]) is float:
            assert abs(meshInfo1[k] - meshInfo2[k]) < 1e-5
        elif type(meshInfo1[k]) is bool:
            assert meshInfo1[k] == meshInfo2[k]
        elif type(meshInfo1[k]) is int:
            assert meshInfo1[k] == meshInfo2[k]


def compareGdmlNumericallyWithAssert(file1, file2):
    if file1 is not None and file2 is not None:
        r = _sp.run(
            ["numdiff", "-s", ', \n"', "-a", "1e-6", str(file1), str(file2)],
            capture_output=True,
        )

        output = r.stdout.decode("utf-8")

        if output.find("equal") != -1:
            pass
        else:
            print(output)
            # echo reference file
            with open(file1) as f:
                for l in f:
                    print(l)

            with open(file2) as f:
                for l in f:
                    print(l)

        assert output.find("equal") != -1
