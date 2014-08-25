#!/usr/local/bin/python
# encoding: utf-8
'''
Created on Aug 22, 2014

@author: ergino
'''

import httplib2
import socket
import time               

MAX_NUMBER_OF_JOB_ON_SESSION = 10
PORT_OF_SERVER_TO_DISTRIBUTE = 1974
recursion_count=0

def distributeWatchId(watch,server,port=PORT_OF_SERVER_TO_DISTRIBUTE):
    result=False
    s = None
    for res in socket.getaddrinfo(server, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            print "Error: ",msg
            continue
        try:
            s.connect(sa)
        except socket.error, msg:
            s.close()
            s = None
            print "Error: ",msg
            continue
        break
    if s is None:
        print 'could not open socket'
        return result    
    start_of_comm = s.recv(1024)
    if start_of_comm.find("<STARTOFCOMMUNICATION/>") != -1:
        s.sendall("<WATCH_ID>" + watch + "</WATCH_ID>")
        job_exec_result=s.recv(1024)
        if job_exec_result.find("<JOB_SUCCESSFULL>" + watch + "</JOB_SUCCESSFULL>") != -1:
            result = True    
    end_of_comm=s.recv(1024)
    if end_of_comm.find("<ENDOFCOMMUNICATION/>") == -1:
        result=False
        
    s.close   
    return result                  


def consumeWatchIds(g_watch_list,last_index,server_list):
    if g_watch_list == None or len(g_watch_list) == 0 or len(g_watch_list) < last_index:
        return None
    while last_index + MAX_NUMBER_OF_JOB_ON_SESSION < len(g_watch_list):
        for server in server_list:
            ix=last_index
            if last_index + MAX_NUMBER_OF_JOB_ON_SESSION < len(g_watch_list):
                while ix - last_index < MAX_NUMBER_OF_JOB_ON_SESSION: 
                    distributeWatchId(g_watch_list[ix],server)
                    ix += 1
            last_index=ix
        time.sleep(2)
    return last_index


def collectWatchListFromSource(source,g_watch_list):
    _watch_list = None 
    #do something to get watch list
    if (source == None) or (source == "") :
        return None

    ix = source.find("watch?v=")
    while (ix != -1):
        _str = source[ix+8:ix+8+11]
        if g_watch_list != None:
            if g_watch_list.count(_str) == 0 :
                if _watch_list == None:
                    _watch_list = []
                if _watch_list.count(_str) == 0 :
                    _watch_list.append(_str)
        else:
            if _watch_list == None:
                _watch_list = []
            if _watch_list.count(_str) == 0 :
                _watch_list.append(_str)
        source = source[ix+8+11:]
        if source != None:
            ix = source.find("watch?v=")
        else:
            ix=-1
        
    if (_watch_list == None) or len(_watch_list) == 0 : 
        return None 
    else: 
        return _watch_list


def downloadSourceOfUrl(url):
    #do something to get http source of url
    if (url == None) or (url == "") :
        return None
    
    try:
        http = httplib2.Http(timeout=20)
        resp, content = http.request(url)
        if resp.status == 200:
            return content 
        else:
            return None
    except:
        return None


def collectWatchList(p_w_list,g_watch_list,rc,last_index,server_list):
    _w_list = None
    rc += 1
    
    if (g_watch_list !=  None) and (len(g_watch_list) - last_index > 100):
        last_index = consumeWatchIds(g_watch_list,last_index,server_list);

    print 'recursion count: ' , rc 
    print 'w list len:' , len(g_watch_list)
    print 'consumed watch id count: ' , last_index
    
    for _watch in p_w_list:
        _w_list = collectWatchListFromSource(downloadSourceOfUrl("http://www.youtube.com/watch?v=" + _watch),g_watch_list)
        
        if ((_w_list != None) and (len(_w_list) != 0)):
            g_watch_list.extend(_w_list)
            if len(g_watch_list) - last_index > 100:
                last_index = consumeWatchIds(g_watch_list,last_index,server_list);
            if rc > 70:
                continue
            collectWatchList(_w_list,g_watch_list,rc,last_index,server_list)
    
    rc -=1


def processUrl(first_url,g_watch_list,last_processed_index,server_list):
    # we load the first youtube file to extrach watch list
    _w_list = collectWatchListFromSource(downloadSourceOfUrl(first_url),g_watch_list)
    if (_w_list != None) :
        if g_watch_list == None :
            g_watch_list = [] ;
        g_watch_list.extend(_w_list)
        collectWatchList(_w_list,g_watch_list,recursion_count,last_processed_index,server_list)
    
    return 0

