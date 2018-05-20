from pathlib import Path
from collections import Counter
from itertools import dropwhile
import re
import pickle
import math

stop_words = Path('aclImdb/stopwords.txt').read_text()

def prepare_data(directory):
    data = []
    dirpath = Path(directory)
    assert(dirpath.is_dir())
    for x in dirpath.iterdir():
        if x.is_file() and re.search('^\d+?_([1-9]|10)\.txt$', x.name):
            data.append(re.split('\s+', re.sub(r'[^\w\s]','',Path(x).read_text(errors='ignore')).lower()))
        elif x.is_dir():
            data.extend(prepare_data(x))
    return data

# Every review. Array of arrays. Punctuation removed. Everything is lower case.
pos_reviews = prepare_data('aclImdb/train/pos')
neg_reviews = prepare_data('aclImdb/train/neg')
all_reviews = pos_reviews + neg_reviews

# Logprior. Probability of an arbritrary review being positive or negative. Using log.
pos_logprior = len(pos_reviews) / len(all_reviews)
neg_logprior = len(neg_reviews) / len(all_reviews)

def remove_uncommon_words(counter):
    for key, count in dropwhile(lambda key_count: key_count[1] >= 10, counter.most_common()):
        del counter[key]
    return counter


def make_counter(array_of_arrays):
    counter = Counter()
    for review in array_of_arrays:
        counter.update(review)
    return remove_uncommon_words(counter)


print(make_counter(pos_reviews).most_common()[:-1])