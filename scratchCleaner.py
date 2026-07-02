#!/usr/bin/env python3
#
# Remove files and directories quickly from a path, and log the deleted files.
# TODO: 
# - make it work in parallel
# - make it tar/gz a tree of directories without any files in it.
# - VERSION 2 - send report to slack
#

from subprocess import check_call
import os,time,signal,optparse,sys
from os import getpid
from os.path import exists


now = int(time.time())
# seconds = 60 * 60 * 24 * 90
# seconds = 5
basedir = "/home/brunog-local/scratchCleaner/"
deletelog = basedir + "scratchCleaner_delete_" + str(now) + ".log"
reportlog = basedir + "scratchCleaner_report_" + str(now) + ".log"
# path = "/home/brunog-local/tmp/"
delFiles = 0
totFiles = 0
totDirs = 0

LOCKFILE = basedir + "scratchCleaner.lock"

def already_running():
    my_pid = getpid()
    if exists(LOCKFILE):
        print("Another instance of this script is already running. Exiting.")
        exit(1)

    with open(LOCKFILE, 'w') as f:
        f.write("PID: " + str(my_pid) + " | Start: " + time.ctime() + "\n")
    return False

def delete(x):
    global delFiles
    stat = os.stat(x)
    mtime = int(stat.st_mtime)
    atime = int(stat.st_atime)
    mdiff = now - mtime
    adiff = now - atime
    
    if os.path.isfile(x):
        # print("File: " + x + " | mtime: " + str(mdiff) + " | atime: " + str(adiff))
        # if mdiff > seconds and adiff > seconds:
        if mdiff > seconds:
            os.unlink(x)
            delFiles += 1
            with open(deletelog, "a") as log_file:
                log_file.write("File: " + x + ": " + str(stat) + "\n")

def report():
    end = int(time.time())
    runtime = end - now
    with open(reportlog, "a") as log_file:
        log_file.write("End: " + time.ctime() + " | ")
        log_file.write("Runtime: " + str(runtime) + " seconds | ")
        log_file.write("Total files: " + str(totFiles) + " | ")
        log_file.write("Files deleted: " + str(delFiles) + " | ")
        log_file.write("Total dirs: " + str(totDirs) + " | ")
        log_file.write("Working dir: " + path + "\n")

def main():
    parser = optparse.OptionParser('[-] Usage: scratchCleaner.py '+ '-p <PATH> -s <SECONDS> -h for help')
    parser.add_option('-p', dest='path', type='string', help='work path')
    parser.add_option('-s', dest='seconds', type='int', help='number of seconds in the past since now')
    (options, args) = parser.parse_args()

    if (options.path == None) | (options.seconds == None):
        sys.exit(parser.usage)

    seconds = options.seconds
    path = options.path
    global totFiles, totDirs
    with open(reportlog, "a") as log_file:
        log_file.write(str(now) + " | ")
        log_file.write("Start: " + time.ctime() + " | ")

    already_running() # Check if another instance is running, and exit if so.
    
    signal.signal(signal.SIGTERM, report) # Trap SIGTERM and call report() before exiting

    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if os.path.islink(os.path.join(root,name)):
                   continue
                totFiles += 1
                delete(os.path.join(root, name))
            for name in dirs:
                totDirs += 1
    except OSError as e:
        print("Dir Error: " + str(e))
    
    except Exception as e:
        print("Error: " + str(e))
    
    finally:
        report()
        if exists(deletelog):
            check_call(['gzip', deletelog])
        os.remove(LOCKFILE)
        exit(0)



####################################################################



if __name__ == '__main__':
    main()

