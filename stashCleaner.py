#!/usr/bin/env python3
#
# Remove files and directories quickly from a path, and log the deleted files.
# TODO: 
# - DONE - catch exception for directories that are not empty, and ignore them.
# - DONE - Add end report, with number of files and directories deleted
# - DONE - have this report be gzipped automatically
# - DONE - Catch Control-C and exit gracefully, with a report of what was deleted so far
# - DONE - check if it is already running.
# - VERSION 2 - send report to slack
#

from subprocess import check_call
import os,time,signal
from os import getpid
from os.path import exists


now = int(time.time())
seconds = 60 * 60 * 24 * 90
# seconds = 5
basedir = "/home/brunog-local/stashCleaner/"
deletelog = basedir + "stashCleaner_delete_" + str(now) + ".log"
reportlog = basedir + "stashCleaner_report.log"
path = "/home/brunog-local/tmp/"
delFiles = 0
delDirs = 0
totFiles = 0
totDirs = 0

LOCKFILE = basedir + "stashCleaner.lock"

def already_running():
    my_pid = getpid()
    if exists(LOCKFILE):
        print("Another instance of this script is already running. Exiting.")
        exit(1)

    with open(LOCKFILE, 'w') as f:
        f.write(str(my_pid))
    return False

def delete(x):
    global delFiles, delDirs
    stat = os.stat(x)
    mtime = int(stat.st_mtime)
    atime = int(stat.st_atime)
    mdiff = now - mtime
    adiff = now - atime
    
    if os.path.isfile(x):
        print("File: " + x + " | mtime: " + str(mdiff) + " | atime: " + str(adiff))
        # if mdiff > seconds and adiff > seconds:
        if mdiff > seconds:
            os.unlink(x)
            delFiles += 1
            with open(deletelog, "a") as log_file:
                log_file.write("File: " + x + ": " + str(stat) + "\n")

    if os.path.isdir(x):
        print("Dir: " + x + " | mtime: " + str(mdiff) + " | atime: " + str(adiff))
        if mdiff > seconds:
            os.rmdir(x)
            delDirs += 1
            with open(deletelog, "a") as log_file:
                log_file.write("Dir: " + x + ": " + str(stat) + "\n")

def report():
    end = int(time.time())
    runtime = end - now
    with open(reportlog, "a") as log_file:
        log_file.write("Runtime: " + str(runtime) + " seconds | ")
        log_file.write("Files deleted: " + str(delFiles) + " | ")
        log_file.write("Dirs deleted: " + str(delDirs) + " | ")
        log_file.write("Total files: " + str(totFiles) + " | ")
        log_file.write("Total dirs: " + str(totDirs) + "\n")

def main():
    global totFiles, totDirs
    with open(reportlog, "a") as log_file:
        log_file.write(time.ctime() + " | ")

    already_running() # Check if another instance is running, and exit if so.
    
    signal.signal(signal.SIGTERM, report) # Trap SIGTERM and call report() before exiting

    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                # print(path, name)
                totFiles += 1
                # print("file: " + os.path.join(root, name))
                delete(os.path.join(root, name))
            for name in dirs:
                # print(path, name)
                totDirs += 1
                # print("dir: " + os.path.join(root, name))
                delete(os.path.join(root, name))
    except OSError as e:
        # print("Dir Error: " + str(e))
        pass
    
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

