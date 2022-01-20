#debug file

with open('test.def', 'rb') as f:
    print(f.readline())
    print(f.read(4))
    f.close()


# the readline also includes the \n in binary mode
