# filecon
## Python peiced file contructor module

### About
filecon is a file contrcuting module that assembles files by out of order peices using a hash file definition. 
It functions similar to how torrent files are shared. Each file is split into peices and hashed into a definition file.
Using the definition file, the module can reconstruct the file from peices sent in any order.

### Features
- Written in pure python
- Uses [blake2b](https://www.blake2.net/) hashing algorithm
- Automagically applies personalization to blake2b using filenames for better security
- Supports any peice size (specefied in bytes)
- Reduces definition file size by using Base64

### Import examples
```Python
import filecon.ifilecon as ifc
from filecon.ifilecon import IFile, IFileDef
```

### Usage examples
```Python
#create IFile object of exisitng file using 64 byte peices
ifile = IFile('myfile.txt', 64)

#create IFile object of new file to be constructed 
ifile2 = IFile('test/myfile.txt', ifile.psize, hash=ifile.hash, size=ifile.size, start=ifile.start)

#generate a definition file from a list of IFIle objects
IFIleDef.generate_def('def.bin', [ifile])

#create a definiton object that handles cretaing files from peices
ifiledef = IFileDef('def.bin')

#add a peice to a new ifile
ifiledef.add_peice(ifile2, b'my totally legit 64 byte looking file peice')
```

### Planned improvments
- Allow hash data to be loaded directly into memory for smaller files (and faster peice adding)
- Improve definition file compression for hashes that are the same (performance improvemnet for smaller files)
- Add multithreading support
- Use proper python type hints  


