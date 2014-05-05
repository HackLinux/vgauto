#!/usr/bin/python2.7
import csv
import re
import threading
import urllib2
import PingIt
from configs import proxy_url



# lock ip list for appending
mlock = threading.RLock()

# object contains server information
class VgServer():
    def __init__(self, csv_or_html):
        self.threads = []
        self.allList = []
        self.pu = proxy_url
        self.csv_or_html = csv_or_html
        
    
    def get_html_response(self, url):
        try:
            response = urllib2.urlopen(url)
        except Exception as err:
            print '\nopen url failed:%s\ntrying using proxy %s ...'%(err, 
                                                                     self.pu)
            proxy = urllib2.ProxyHandler(self.pu)
            opener = urllib2.build_opener(proxy)
            #urllib2.install_opener(opener)
            try:
                response = opener.open(url)
                #response = urllib2.urlopen('http://www.vpngate.net/en/')
            except Exception as err:
                print 'open url failed again!\nexiting ...'
                exit(0)
        
        html = response.read()
        return html
        
    
    def get_ip_from_csv(self):
        try:
            csv_data = open('tmp_csv.csv', 'rb').read()
        except Exception as err:
            print 'tmp_csv.csv not found! trying get it from vpngate.net ..'
            url = 'http://www.vpngate.net/api/iphone/'
            csv_data = self.get_html_response(url)
            with open('tmp_csv.csv', 'wb') as fw:
                fw.write(csv_data)
            
        try:    
            tmp_csv_data = csv_data.split('\n')
        except Exception as err:
            print 'fetch tmp_csv.csv file error!'
            exit(0)
        
        fieldnames = tmp_csv_data[1].split(',')
        tmp_csv_data = tmp_csv_data[2:]
        csv_reader = csv.DictReader(tmp_csv_data, 
                                    fieldnames=fieldnames,
                                    delimiter=',')
        
        ip_list = []
        count = 0
        for row in csv_reader:
            ip = row['IP']
            num_sessions = row['NumVpnSessions']
            lspeed = row['Speed']
            if lspeed is not None:
                lspeed = int(lspeed)/1024/1024
            pint_to_google = row['Ping']
            openvpn_data = row['OpenVPN_ConfigData_Base64\r']
            ip_list.append([ip, num_sessions, str(lspeed)+"Mbps", pint_to_google, openvpn_data])
        
        print 'get openvpn server list succeed, totally %s servers'%len(ip_list)
        # remove the last None item
        ip_list = ip_list[:-1]
        return ip_list
        
    
    # get the origin server list
    def get_ip_from_html(self):
        url = 'http://www.vpngate.net/en/'
        html = self.get_html_response(url)
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
        if self.csv_or_html == 'openvpn':
            ip = ip_port[0]
            ping = ip_port[1]
            lspeed = ip_port[2]
            ping_google = ip_port[3]
            openvpn_data = ip_port[4]
        elif self.csv_or_html == 'vpngate':
            ip = ip_port[0]
            port = ip_port[1]
            lspeed = ip_port[2]
        else:
            print 'VPN program type error!'
            exit(0)
        
        p = PingIt.PingIt(ip)
        p.start()
        pingValue = p.getLegacy()
        
        if pingValue != -1:
            mlock.acquire()
            if self.csv_or_html == 'openvpn':
                self.allList.append([pingValue, ip, ping_google, lspeed, openvpn_data])
            elif self.csv_or_html == 'vpngate':
                self.allList.append([pingValue, ip, port, lspeed])
            mlock.release()


    # get all ping result into a list
    def GetAll(self):
        if self.csv_or_html == 'openvpn':
            ip_list = self.get_ip_from_csv()
        elif self.csv_or_html == 'vpngate':
            ip_list = self.get_ip_from_html()
        else:
            print 'VPN program type error!'
            exit(0)
            
        for ip_port in ip_list:
            t = threading.Thread(target=self.GetLegacy, args=(ip_port, ), 
                                 name='thread-'+ip_port[0])
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


if __name__ == "__main__":
    a = VgServer('openvpn')
    a.get_ip_from_csv()
