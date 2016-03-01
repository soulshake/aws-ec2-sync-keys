#!/usr/bin/env python
from subprocess import Popen, PIPE
import sys, os
from subprocess import call
import socket

def load_aws_keys():
    cmd = "aws ec2 describe-key-pairs"
    result = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    keys = {}
    for line in result.split('\n'):
        line = line.split()
        if line:
            keys[line[1]] = line[2]
    return keys

def get_key_paths():
    home = os.path.expanduser("~")
    ssh_path = os.path.join(home, ".ssh")
    ignore = ['known_hosts', 'authorized_keys', 'pub', 'asc', 'id_rsa']

    paths = []
    for f in os.listdir(ssh_path):
        if f.split('.')[-1] in ignore or f in ignore:
            continue
        paths.append(os.path.join(ssh_path, f))
    return paths

def load_our_keys(paths):
    print("Loading private keys: {}".format(paths))
    our_keys = {}
    for privkey_path in paths:
        our_keys.update(load_key(privkey_path))
    return our_keys

def load_fingerprint(path):
    cmd = "openssl rsa -in {} -pubout -outform DER | openssl md5 -c".format(path)
    result = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    result = result.split()
    if result[0] == '(stdin)=':
        fingerprint = result[1]
    else:
        raise Exception("Could not load fingerprint from path {}".format(path))
    return fingerprint

def load_public_key_material(path):
    cmd = "openssl rsa -in {} -pubout".format(path)
    result = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    result = result.split('\n')
    result = result[1:-2] # remove ---BEGIN--- and ---END--- lines
    result = "".join(result)
    return result

def load_key(path):
    fp = load_fingerprint(path)
    ret = {fp: {}}
    ret[fp]['privkey_path'] = path
    ret[fp]['public_key_material'] = load_public_key_material(path)
    return ret

def print_aws_keys(aws_keys):
    print("== AWS KEYS ==")
    for key in aws_keys:
        print("{} == {}".format(key, aws_keys[key]))

def print_our_keys(our_keys):
    print("== OUR KEYS ==")
    for key in our_keys:
        print("{} == {}".format(key, our_keys[key]))
    print("")

def check_our_keys(our_keys):
    print("Checking our {} keys are in AWS...".format(len(our_keys)))
    for fingerprint in our_keys:
        if fingerprint not in aws_keys:
            print("{} = NOK".format(fingerprint))
            import_key_by_path(our_keys[fingerprint]['privkey_path'])
        else:
            print("{} = OK ({})".format(fingerprint, aws_keys[fingerprint]))

def make_key_name(path):
    name = os.getenv('USER')
    name += "@" + socket.gethostname()
    name += ":" + os.path.realpath(path)
    return name

def import_key(key):
    fingerprint = key['fingerprint']
    pubkey = key['public_key_material']

def import_key_by_path(path):
    name = make_key_name(path)

    #fingerprint = load_fingerprint(path)
    pubkey = load_public_key_material(path)
    cmd = 'aws ec2 import-key-pair --key-name "{}" --public-key-material "{}"'.format(name, pubkey)
    print("!! Running command !!")
    print(cmd)
    result = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    print(result)
    return result


def gen_key(name):
    #TODO
    # openssl genrsa -out my-key.pem 2048
    # openssl rsa -in my-key.pem -pubout > my-key.pub
    cmd = "openssl genrsa -out {}.pem 2048".format(name)
    cmd = "openssl rsa -in {}.pem -pubout > {}.pub".format(name, name)

paths = sys.argv[1:] or get_key_paths()

our_keys = load_our_keys(paths)
print_our_keys(our_keys)

aws_keys = load_aws_keys()
print_aws_keys(aws_keys)

check_our_keys(our_keys)
