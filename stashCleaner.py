#!/usr/bin/env python3
#
# Remove files and directories quickly from a path, and optionally log the deleted files.
#
#

import os,sys,optparse,time,shutil,gzip

def delete(x):
    os.unlink(x)

def log(x):
    logpath = path + "deleted.log"
    with open(logpath, "a") as log_file:
        log_file.write(x + ": " + str(stat) + "\n")
    
def main():
    parser = optparse.OptionParser('[-] Usage: dircleaner.py '+ '-p <PATH> -s <SECONDS> -a <ACTION> -h for help')
    parser.add_option('-p', dest='path', type='string', help='work path')
    parser.add_option('-s', dest='seconds', type='int', help='number of seconds in the past since now')
    parser.add_option('-a', dest='action', type='string', help='d = delete files, dl = delete files and log')
    (options, args) = parser.parse_args()

    if (options.path == None) | (options.seconds == None) | (options.action == None):
        sys.exit(parser.usage)

    global path
    if (options.path == "."):
        path = "./"
    else:
        path = options.path
    
    seconds = options.seconds
    action = options.action


    if (action != "d") & (action != "dl"):
        sys.exit("Valid actions are:\n\nd = delete files, dl = delete files and log\n\nInsert coin and try again! ")

    now = int(time.time())
    files = os.listdir(path)
    os.chdir(path)

    global stat

    for a in files:
        if os.path.isfile(a):
            stat = os.stat(a)
            ctime = int(stat.st_ctime)
            diff = now - ctime
            if diff > seconds:
                if action == "dl":
                    delete(a)
                    log(a)
                elif action == "d":
                    delete(a)

####################################################################

if __name__ == '__main__':
    main()
