#!/usr/bin/python2.7
import urllib2



# get ip location
def get_region(ip):
    response = urllib2.urlopen('http://opendata.baidu.com/api.php?query=%s&resource_id=6006&oe=utf-8'%ip)

    data = response.read()[1:-1].split('"')
    index = data.index('location') + 2

    return data[index]


