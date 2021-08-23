#A file constructor module that creates files from out of order peices (V3)

#CONFIG
CRYPTO_BUFF = 8192 #hasher file read size
HASH_SIZE = 47 #blake2b b64 hash size in bytes

#Python modules
import os
#import cython
import nacl.encoding
import nacl.hash
import nacl.hashlib
import base64
from ruamel.yaml import YAML

#debugging for peices out of order
import random

#Ifile class that manages peices of file
class IFile:
    def __init__(s, filename, ifile_def):
        pass

#handles Ifile def (info and hashes)
class IFileDef:
    def __init__(s, filename, ramload=False):
        s.defname = filename
        s.ramload = ramload
        raw_def = ''
        with open(s.defname, 'r') as f:

            #had to replace with while loop cuz iter block tell()
            line = f.readline()
            while line:
                #print(line)

                if line != 'data:\n':
                    raw_def = raw_def + line
                else:
                    s.data_start = f.tell()
                    break

                line = f.readline()

        yaml = YAML(typ='rt')
        node = yaml.load(raw_def)  
        
        try:
            s.filename = node['filename']
            s.size = node['size']
            s.psize = node['psize']
            s.hash = node['hash']
        except Exception as e:
            print('Invalid IFile def!')
            raise e

        #load hashes into list if ramload is true
        if s.ramload:
            s.hashlist = []
            with open(s.defname, 'rb') as f:
                f.seek(s.data_start)
                data = f.read(HASH_SIZE)
                while data:
                    #print(data)
                    s.hashlist.append(data)
                    data = f.read(HASH_SIZE)
                f.close()

    def get_index(s, peice, person):
    
        indexes = []
        p_hash = generate_hash(data=peice, person=person)
        index = 0

        if s.ramload:

            for hashr in hashes:

                if hashr == p_hash:
                    indexes.append(index)

                index += 1
        else:

            with open(s.defname, 'rb') as f:
                #seek to hashes
                f.seek(s.data_start)

                data = f.read(HASH_SIZE)
                while data:
                    #print(data)
                    if data == p_hash:
                        indexes.append(index)

                    data = f.read(HASH_SIZE)
                    index += 1

                f.close()

        return indexes   

#handles creating and adding peices to file
class FileBuilder:

    def __init__(s, ifile):

        #person for blake2b
        s.person = os.path.basename(ifile.filename).encode('utf8')

        #debug person
        #s.person = b'test1.txt'
        
        #create file
        with open(ifile.filename, 'wb') as f:
            f.seek(ifile.size - 1) #minus 1 for single byte write space
            f.write(b'0')
            f.close()
    
        print('File created at', ifile.filename)

    def add_peice(s, peice):
        
        indexes = ifile.get_index(peice, s.person)

        if len(indexes) == 0:
            print('A peice did not match the hashlist!')
            return

        for index in indexes:
            with open(ifile.filename, 'r+b') as f:
                f.seek(ifile.psize * index)
                f.write(peice)
                f.close()

    def verify_file(s):
        f_hash = generate_hash(filepath=ifile.filename, person=os.path.basename(ifile.filename).encode('utf8'))
        if f_hash == ifile.hash:
            return True
        return False

#returns list of indexes of hash to peice match or empty if none
def get_index(peice, hashes, person):
    
    indexes = []
    p_hash = generate_hash(data=peice, person=person)
    index = 0
    for hashr in hashes:

        #debug print
        #print(peice, '|', p_hash)

        if hashr == p_hash:
            indexes.append(index)

        index += 1

    return indexes   

#returns hashlist of a file
def get_file_hashlist(filename, psize):

    person = os.path.basename(filename).encode('utf8')
    hashes = []

    with open(filename, 'rb') as f:
        peice = f.read(psize)
        #print(peice)
        while peice:
            p_hash = generate_hash(data=peice, person=person)
            hashes.append(p_hash)
            #print(p_hash)
            peice = f.read(psize)
            #print(peice)

        f.close()

    return hashes

#returns peices of file
def get_file_peices(filename, psize, shuffle=False):

    peices = []

    with open(filename, 'rb') as f:
        peice = f.read(psize)
        while peice:
            if peice not in peices:
                peices.append(peice)
            peice = f.read(psize)

        f.close()

    if shuffle:
        random.shuffle(peices)

    return peices

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

#generates a template ifile def from list of dirs
def generate_raw_ifile_def(files, output):

    yaml = YAML(typ='rt')
    node = {'files':[]}

    for file in files:
        fnode = {'file'}

        fnode['file']['name'] = file
        fnode['file']['hash'] = generate_hash(filepath=file, person=os.path.basename(file).encode('utf8'))
        fnode['file']['size'] = os.path.getsize(file)
        fnode['file']['size'] = 0
        fnode['file']['datastart'] = 0
        fnode['file']['dataend'] = 0

        node['files'].append(fnode)

    with open(output, 'wb') as f:
        yaml.dump(fnode, f)
        f.close()

#generates full ifile hash file from preexsiting raw def file
def generate_ifile_def(idef):

    yaml = YAML(typ='rt')
    with open(idef, 'r+b') as f:
        node = yaml.load(f)
        #f.close()

        for file in node['files']:
            name = file['file']['name']
            psize = file['file']['psize']
            hashes = get_file_hashlist(name, psize)

            f.seek(0, 2)
            f.write(b'\n')




