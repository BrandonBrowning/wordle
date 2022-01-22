
def max_by(iterable, scorer):
    iterator = iter(iterable)
    result = next(iterator)
    result_score = scorer(result)
    for item in iterator:
        score = scorer(item)
        if score > result_score:
            result = item
            result_score = score
    return result