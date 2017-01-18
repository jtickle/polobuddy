def genError(path, expected, value):
    return "At " + path + " expected " + expected + ", got " + str(value)
def passthru(raw=None, path=""):
    if(raw is None):
        raise TypeError('Expected any value; got None')
    return raw

def fail(raw=None, path=""):
    raise TypeError(genError(path, 'no value', raw))

def makeTypeEnsurer(f, tstr):
    def ensurer(raw=None, path=""):
        try:
            return f(raw)
        except TypeError:
            raise TypeError(genError(path, tstr, raw))
    ensurer.f = f
    ensurer.tstr = tstr
    return ensurer

typeInt = makeTypeEnsurer(int, 'int')
typeFloat = makeTypeEnsurer(float, 'float')
typeString = makeTypeEnsurer(str, 'str')

def listOf(raw=[], path="", ensurer=passthru):
    if(not isinstance(raw, list)):
        raise TypeError(genError(path, 'list', raw))
    ret = []
    i = 0
    for v in raw:
        sub = path + "[" + str(i) + "]"
        ret.append(ensurer(raw=v, path=sub))
        i += 1
    return ret

def dictOf(raw={}, path="", ensurers={}, ensureRest=passthru):
    if(not isinstance(raw, dict)):
        raise TypeError(genError(path, 'dict', raw))
    ret = {}
    for k in raw:
        sub = path + "[" + k + "]"
        if(k not in ensurers.keys()):
            ret[k] = ensureRest(raw=raw[k],path=sub)
        else:
            ret[k] = ensurers[k](raw=raw[k], path=sub)
    return ret
