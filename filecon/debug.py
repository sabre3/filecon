#debug

import ifilecon

from pathlib import Path

#debug
ifile = ifilecon.IFile('debug/test/test1.txt', 16)

exit()

ifile2 = ifilecon.IFile('debug/test1.txt', 16, hash=b'yWJloUxkew/6XV+XK5rcGTg9/8E6OGzOiqVhpHiDW2I=', size=257, start=69)
#print(ifile.get_peice(2))

#ifile2.add_peice(0, b'lmao')
#ifile2.add_peice(1, b'rofl')

#exit()

#IFileDef.generate_def('debug/test.bin', [ifile])

ifdef = IFileDef('debug/test.bin')
#print(ifdef.ifiles)

print(ifile2.verify())

index = 0
while index <= ifile.maxindex:
    p = ifile.get_peice(index)
    #print(p)
    ifdef.add_peice(ifile2, p)
    index += 1

print(ifile2.verify())



ifile = IFile('debug/test3.txt', 212)







exit()


p = Path('debug/test1.txt')

with open(p, 'rb') as f:
    print(f.read(16))
    f.close()
