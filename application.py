def truncate(f):
    s = '%.12f' % f
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*2)[:2]])

print(truncate(12.9))