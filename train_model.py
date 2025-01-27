from pathlib import Path
from collections import Counter
from itertools import dropwhile
import re
import pickle
import math

def get_stop_words():
    stop_words = []
    filepath = Path('aclImdb/stopwords.txt').read_text()
    return re.split('\s+', filepath)


def prepare_text(text):
    return re.split('\s+', re.sub(r'[^\w\s]','', text).lower())


def prepare_data(directory):
    data = []
    dirpath = Path(directory)
    assert(dirpath.is_dir())
    for x in dirpath.iterdir():
        if x.is_file() and re.search('^\d+?_([1-9]|10)\.txt$', x.name):
            data.append(re.split('\s+',
            re.sub(r'[^\w\s]','',Path(x).read_text(errors='ignore')).lower()))
        elif x.is_dir():
            data.extend(prepare_data(x))
    return data


def remove_uncommon_words(counter):
    for key, count in dropwhile(lambda key_count: key_count[1] > 10, counter.most_common()):
        del counter[key]
    return counter


def remove_stop_words(counter):
    for word in stop_words:
        del counter[word]
    return counter


def make_counter(array_of_arrays):
    counter = Counter()
    for review in array_of_arrays:
        counter.update(review)
    remove_uncommon_words(counter)
    remove_stop_words(counter)
    return counter


def get_word_weight():
    pos_word_weights = 0
    neg_word_weights = 0
    for word in counter_all_reviews:
        pos_word_weights += (counter_pos_reviews.get(word, 0) +
                1)
        neg_word_weights += (counter_neg_reviews.get(word, 0) +
                1)
    return pos_word_weights, neg_word_weights


def get_loglikelihood():
    pos_word_weights, neg_word_weights = get_word_weight()
    alpha = 12
    pos_loglikelihood = dict()
    neg_loglikelihood = dict()
    for word in counter_all_reviews:
        pos_loglikelihood[word] = math.log((counter_pos_reviews.get(word, 0) +
            alpha) /
            pos_word_weights)
    for word in counter_all_reviews:
        neg_loglikelihood[word] = math.log((counter_neg_reviews.get(word, 0) +
            alpha) /
            neg_word_weights)
    return pos_loglikelihood, neg_loglikelihood


def save_obj(obj, name):
    with open('model_values/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('model_values/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def save_model_values():
    # Logprior. Probability of an arbritrary review being positive or negative. Using log.
    pos_logprior = math.log(len(pos_reviews) / len(all_reviews))
    neg_logprior = math.log(len(neg_reviews) / len(all_reviews))
    save_obj(pos_logprior, 'pos_logprior')
    save_obj(neg_logprior, 'neg_logprior')

    # Loglikelihoods. Looks at every word left in the training set and
    # calculates a probability of the word occuring in positive and  negative
    # reviews. Using log.
    pos_loglikelihood, neg_loglikelihood = get_loglikelihood()
    save_obj(pos_loglikelihood, 'pos_loglikelihood')
    save_obj(neg_loglikelihood, 'neg_loglikelihood')
    

def get_prediction(review):
    pos_prediction = 0
    neg_prediction = 0
    for word in review:
        if word in (pos_loglikelihood or neg_loglikelihood):
            pos_prediction += ((pos_logprior) +
                    (pos_loglikelihood.get(word)))
            neg_prediction += ((neg_logprior) +
                    (neg_loglikelihood.get(word)))
    if max(pos_prediction, neg_prediction) is pos_prediction:
        return 1
    elif max(pos_prediction, neg_prediction) is neg_prediction:
        return 0
    else:
        print('Something went wrong when predicting class of: ' + review)


def calculate_error():
    correct_pos_prediction = 0
    correct_neg_prediction = 0

    for review in pos_test_reviews:
        if (get_prediction(review) == 1):
            correct_pos_prediction += 1

    for review in neg_test_reviews:
        if (get_prediction(review) == 0):
            correct_neg_prediction += 1

    print("Predicted correctly on: " + str(correct_pos_prediction) + " out of "
            + str(len(pos_reviews)) + " positive reviews")
    print("Accuracy for positive reviews: " + str(correct_pos_prediction /
        len(pos_reviews)))
    print("Predicted correctly on: " + str(correct_neg_prediction) + " out of "
            + str(len(neg_reviews)) + " negative reviews")
    print("Error rate for negative reviews: " + str(correct_neg_prediction /
        len(neg_reviews)))
    print('Precision: ' + str(correct_pos_prediction / (correct_pos_prediction
        + (len(neg_reviews) - correct_neg_prediction))))
    print('Recall: ' + (str(correct_pos_prediction / (correct_pos_prediction +
        (len(pos_reviews))
        - correct_pos_prediction))))
    print('Accuracy: ' + str((correct_pos_prediction + correct_neg_prediction) /
            (len(pos_reviews) + len(neg_reviews))))


if __name__ == '__main__':
    stop_words = get_stop_words()

    # Every review. Array of arrays. Punctuation removed. Everything is lower case.
    pos_reviews = prepare_data('aclImdb/train/pos')
    neg_reviews = prepare_data('aclImdb/train/neg')
    all_reviews = pos_reviews + neg_reviews

    pos_test_reviews = prepare_data('aclImdb/test/pos')
    neg_test_reviews = prepare_data('aclImdb/test/neg')

    # Create Counters and remove stop words and uncommon words.
    counter_all_reviews = make_counter(all_reviews)
    counter_pos_reviews = make_counter(pos_reviews)
    counter_neg_reviews = make_counter(neg_reviews)

    # This line  can be ccommented out if no changes has been made to the
    # calculation of loglikelihoods. Doing so will decrease the run time.
    save_model_values()

    # Load loglikelihood for each word that is left in training set from file.
    pos_loglikelihood = load_obj('pos_loglikelihood')
    neg_loglikelihood = load_obj('neg_loglikelihood')
    pos_logprior = load_obj('pos_logprior')
    neg_logprior = load_obj('neg_logprior')

    # Using Multinomial Naive Bayes to calculate prediction on 25k test
    # reviews. Prints error rate.
    print("Calculating test reviews ...")
    calculate_error()


