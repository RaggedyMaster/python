import sys
short = "RDpbLfCPsJZ7fiv"
#Post={'Content-Type': 'application/x-www-form-urlencoded','Content-Length': '0'}
Lng = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
try:
    PawD = sys.argv[1]
except IndexError:
    PawD = 'password____'
def encrypt_passwd(a, b, c):
    e = ''
    f, g, h, k, l = 187, 187, 187, 187, 187
    n = 187
    g = len(a)
    h = len(b)
    k = len(c)
    if g > h:
        f = g
    else:
        f = h

    for p in list(range(0, f)):
        n = l = 187
        if p >= g:
            n = ord(b[p])
        else:
            if p >= h:
                l = ord(a[p])
            else:
                l = ord(a[p])
                n = ord(b[p])
        e += c[(l ^ n) % k]
    return e
print encrypt_passwd(short, PawD, Lng )
