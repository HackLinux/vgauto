# coding=utf-8
import sys
import subprocess
import time
import get_ip



class MyVPN():
	def __init__(self, ip, port, enable):
		self.ip = ip
		self.port = port
		self.enable = int(enable)
		self.conf_file_name = 'vgp.vpn'
		self.conf_name = 'vgp1'
		self.vpn_adapter = 'vpn_vg'
		self.conf_string = '''﻿# VPN Client VPN Connection Setting File
# 
# This file is exported using the VPN Client Manager.
# The contents of this file can be edited using a text editor.
# 
# When this file is imported to the Client Connection Manager
#  it can be used immediately.

declare root
{
	bool CheckServerCert false
	uint64 CreateDateTime 0
	uint64 LastConnectDateTime 0
	bool StartupAccount false
	uint64 UpdateDateTime 0

	declare ClientAuth
	{
		uint AuthType 1
		byte HashedPassword H8N7rT8BH44q0nFXC9NlFxetGzQ=
		string Username vpn
	}
	declare ClientOption
	{
		string AccountName vgp1
		uint AdditionalConnectionInterval 1
		uint ConnectionDisconnectSpan 0
		string DeviceName vg
		bool DisableQoS false
		bool HalfConnection false
		bool HideNicInfoWindow false
		bool HideStatusWindow false
		string Hostname %s
		string HubName VPNGATE
		uint MaxConnection 1
		bool NoRoutingTracking false
		bool NoTls1 false
		bool NoUdpAcceleration false
		uint NumRetry 4294967295
		uint Port %s
		uint PortUDP 0
		string ProxyName $
		byte ProxyPassword $
		uint ProxyPort 0
		uint ProxyType 0
		string ProxyUsername $
		bool RequireBridgeRoutingMode false
		bool RequireMonitorMode false
		uint RetryInterval 15
		bool UseCompress false
		bool UseEncrypt true
	}
}
''' % (ip, port)
		self.create_tmp_conf_file()


	def create_tmp_conf_file(self):
		tmp_f = open(self.conf_file_name, 'w')
		tmp_f.write(self.conf_string)
		tmp_f.close()


	# clear recent account settings, import a new one, and connect it
	def connect_vpn(self):
		# create Popen instance
		p = subprocess.Popen(['vpncmd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

		# input our commands
		p.stdin.write('2\n')
		p.stdin.write('\n')
		p.stdin.write('accountdisconnect %s\n'%self.conf_name)
		p.stdin.write('accountdel %s\n'%self.conf_name)
		p.stdin.write('accountimport\n')
		p.stdin.write(self.conf_file_name)
		p.stdin.write('\n')
		p.stdin.write('accountconnect %s\n'%self.conf_name)
		p.stdin.write('keepenable\n')
		p.stdin.write('accountstatusget %s\n'%self.conf_name)

		# run commands and exit
		a = p.communicate()

		# display commands response
		for i in a:
			print i


	def status_get(self):
		# create Popen instance
		p = subprocess.Popen(['vpncmd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

		# input our commands
		p.stdin.write('2\n')
		p.stdin.write('\n')
		p.stdin.write('accountstatusget %s\n'%self.conf_name)

		# run commands and exit
		a = p.communicate()

		# display commands response
		for i in a:
			print i
	
	
	def dhclient_refresh(self):
		subprocess.call(['dhclient', '-r', self.vpn_adapter])
		subprocess.call(['dhclient', self.vpn_adapter])
		subprocess.call(['ifconfig'])


	def change_route(self):
		subprocess.call(['ip', 'route', 'add', self.ip, 'via', '192.168.0.1', 'dev', 'eth0'])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '10.211.254.254', 'dev', self.vpn_adapter])

	
	def restore_default_route(self):
		subprocess.call(['ip', 'route', 'del', self.ip])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '192.168.0.1', 'dev', 'eth0'])


	def vg_switch(self):
		if self.enable == 1:
			print '\nreconfig account settings and connect ...'
			self.connect_vpn()
			time.sleep(3)	
			self.status_get()
			print '\ndhclient refreshing ...'
			self.dhclient_refresh()
			print '\nchanging route ...'
			self.change_route()
			print '\nnow you can enjoy the vpn connection!'
		elif self.enable == 0:
			print '\nrestoring default route settings ...'
			self.restore_default_route()
			print '\ndefault route settings set successfully!'
		else:
			print '\nUnknown error!!!'
			exit(0)



if __name__ == "__main__":
    op_flag = raw_input('You have some choices:\n\t1. open vpn connection\n\t2. close vpn connection\n\t3. exit\nSo, which one do you like:')
    
    # init default param value
    ip = '124.56.10.199'
    port = '995'
    
    
    if op_flag == '1':
        print 'Retrieving best server for you, please wait ...'
        
        serv = get_ip.VgServer()
        best_server = serv.get_result()
        
        if len(best_server) < 5:
            print '\nno suitable server found, please retry!'
            exit(0)
        
        print 'Here is the best 5 servers for you:'
        print '\n\tNo.\tping\tIP\t\tPort\tLineSpeed'
        for i in range(len(best_server)):
            print '\t%s.'%(i+1),
            print '\t%s\t%s\t%s\t%s'%(best_server[i][0], best_server[i][1], \
                    best_server[i][2],best_server[i][3])
        
        try:
            choice_flag = int(raw_input('Which one do you like to connect with:'))
        except:
            print '\nPlease check your input!'
            
        if choice_flag in range(1, 6):
            ip = best_server[choice_flag-1][1]
            port = best_server[choice_flag-1][2]
        else:
            print '\nPlease enter from "1" to "5"!'
        
        
        # save selected server info into a file, if we want to disconnect we read from it
        with open('tmp_ip.txt', 'wb') as fw:
            fw.write('%s:%s'%(ip, port))

        confirm_flag = raw_input('You have choose:%s:%s, continue to connect?\n1. yes\n2. no\nPlease make your choice:'%(ip, port))
        
        if confirm_flag == '1':
            print '\nBegin VPN configuration, please wait ...'
            print '\ncreating vpn instance ...'
            #a = MyVPN(sys.argv[1], sys.argv[2], sys.argv[3])
            a = MyVPN(ip, port, 1)
            a.vg_switch()
        elif confirm_flag == '2':
            print '\nexiting ...'
            exit(0)
        else:
            print '\nInvalid input, please check!'
            exit(0)
            
    elif op_flag == '2':
        with open('tmp_ip.txt', 'rb') as fr:
            recent_server = fr.readline().split(':')
            print recent_server
            ip, port = recent_server
        a = MyVPN(ip, port, 0)
        a.vg_switch()
        
    elif op_flag == '3':
        exit(0)
        
    else:
        print '\nInvalid input, please check!'
        exit(0)
