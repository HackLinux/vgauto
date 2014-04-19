#!/usr/bin/python2.7
import threading
import urllib2
import re
import PingIt



# lock ip list for appending
mlock = threading.RLock()

# object contains server information
class VgServer():
    def __init__(self):
        self.threads = []
        self.allList = []
    
    
    # get the origin server list
    def get_ip_from_html(self):
        try:
            response = urllib2.urlopen('http://www.vpngate.net/en/')
        except Exception as err:
            print '\nopen url failed:%s\ntrying using proxy 127.0.0.1:8087 ...'%err
            proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
            opener = urllib2.build_opener(proxy)
            #urllib2.install_opener(opener)
            try:
                response = opener.open('http://www.vpngate.net/en/')
                #response = urllib2.urlopen('http://www.vpngate.net/en/')
            except Exception as err:
                print 'open url failed again!\nexiting ...'
                exit(0)
        
        html = response.read()
        
        # match strings like "ip=192.168.0.1&tcp=443"
        p_ip_tcp = re.compile('ip=\d+\.\d+\.\d+\.\d+&tcp=\d+')
        # match strings like "99 Mbps"
        p_linespeed = re.compile('\d+ Mbps')
        ip_tcp = p_ip_tcp.findall(html)
        linespeed = p_linespeed.findall(html)
        
        # match ip, though this may match strings like "111111111.111.11111.1":)
        p_ip = re.compile('\d+\.\d+\.\d+\.\d+')
        # match port
        p_port = re.compile('(?<=tcp\=)\d+')
        
        ip_list = []
        count = 0
        
        for i in ip_tcp:
            ip = p_ip.findall(i)[0]
            port = p_port.findall(i)[0]
            lspeed = linespeed[count]
            ip_list.append([ip, port, lspeed])
            count += 1

        print 'get [ip, port] list succeed, totally %s servers'%len(ip_list)
        return ip_list


    # get ping value
    def GetLegacy(self, ip_port):
        ip = ip_port[0]
        port = ip_port[1]
        lspeed = ip_port[2]
        p = PingIt.PingIt(ip)
        p.start()
        pingValue = p.getLegacy()
        
        if pingValue != -1:
            mlock.acquire()
            self.allList.append([pingValue, ip, port, lspeed])
            mlock.release()


    # get all ping result into a list
    def GetAll(self):
        ip_list = self.get_ip_from_html()
        
        for ip_port in ip_list:
            t = threading.Thread(target=self.GetLegacy, args=(ip_port, ), name='thread-'+ip_port[0])
            t.start()
            self.threads.append(t)


    # return ip list sorted by ping value, 
    # like this: [[10, '61.153.236.234', '0', '00 Mbps'], [...], ...]
    def get_result(self):
        self.GetAll()
        for t in self.threads:
            t.join()
        
        print 'sort list by ping value ... '
        self.allList = sorted(self.allList)
        
        # return best 10 in the list
        return self.allList[0:10]

