###############################################################################
# Yagudaev.com                                                                #
# Copyright (C) 2011                                                          #
#                                                                             #
# Authors:                                                                    #
#    Michael Yagudaev michael@yagudaev.com                                    #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

'''
Created on 2011-04-19

Description: This script screen scrapes a page provided to it as an argument and then downloads
all the audio files found on the page.

Use: > downloader -u http://www.example.com/music
'''
import getopt
import sys
import urllib
import re
import threading
import datetime

downloadListLock = threading.Lock()

class WorkerThread (threading.Thread):
    def __init__(self, downloadList):
        self._downloadList = downloadList
        threading.Thread.__init__ ( self )
    
    def run(self):
        # download the files
        i = 0
        print "started thread #%s" % self.getName()
        
        for download in self._downloadList:
            i += 1
            downloadListLock.acquire(True)
            
            if download['inProgress'] == False:
                print "downloading file %s of %s (%s, thread: %s)" % (i, len(self._downloadList), download['filename'], self.getName())
                download['inProgress'] = True
                downloadListLock.release()
                
                downloadConnection = urllib.urlopen(download['url'])
                newFile = open(download['filename'], "wb")
                newFile.write(downloadConnection.read())
            
                print "finished writing %s (thread: %s)" % (download['filename'], self.getName())
            else:
                downloadListLock.release()

def main():
    #Reading in options from the command line
    optlist, args = getopt.getopt(sys.argv[1:], 'u:', ['url='])
    
    timeAtStart = datetime.datetime.now()
    
    if(not optlist):
        print """Wrong format!
            Options are:
            -u (--url): the URL where to download the content from
            """
        exit()
    else:
        #Parsing options specified in command line
        for opt, val in optlist:
            if opt == "-u" or opt == "--url":
                url = val
                if val.endswith('/'):
                    url = val[:-1]
                    
                print "`%s`" % url
    
    numThreads = 5
    
    # start reading the URL
    connection = urllib.urlopen(url)
    html = connection.read()
    
    patternLinks = re.compile(r'<a\s.*?href\s*?=\s*?"(.*?)"', re.DOTALL)
    iterator = patternLinks.finditer(html);

    downloadList = []
    
    # process individual items
    for match in iterator:
    #    print match.groups()
        fileUrl = match.group(1)
            
        if fileUrl.endswith(".mp3") or fileUrl.endswith(".wav") or fileUrl.endswith(".wma"):
            # absolute URL
            if fileUrl.startswith("http://"):
                filename = fileUrl[7:] # TODO: clean this up more!
                downloadUrl = fileUrl
            else: # relative url
                filename = fileUrl
                downloadUrl = url + '/' + fileUrl
            
            downloadList.append({'filename' : filename, 'url' : downloadUrl, 'inProgress': False})
    
    threads = []
    
    # create threads
    for i in range(0, numThreads):
        threads.append(WorkerThread(downloadList))
        threads[i].setName(i)
        threads[i].start()
    
    # wait for all threads to finish
    for t in threads:
        t.join()
        
    # print summary
    totalTime = datetime.datetime.now() - timeAtStart
    print "-" * 50
    print "Statistics"
    print "-" * 50
    print "Total Download Time: %s" % totalTime
    print "Average per File Time: %s" % (totalTime / len(downloadList))
                  
if __name__ == "__main__":
    main()
