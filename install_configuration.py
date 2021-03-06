#!/usr/bin/env python3
import os
import sys
import configparser
import shutil
from os import path as p

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def linux_stuff_template(stuff):
    return '''
#!/bin/bash
#
## This file define the STUFF environment variable
## It's automatically generated by install_configuration.py

export STUFF={0}
'''.format(stuff)

def remove_path(path):
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

def str_filetype(path):
    if os.path.lexists(path):
        if os.path.islink(path):
            typef = "symlink"
            if not os.path.exists(path):
                typef = "broken " + typef
        elif os.path.isdir(path):
            typef = "directory"
        elif os.path.isfile(path):
            typef = "file"
        else:
            typef = "unknown"
    else:
        typef = "not existent"
    return typef

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
                It must be "yes" (the default), "no" or None (meaning
                an answer is required of the user).

        The "answer" return value is one of "yes" or "no".
        """

    valid = {"yes":True, "y":True, "ye":True, "no":False, "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                            "(or 'y' or 'n').\n")

def install(src, dst):
    print("\t[>]", src, "->", dst)
    doit = False
    if os.path.exists(src):

        if os.path.lexists(dst):
            if not os.path.islink(dst) or os.readlink(dst) != src:
                typef = str_filetype(dst)
                if query_yes_no(WARNING+"\t[^] " + dst + " already exists (it's a "+typef+"), override?" + ENDC):
                    os.remove(dst)
                    doit = True
        else:
            doit = True

        if doit:
            try:
                dstdir = os.path.dirname(dst)
                if not os.path.isdir(dstdir):
                    os.makedirs(dstdir)
                os.symlink(src, dst)
                print(OKGREEN, "\t[+] Installed", ENDC)
            except e:
                print(FAIL, "\t[-] ERROR:", e, ENDC)
        else:
            print(FAIL, "\t[-] Skipped", ENDC)
    else:
        print(FAIL, "\t[#] ERROR:", src, "doesn't exists!", ENDC)
    print("")


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("./install.cfg")

    HOME = os.environ['HOME'];

    try:
        STUFF = os.environ['STUFF'];
    except:
        STUFF = os.path.abspath(os.path.dirname(sys.argv[0]))

    files = {}
    for s in config.sections():
        src = config.get(s, 'src')
        dst = config.get(s, 'dst')
        files[s] = (p.join(STUFF, src), p.join(HOME, dst))

    print(HEADER + " =========================================")
    print(         "  LINUX STUFF INSTALL CONFIGURATION TOOL!")
    print(         " =========================================\n\n", ENDC)

    # Installing the linux_stuff file
    if os.path.lexists(HOME + '/.linux_stuff'):
        os.remove(HOME + '/.linux_stuff')
    with open(HOME + '/.linux_stuff', 'w') as f:
        f.write(linux_stuff_template(STUFF))

    for k, (src,dst) in files.items():
        print(OKBLUE, " [*] Installing", k, "configuration" , ENDC)
        install(src, dst)
