from pathlib import Path
import string
import re


data = []


def prepare_data(directory):
    dirpath = Path(directory)
    assert(dirpath.is_dir())
    for x in dirpath.iterdir():
        if x.is_file() and re.search('^\d+?_[1-9]\.txt$', x.name):
            data.append(Path(x).read_text(errors='ignore'))
        elif x.is_dir():
            data.extend(prepare_data(x))
    return data

# Prints every file like this: PosixPath('aclImdb/train/pos/4290_9.txt')
# pprint(prepare_data('aclImdb'))

prepare_data('aclImdb')

print(data[3])

