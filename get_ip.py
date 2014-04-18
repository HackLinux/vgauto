import threading
import urllib2
import re
import PingIt



mlock = threading.RLock()

class VgServer():
    def __init__(self):
        self.threads = []
        self.allList = []
    

    def get_ip_from_html(self):
        try:
            response = urllib2.urlopen('http://www.vpngate.net/en/')
        except Exception as err:
            print '\nopen url failed:%s\ntrying using proxy 127.0.0.1:8087 ...'%err
            proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            try:
                response = urllib2.urlopen('http://www.vpngate.net/en/')
            except Exception as err:
                print 'open url failed again!\nexiting ...'
                exit(0)
        
        html = response.read()
        p = re.compile('ip=\d+\.\d+\.\d+\.\d+&tcp=\d+')
        ip_tcp = p.findall(html)
        p_ip = re.compile('\d+\.\d+\.\d+\.\d+')
        p_port = re.compile('(?<=tcp\=)\d+')
        ip_list = []
        for i in ip_tcp:
            ip = p_ip.findall(i)[0]
            port = p_port.findall(i)[0]
            ip_list.append([ip, port])
        
        print 'get [ip, port] list successed, totally %s servers'%len(ip_list)
        return ip_list


    # get ping value
    def GetLegacy(self, ip_port):
        ip = ip_port[0]
        port = ip_port[1]
        p = PingIt.PingIt(ip)
        p.start()
        pingValue = p.getLegacy()
        
        if pingValue != -1:
            mlock.acquire()
            self.allList.append([pingValue, ip, port])
            mlock.release()


    # get all ping result into a list
    def GetAll(self):
        ip_list = self.get_ip_from_html()
        
        for ip_port in ip_list:
            t = threading.Thread(target=self.GetLegacy, args=(ip_port, ), name='thread-'+ip_port[0])
            t.start()
            self.threads.append(t)


    # return ip list sorted by ping value
    def get_result(self):
        self.GetAll()
        for t in self.threads:
            t.join()
        
        print 'sort list by ping value ... '
        self.allList = sorted(self.allList)
        for i in self.allList:
            ip = self.allList[0][1]
            port = self.allList[0][2]
            if port != '0':
                return ip, port
            else:
                continue
        print '\nNo usable port found, please retry!'
        return -1

    def close_db():
        self.conn.close()




if __name__ == "__main__":
    s = VgServer()
    print s.get_result()
   

    


