# DFSs
Distributed file system inspired by GFS.

## Table of contents
- [How system should work](#how-system-should-work)
 - [Client](#client)
 - [Master](#master)
 - [Chunk](#chunk)
- [Use cases](#use-cases)
 - [Client namespace manipulation](#client-namespace-manipulation)
 - [Client put file](#client-put-file)
 - [Client get file](#client-get-file)
 - [Client delete file](#client-delete-file)
 - [Client append to file](#client-append-to-file)
 - [New chunk server](#new-chunk-server)
 - [Lost chunk server](#lost-chunk-server)
 - [Master server restart](#master-server-restart)
 - [Chunk server restart](#chunk-server-restart)
 - [Periodical master server diagnostic](#periodical-master-server-diagnostic)
- [Demonstration](#demonstration)
- [Possible improvements](#possible-improvements)

## How system should work
There is a client on users PC.
Also there is a master server on remote server.
And there are a lot of file servers on different computers.

### Client
Has CLI to work with file namespaces and get, put, delete, (append?) files.
Has local file with user settings.

### Master
Has all metadata about **files** (namespace: chunks uuid) and **chunks** (chunk uuid: replica locations).
Conduct periodical diagnostic about chunk servers status.

### Chunk
Has local chunk metadata (chunk uuid: file name).
Report master after connection to network and periodical diagnostic.

## Use cases
Here is a brief overview of system behavior.

### Client namespace manipulation
Client use CLI to create, delete, print namespaces.

client-server communications:
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

### Master server restart

### Chunk server restart

### Periodical master server diagnostic


## Demonstration



## Possible improvements