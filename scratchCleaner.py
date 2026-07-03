#!/usr/bin/env python3
#
# Remove files and directories quickly from a path, and log the deleted files.
# TODO: 
# - VERSION 2 - send report to slack

from subprocess import check_call
import os,time,signal,optparse,sys,tarfile,shutil
from os import getpid
from os.path import exists

parser = optparse.OptionParser('[-] Usage: scratchCleaner.py '+ '-p <PATH> -s <SECONDS> -h for help')
parser.add_option('-p', dest='path', type='string', help='work path')
parser.add_option('-s', dest='seconds', type='int', help='number of seconds in the past since now. Example: 30/60/90 days, 2592000, 5184000, 7776000 seconds')
(options, args) = parser.parse_args()

if (options.path == None) | (options.seconds == None):
    sys.exit(parser.usage)

seconds = options.seconds
path = options.path

username = os.path.basename(path.rstrip('/'))
print("username is " + username)

now = int(time.time())
starttime = time.ctime()
basedir = "/home/brunog-local/scratchCleaner/"
# basedir = "/network/scratch/.idt/scratchCleaner/"
deletelog = basedir + "scratchCleaner_delete_" + username + "_" + str(now) + ".log"
reportlog = basedir + "scratchCleaner_report.log"
delFiles = 0
totFiles = 0
totDirs = 0
LOCKFILE = basedir + "scratchCleaner_" + str(now) + ".lock"

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

def compressdir(x):
    print("Compressing empty directory: " + x)

    with tarfile.open(x + "ARCHIVED_DIRTREE_" + username + "_" + str(now) + ".tgz", "w:gz") as tar:
        tar.add(x, arcname=os.path.basename(x))
    
    for name in os.listdir(x):
        file_path = os.path.join(x, name)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def report():
    end = int(time.time())
    runtime = end - now
    with open(reportlog, "a") as log_file:
        log_file.write(username + " | ")
        log_file.write("Start: " + starttime + " | ")
        log_file.write("End: " + time.ctime() + " | ")
        log_file.write("Runtime: " + str(runtime) + " seconds | ")
        log_file.write("Total files: " + str(totFiles) + " | ")
        log_file.write("Files deleted: " + str(delFiles) + " | ")
        log_file.write("Total dirs: " + str(totDirs) + " | ")
        log_file.write("Inodes: " + str(totDirs+totFiles) + " | ")
        log_file.write("Working dir: " + path + " | ")
        log_file.write("Run number: " + str(now) + "\n")

def main():
    global totFiles, totDirs

    already_running() # Check if another instance is running, and exit if so.
    
    signal.signal(signal.SIGTERM, report) # Trap SIGTERM and call report() before exiting

    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if "ARCHIVED" in name:   # see compressdir() function.
                   continue
                if os.path.islink(os.path.join(root,name)):
                   continue
                totFiles += 1
                delete(os.path.join(root, name))
            for name in dirs:
                totDirs += 1
            
        if totFiles == 0 and totDirs > 0:
            compressdir(path)
                
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

