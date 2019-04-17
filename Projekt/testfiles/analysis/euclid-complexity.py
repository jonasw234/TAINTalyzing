def euclid(n, m):
    if n > m:
        r = m
        m = n
        n = r
    r = m % n
    while r != 0:
        m = n
        n = r
        r = m % n
    return n
