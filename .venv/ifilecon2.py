# Lol gonna redo this again

import os
import nacl.encoding
import nacl.hash
import nacl.hashlib
import base64
from pathlib import Path

#CONFIG
CRYPTO_BUFF = 8192 #file hasher block read size (how many bytes to load into memory for hashing on each read)
HASH_SIZE = 44 #blake2b b64 hash size in bytes (Don't change unless you modify the blake2b size!)
FILE_EXTENSION = '.def' #the file extension to use for IFile defenitions
MEM_LOAD_SIZE = 16 #the maximum file size in Mb that will be loaded into RAM before it switches to file def read only

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

class IFile:

    #init
    def __init__(s, filepath, generate, psize=512):
        
        s.path = Path(filepath) #filepath
        s.psize = psize #file peice size

        if generate:
            #create definition from file
            s.person = s.path.name.encode('utf8')[:len(s.path.name) - 16] #person string for blake2b
            pass
        else:
            #new file to be contructed
            pass

        #generate definition of file and load into memory if below the thresh-hold
        def generate_def(s):
            pass

class IDef:

    def __init__(s, path, psize):
        s.path = path
        s.psize = psize
        s.person = s.path.name.encode('utf8')[:len(s.path.name) - 16] #person string for blake2b
        s.size = 0
        s.hashlist = []
        s.header = None

    def generate(s):

        size = os.path.getsize(s.path)
        s.size = size

        if size < MEM_LOAD_SIZE * 1048576:
            #load into hashlist
            with open(s.path, 'rb') as f:

                data = f.read(s.psize)
                while data:

                    hash = generate_hash(data, person=s.person)
                    s.hashlist.append(hash)
                    s.header = (s.path.name, generate_hash(filepath=s.path), size, s.psize)
                    data = f.read(s.psize)

                f.close()
        else:
            #create a def file
            def_path = Path(s.path + FILE_EXTENSION)

            file_hash = generate_hash(filepath=s.path)

            #set header
            s.header = (s.path.name, generate_hash(filepath=s.path), size, s.psize)

            #write header
            with open(def_path, 'w') as f:
                f.write(s.path.name+';')
                f.write(file_hash+';')
                f.write(size+';')
                f.write(s.psize+'\n')
                f.close()

            #write hashlist
            with open(s.path, 'rb') as f:
                with open(def_path, 'wb') as d:

                    data = f.read(s.psize)
                    while data:

                        hash = generate_hash(data, person=s.person)
                        d.write(hash)
                        data = f.read(s.psize)
                d.close()
            f.close()

    def load(s, path):
        #load from file path

        #load header:
        with open(path, 'r') as f:
            header = f.readlien().split(';')
            s.header = (header[0], header[1], header[2], header[3])
            s.size = header[2]
            f.close()

        #load hash data only if small enough
        if s.size < MEM_LOAD_SIZE * 1048576:
            with open((path, 'rb')) as f:
                pass

#will take an open file object and skip the header
def skip_head(f):
    pass
