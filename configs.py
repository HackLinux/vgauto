# coding=utf-8


# start_vpn.py
# save current connected server
connected_server = 'tmp_server.log'
# save connected server history
server_history = 'server_histroy.log'


# get_ip.py
# http/https proxy server url
proxy_url = {'http': '127.0.0.1:8087'}


# get_location.py
# ip geography information database url
location_post_url = 'http://opendata.baidu.com/api.php?query=%s&resource_id=6006&oe=utf-8'


# MyVPN.py
# temporary account config file, and account params
tmp_cfg_file = 'vgp.vpn'
account_name = 'vgp1'
virtual_adapter = 'vpn_vg'
# network settings
my_gateway = '192.168.0.1'
my_adapter = 'eth0'
# tmp_cfg_file template
tmp_cfg_file_template = '''﻿# VPN Client VPN Connection Setting File
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
'''
