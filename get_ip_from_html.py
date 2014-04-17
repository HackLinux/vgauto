import urllib2
import re



html = urllib2.urlopen('http://www.vpngate.net/en/')
origin_source = html.read()

for i in origin_source.split():
	if i == 'TCP: ':
		print i
	else:
		continue
