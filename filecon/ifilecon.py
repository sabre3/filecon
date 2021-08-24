#A file constructor module that creates files from out of order peices using a definition file
#Creator and Maintainer: sabre3
#Release: v0.1.1

#module import examples:
#import filecon.ifilecon as ifc
#from filecon.ifilecon import IFile, IFileDef

#CONFIG
CRYPTO_BUFF = 8192 #hasher file block read size
HASH_SIZE = 44 #blake2b b64 hash size in bytes (Don't change unless you modify the black2b size!)

#Python modules
import os
import nacl.encoding
import nacl.hash
import nacl.hashlib
import base64
import math
from ruamel.yaml import YAML
from pathlib import Path

#generates a blake2b hash of binary data or file with an optional person
def generate_hash(data=None, filepath=None, person=b''):
        HASHER = nacl.hash.blake2b
        S_ENCODER = nacl.encoding.Base64Encoder
        F_ENCODER = base64.b64encode #no easy way to set other encoders for file hash, plus B64 uses least space
        
        if filepath != None:
            #hash file
            with open(filepath, 'rb') as f:
                advanced_hasher = nacl.hashlib.blake2b(person=person)
                
                for chunk in iter(lambda: f.read(CRYPTO_BUFF), b''):
                    advanced_hasher.update(chunk)
            
            advanced_hasher = F_ENCODER(advanced_hasher.digest())
            return advanced_hasher

        elif data != None:
            #hash string
            digest = HASHER(data, encoder=S_ENCODER, person=person)
            return digest

#class that handles def of ifile objects
class IFileDef:
    
    #init
    def __init__(s, defpath):
        
        s.path = Path(defpath)
        s.ifiles = []

        #load header details from bin folder and init IFile objects into list
        with open(s.path, 'rb') as f:
            data = f.read(1)

            while data:
                if data == b':':
                    #new Ifile def
                    ifile_bin = b''
                    d_count = 0 #delimiter count
                    while data:
                        data = f.read(1)
                        ifile_bin = ifile_bin + data

                        if data == b';':
                            d_count += 1
                        if d_count == 4:
                            ifile =IFileDef.__create_ifile(ifile_bin, f.tell() + 1) #plus one because hashes start on next byte
                            s.ifiles.append(ifile)
                            break

                data = f.read(1)

    #add peice to file
    def add_peice(s, ifile, peice):

        p_hash = generate_hash(data=peice, person=ifile.person)

        with open(s.path, 'rb') as f:
            f.seek(ifile.start)

            index = 0
            hashr = f.read(HASH_SIZE)
            while index <= ifile.maxindex:

                if p_hash == hashr:
                    ifile.add_peice(index, peice)

                hashr = f.read(HASH_SIZE)
                index += 1

            f.close()

    #creates ifile object from bin data header
    @staticmethod
    def __create_ifile(bindata, start):
        data = bindata.decode('utf8').split(';')
        
        hashr = data[0]
        name = data[1]
        size = int(data[2])
        psize = int(data[3])

        ifile = IFile(name, psize, hashr, size, start)
        return ifile

    #create ifile def.bin from ifile objects
    @staticmethod
    def generate_def(defpath, ifiles):
        path = Path(defpath)

        with open(path, 'wb') as f:

            for ifile in ifiles:

                #write header (long boi ))))) )
                head = b':' + ifile.hash + b';' + str(ifile.path).encode('utf8') + b';' + str(ifile.size).encode('utf8') + b';' + str(ifile.psize).encode('utf8') + b';'
                f.write(head)

                #update start byte
                ifile.start = f.tell()

                #write hashlist
                index = 0
                while index <= ifile.maxindex:
                    p_hash = ifile.get_hash(index)
                    f.write(p_hash)
                    index += 1

            f.close()

#class that creates ifiles capable of peice contruction
class IFile:
    
    #init
    def __init__(s, filepath, psize, hash=b'', size=0, start=0):
        
        s.path = Path(filepath) #filepath
        s.psize = psize #file peice size
        s.start = start #start index of hashes in def
        s.person = s.path.name.encode('utf8')[:len(s.path.name) - 16] #person string for blake2b

        if s.path.exists():
            s.size = s.path.stat().st_size
            s.hash = generate_hash(filepath=s.path, person=s.person)
        else:
            s.size = size #file size
            s.hash = hash #file hash

            with open(s.path, 'wb') as f:
                f.seek(s.size - 1) #minus 1 for single byte write space
                f.write(b'0')
                f.close()

        #max index value for reading hashes or peices
        #print(math.ceil(s.size / s.psize))
        s.maxindex = math.ceil(s.size / s.psize)
    
    #returns peice at given index
    def get_peice(s, index):

        with open(s.path, 'rb') as f:
            f.seek(index * s.psize)
            p = f.read(s.psize)
            f.close()

        return p

    #returns hash at given index
    def get_hash(s, index):

        with open(s.path, 'rb') as f:
            f.seek(index * s.psize)
            p = f.read(s.psize)
            hashr = generate_hash(p, person=s.person)
            f.close()

        return hashr

    #adds peice to file at index
    def add_peice(s, index, peice):

        with open(s.path, 'r+b') as f:
            f.seek(index * s.psize)
            f.write(peice)
            f.close()

    #verifies file compared to def hash
    def verify(s):
        return generate_hash(filepath=s.path, person=s.person) == s.hash



