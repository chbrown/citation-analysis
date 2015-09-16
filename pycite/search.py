# importing division from __future__ only affects divisions done in this module
from __future__ import division
import math
import heapq
from collections import defaultdict
from operator import itemgetter

get0 = itemgetter(0)
get1 = itemgetter(1)


def _iter_hashtable(hashtable, document_count):
    '''
    `hashtable` will probably be a defaultdict(list), but can be any dict-like
    mapping from tokens to document ids.

    Scoring:

    If a token is a common term, e.g., 'proceedings', it will be discounted
    because the number of ids matching that token will be higher. If a token is
    a name, e.g., 'mccallum', it will have fewer matching document ids, and a
    proportionally higher score.

    `document_count` is used to modulate the score for all document ids
    matching a given token. The score is basically the (I)DF in TF-IDF, using
    the formula: math.log(document_count / len(ids))

    This function yields (token, [(id, score)]) tuples where all the scores
    will be the same for a given token. The list of (id, score) pairs will be
    sorted by id, and the scores will all be identical in a given list. There
    may be duplicate ids in the list.
    '''
    for token, ids in hashtable.iteritems():
        score = math.log(document_count / len(ids))
        yield token, sorted((id, score) for id in ids)


def sumby(iterable, keyfunc, valfunc):
    '''
    Like itertools.groupby, but with the special purpose of summing by key,
    and thus more lightweight.

    list(sumby(iter([('a', 1), ('b', 2), ('b', 3), ('c', 4)]), get0, get1))
    list(sumby(iter([('a', 1)]), get0, get1))
    list(sumby(iter([]), get0, get1))
    '''
    # initialize
    initial_item = next(iterable)
    curr_key = keyfunc(initial_item)
    curr_total = valfunc(initial_item)
    # run
    for item in iterable:
        key = keyfunc(item)
        if key == curr_key:
            curr_total += valfunc(item)
        else:
            yield curr_key, curr_total
            curr_key = key
            curr_total = valfunc(item)
    yield curr_key, curr_total


class InvertedIndex(object):
    def __init__(self, hashtable):
        '''
        `hashtable` should be a mapping from tokens to lists of sorted
        (id, score) tuples.
        '''
        self.hashtable = hashtable

    @classmethod
    def from_documents(cls, id_tokens_iterable):
        '''
        Each item in `id_tokens_iterable` should be an (id, tokens) tuple.
        '''
        hashtable = defaultdict(list)
        # hashtable is a mapping from tokens to lists of documents ids
        document_count = 0
        for id, tokens in id_tokens_iterable:
            document_count += 1
            for token in tokens:
                hashtable[token].append(id)
        # now prepare that hashtable for faster lookup
        sorted_hashtable = dict(_iter_hashtable(hashtable, document_count))
        return cls(sorted_hashtable)

    def search(self, tokens):
        '''
        yields (id, score) tuples for each document id matching one of the
        tokens. If a single document matches multiple tokens, the scores for
        each match are summed, so that ids are not repeated.

        Each document score is normalized by dividing by the total number of
        tokens.
        '''
        ids_scores_iter = (self.hashtable[token] for token in tokens)
        # see https://docs.python.org/2/library/heapq.html for the merge part
        for id, total_score in sumby(heapq.merge(*ids_scores_iter), get0, get1):
            yield id, total_score / len(tokens)
