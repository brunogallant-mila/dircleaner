#!/usr/bin/env python3
#
# Remove files and directories quickly from a path, and log the deleted files.
# TODO: catch exception for directories that are not empty, and ignore them.
#

import os,time

NOW = int(time.time())
seconds = 5
logpath = "/home/brunog-local/stash_cleanup.log"
path = "/home/brunog-local/tmp1/"

def delete(x):
    stat = os.stat(x)
    mtime = int(stat.st_mtime)
    atime = int(stat.st_atime)
    mdiff = NOW - mtime
    adiff = NOW - atime
    
    if os.path.isfile(x):
        if mdiff > seconds and adiff > seconds:
            os.unlink(x)
            # print("Dead file: " + x)

    elif os.path.isdir(x):
        if mdiff > seconds:
            os.rmdir(x)
            # print("Dead dir: " + x)

    with open(logpath, "a") as log_file:
        log_file.write(x + ": " + str(stat) + "\n")


def main():

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            # print("file: " + os.path.join(root, name))
            delete(os.path.join(root, name))
        for name in dirs:
            # print("dir: " + os.path.join(root, name))
            delete(os.path.join(root, name))


####################################################################



if __name__ == '__main__':
    main()
