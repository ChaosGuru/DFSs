# DFSs
Distributed file system inspired by GFS.

## Table of contents
- [How system should work](#how-system-should-work)
    - [Client](#client)
    - [Sensei](#sensei)
    - [Chunk](#chunk)
- [Use cases](#use-cases)
    - [Client namespace manipulation](#client-namespace-manipulation)
    - [Client put file](#client-put-file)
    - [Client get file](#client-get-file)
    - [Client delete file](#client-delete-file)
    - [Client append to file](#client-append-to-file)
    - [New chunk server](#new-chunk-server)
    - [Lost chunk server](#lost-chunk-server)
    - [Sensei server restart](#sensei-server-restart)
    - [Chunk server restart](#chunk-server-restart)
    - [Periodical sensei server diagnostic](#periodical-sensei-server-diagnostic)
- [Installation](#installation)
- [Demonstration](#demonstration)
- [Possible improvements](#possible-improvements)


## How system should work
There is a client on users PC.
Also there is a sensei server on remote server.
And there are a lot of file servers on different computers.

### Client
Has CLI to work with file namespaces and get, put, delete, (append?) files.
Has local file with user settings.

### Sensei
Has all metadata about **files** (namespace: chunks uuid) and **chunks** (chunk uuid: replica locations).
Conducts periodical diagnostic about chunk servers status.

### Chunk
Has local chunk metadata (chunk uuid: file name).
Report sensei after connection to network and periodical diagnostic.

## Use cases
Here is a brief overview of system behavior.

### Client namespace manipulation
Client use CLI to create, delete, print namespaces.
Client related data is saved in metadata.json file.

client-sensei server communications:
- add namespace
- delete namespace
- get namespaces

client cli:
- print current directory
- change current directory
- print namespaces
- print tree of namespaces
- add namespace
- remove namespace

### Client put file

### Client get file

### Client delete file

### Client append to file

### New chunk server

### Lost chunk server

### Sensei server restart

### Chunk server restart

### Periodical sensei server diagnostic


## Installation
For running this programm you will need:
- python3.7
- pip
- git

1. Clone the repository
```bash
git clone https://github.com/ChaosGuru/DFSs.git
```
2. Install necessary packages
```bash
pip install rpyc==5.0.1 click==7.1.2
```

**Ready**


## Demonstration

To use the system you need:
1. Start sensei server:
```bash
python server/sensei_dono.py 
```
2. Start chunk servers (write about it later)
3. Enter client directory
```bash
cd client
```

### Example with client cli
$ python client_kun.py pwd
/
$ python client_kun.py mkdir example
/example/
$ python client_kun.py ls
example
$ python client_kun.py tree
/example/
$ python client_kun.py cd example2
Error! Path do not exists!
/
$ python client_kun.py cd example
/example/
$ python client_kun.py pwd
/example/
$ python client_kun.py ls

$ python client_kun.py tree
/example/
$ python client_kun.py cd /
/
$ python client_kun.py pwd
/
$ python client_kun.py mkdir example2
/example2/
$ python client_kun.py tree
/example/
/example2/
$ python client_kun.py cd example2
/example2/
$ python client_kun.py mkdir new
/example2/new/
$ python client_kun.py mkdir new2
/example2/new2/
$ python client_kun.py ls
 new new2
$ python client_kun.py tree
/example2/
/example2/new/
/example2/new2/
$ python client_kun.py cd ..
/
$ python client_kun.py pwd
/
$ python client_kun.py tree
/example/
/example2/
/example2/new/
/example2/new2/
$ python client_kun.py ls
example example2
$ python client_kun.py ls example2
 new2 new
$ python client_kun.py rm example2
Removed 3 elements in namespace /example2/
$ python client_kun.py tree
/example/
$ python client_kun.py ls
example


## Possible improvements