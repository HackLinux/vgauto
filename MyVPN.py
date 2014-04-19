# coding=utf-8
#!/usr/bin/python2.7
import subprocess
import time



# vpncmd and route table settings
class MyVPN():
	def __init__(self, ip, port, enable):
		self.ip = ip
		self.port = port
		self.enable = int(enable)
		self.conf_file_name = 'vgp.vpn'
		self.conf_name = 'vgp1'
		self.vpn_adapter = 'vpn_vg'
		
		# vpncmd import file template
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

    
    # create a tmp *.vpn file, import it from vpncmd to create account
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

    
    # show accountstatusget information
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
	
	
	# refresh vpncmd adapter ip, 
	# if connected successfully it will get from the vpn server
	def dhclient_refresh(self):
		subprocess.call(['dhclient', '-r', self.vpn_adapter])
		subprocess.call(['dhclient', self.vpn_adapter])
		subprocess.call(['ifconfig'])

    
    # change route table settings
	def change_route(self):
		subprocess.call(['ip', 'route', 'add', self.ip, 'via', '192.168.0.1', 'dev', 'eth0'])
		# here "10.211.0.0/16" and "10.211.1.54" are static, we can use ifconfig to
		# make it work more properly. Normally after we have refreshed the dhcp
		# we will get a new ip address and this will also add automatically in route
		# table, seems we do not need to worry about this:)
		# subprocess.call(['ip', 'route', 'add', '10.211.0.0/16', 'protocol', 'kernel', 'scope', 'link', 'src', '10.211.1.54', 'dev', self.vpn_adapter])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '10.211.254.254', 'dev', self.vpn_adapter])

	
	# restore route table settings
	def restore_default_route(self):
		subprocess.call(['ip', 'route', 'del', self.ip])
		# static "10.211.0.0/16". I'm not worry about this line:)
		# subprocess.call(['ip', 'route', 'del', '10.211.0.0/16'])
		subprocess.call(['ip', 'route', 'change', 'default', 'via', '192.168.0.1', 'dev', 'eth0'])


    # switch connection states: connect or disconnect
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

