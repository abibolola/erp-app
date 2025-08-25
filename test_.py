s = "anagram"
t = "nagaram"

def ident(x, y):
    if x[::1] == y:
        return True
    return False