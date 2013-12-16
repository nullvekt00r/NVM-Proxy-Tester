###############################################
# Multithreaded Mass Proxy Tester
# Author: nullvekt00r
# Todo: Pass User-agent, and parse results for keyword
###############################################

import time
import argparse
import pycurl
import cStringIO
import threading
import Queue

print "=============================\nMultithreaded Mass Proxy Tester\nAuthor: nullvekt00r\n============================="

parser = argparse.ArgumentParser(description='Multithreaded Mass proxy tester.  Accepts filename containing list of proxies as first argument, and a test URL as the second argument.')
parser.add_argument('input_file', help='Text file with list of proxies to test. Format is one ip:port per line.')
parser.add_argument('test_url', help='URL to test proxy against')
parser.add_argument('output_file', help='Output file that the list of working proxies will be written to.')
args = parser.parse_args()

numThreads = 50
connectTimeout = 7
testTimeout = 5
queue = Queue.Queue()
proxyList = (line.rstrip('\n') for line in open(args.input_file))
goodProxies = []

class ThreadProxy(threading.Thread):
    'Threaded Proxy Tester Class'
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True:
            testProxy = self.queue.get()
            proxyType = ""
            buf = cStringIO.StringIO()
            #print "\nTesting proxy: %s"%(testProxy)
            #print "Testing as Socks5 proxy..."

            c1 = pycurl.Curl()
            c1.setopt(pycurl.URL, args.test_url)
            c1.setopt(pycurl.PROXY, testProxy)
            c1.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            c1.setopt(pycurl.CONNECTTIMEOUT, connectTimeout)
            c1.setopt(pycurl.TIMEOUT, testTimeout)
            c1.setopt(pycurl.NOSIGNAL, 1)
            c1.setopt(pycurl.WRITEFUNCTION, buf.write)
            try:
                c1.perform()
                #print "Success!"
                #print "Output: \n", buf.getvalue()
                proxyType = "socks5"
                #goodProxies.append(proxyType+' '+testProxy)
                goodProxies.append(testProxy)
            except pycurl.error, error:
                errno, errstr = error
                #print "Socks5 test failed\nError: ", errstr
            if proxyType != "socks5":
                #print "\nTesting as Socks4 proxy..."
                c2 = pycurl.Curl()
                c2.setopt(pycurl.URL, args.test_url)
                c2.setopt(pycurl.PROXY, testProxy)
                c2.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
                c2.setopt(pycurl.CONNECTTIMEOUT, connectTimeout)
                c2.setopt(pycurl.TIMEOUT, testTimeout)
                c2.setopt(pycurl.NOSIGNAL, 1)
                c2.setopt(pycurl.WRITEFUNCTION, buf.write)
                try:
                    c2.perform()
                    #print "Success!"
                    #print "Output: \n", buf.getvalue()
                    proxyType = "socks4"
                    #goodProxies.append(proxyType+' '+testProxy)
                    goodProxies.append(testProxy)
                except pycurl.error, error:
                    errno, errstr = error
                    #print "Socks4 test failed\n Error: ", errstr
                
            if proxyType != "socks4" and proxyType != "socks5":
                #print "\nTesting as HTTP proxy..."
                c3 = pycurl.Curl()
                c3.setopt(pycurl.URL, args.test_url)
                c3.setopt(pycurl.PROXY, testProxy)
                c3.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
                c3.setopt(pycurl.CONNECTTIMEOUT, connectTimeout)
                c3.setopt(pycurl.TIMEOUT, testTimeout)
                c3.setopt(pycurl.NOSIGNAL, 1)
                c3.setopt(pycurl.WRITEFUNCTION, buf.write)
                try:
                    c3.perform()
                    #print "Success!"
                    #print "Output: \n", buf.getvalue()
                    proxyType = "http"
                    #goodProxies.append(proxyType+' '+testProxy)
                    goodProxies.append(testProxy)
                except pycurl.error, error:
                    errno, errstr = error
                    #print "HTTP test failed\n Error: ", errstr

            #print "\nTest finished\n"
            #if len(proxyType) > 0:
                #ip,port = testProxy.split(':')
                #print "%s %s %s WORKING" % (proxyType, ip, port)
            #else:
                #print "%s FAILED" % (testProxy)

            buf.close()
            
            # Sets task done for queue
            self.queue.task_done()

start = time.time()
def main():
    # Spawn threads, and pass them the queue instance
    for i in range(numThreads):
        t = ThreadProxy(queue)
        t.setDaemon(True)
        t.start()

    # Load proxies into queue
    for p in proxyList:
        queue.put(p)

    # Wait for the everything in the queue to be processed
    queue.join()

print "Testing proxies from input file %s..." % (args.input_file)
main()
print "\nElapsed Time: %s\n" % (time.time() - start)
#print "Good Proxies: "
#for i in goodProxies:
#    print i
print "Writing working proxies to output file: %s" % args.output_file
f = open(args.output_file, 'w')
for i in goodProxies:
    f.write(i+'\n')
f.close()
print "Done\n"

