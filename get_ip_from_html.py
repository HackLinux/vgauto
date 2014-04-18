import urllib2
import re


html = None

try:
	html = urllib2.urlopen('http://www.vpngate.net/en/', timeout=10)
except Exception as err:
	print 'open url failed:%s\ntrying using proxy 127.0.0.1:8087 ...'%err
	proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)

	try:
		html = urllib2.urlopen('http://www.vpngate.net/en/', timeout=10)
	except Exception as err:
		print 'open url failed again:%s\nexiting ...'%err
		exit(0)

	
'''
proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)
html = urllib2.urlopen('http://www.vpngate.net/en/', timeout=10)
'''
origin_source = html.read()

print origin_source
