# from https://github.com/micropython/micropython-lib/blob/master/python-stdlib/functools/functools.py
def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value
