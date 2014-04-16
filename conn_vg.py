# coding=utf-8
import sys
import subprocess
import time


class MyVPN():
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
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
		#subprocess.call(['ifconfig'])


	def change_route(self):
		subprocess.call(['ip', 'route', 'add', self.ip, 'via', '192.168.0.1', 'dev', 'eth0'])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '10.211.254.254', 'dev', self.vpn_adapter])

	
	def restore_default_route(self):
		subprocess.call(['ip', 'route', 'del', self.ip])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '192.168.0.1', 'dev', 'eth0'])


if __name__ == "__main__":
	print '\nBegin VPN configuration, please wait ...'
	print '\ncreating vpn instance ...'
	a = MyVPN(sys.argv[1], sys.argv[2])
	'''
	print '\nreconfig account settings and connect ...'
	a.connect_vpn()
	time.sleep(3)	
	a.status_get()
	print '\ndhclient refreshing ...'
	a.dhclient_refresh()
	print '\nchanging route ...'
	a.change_route()
	print '\nnow you can enjoy the vpn connection!'
	'''
	print '\nrestoring default route settings ...'
	a.restore_default_route()
	print '\ndefault route restored!'
