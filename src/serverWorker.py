#!/usr/local/bin/python
# encoding: utf-8
'''
Created on Aug 22, 2014

@author: eozekes
'''

import socket               
import time
import subprocess
import thread

def executeJobWrapper(thread_name,watch_id):
    print thread_name + ' is executing !!!'
    pid = subprocess.Popen(["/usr/bin/chromimum-browser","http://www.youtube.com/watch?v=" + watch_id])
    time.sleep(180)
    pid.kill()
    print thread_name + ' is exiting !!!'


def executeJob(watch):
    if watch == None:
        return 0
    try:
        thread.start_new_thread(executeJobWrapper,("Thread-" + watch ,watch,))
        return 1
    except:
        print "Thread-" + watch + " not executed.!!!"
        return 0
    
#<WATCH_ID>ID</WATCH_ID>
def parseJob(job):
    if job == None:
        print "job is None!!!!"
        return None
    
    start_of = job.find("<WATCH_ID>") ;
    end_of = job.find("</WATCH_ID>")
    
    if start_of == -1 or end_of == -1:
        print "job is INVALID!!!!"
        return None
    
    return job[start_of + 10:end_of]

def processJob(job):
    return parseJob(job)
    
def sendStart(connection):
    connection.send("<STARTOFCOMMUNICATION/>")

def sendStop(connection):
    connection.send("<ENDOFCOMMUNICATION/>")

def sendMsg(connection,msg):
    connection.send(msg)
    
def receiveJobForWatchId(connection):
    return processJob(connection.recv(1024))

def startServer(port,daemon):
    if daemon :
        print "Server started as a daemon!!!"
    else:
        print "Server started as batch process!!!"
    print "Port is ",port


    s = None
    for res in socket.getaddrinfo('10.211.11.154', port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(5)
        except socket.error, msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print 'could not open socket'
        return 0

    while daemon:
        connect, addr = s.accept()     
        print 'Got connection from', addr
        sendStart(connect)
        _watch_id = receiveJobForWatchId(connect)
        if _watch_id != None:
            if executeJob(_watch_id) == 1:
                print "Job for %s is successfull!!!" %(_watch_id)
                sendMsg(connect,"<JOB_SUCCESSFULL>" + _watch_id + "</JOB_SUCCESSFULL>" )
            else:
                print "<JOB_FAILED>%s</JOB_FAILED>!!!" %(_watch_id)
                sendMsg(connect,"<JOB_FAILED>" + _watch_id + "</JOB_FAILED>" )
        else:
            print "<JOB_FAILED/>!!!"
            sendMsg(connect,"<JOB_FAILED/>")
        sendStop(connect)
        connect.close()                

    
    return 0
