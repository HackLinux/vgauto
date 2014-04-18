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

		# write tmp.html file for port searching
		html = response.read()
		with open('tmp.html', 'wb') as fw:
			fw.write(html)

		p = re.compile('\d+\.\d+\.\d+\.\d+')
		ip_list = p.findall(html)

		return ip_list


	# get ping value
	def GetLegacy(self, ip):
		p = PingIt.PingIt(ip)
		p.start()
		pingValue = p.getLegacy()
		if pingValue != -1:
			mlock.acquire()
			self.allList.append([pingValue, ip])
			mlock.release()


	# get all ping result into a list
	def GetAll(self):
		ip_list = self.get_ip_from_html()
		tmp_list = []
		for ip in ip_list:
			if ip in tmp_list:
				continue
			t = threading.Thread(target=self.GetLegacy, args=(ip, ), name='thread-'+ip)
			t.start()
			self.threads.append(t)
			tmp_list.append(ip)


	# return ip list sorted by ping value
	def get_result(self):
		self.GetAll()
		for t in self.threads:
			t.join()	
		
		self.allList = sorted(self.allList)


	def close_db():
		self.conn.close()




if __name__ == "__main__":
	s = VgServer()
	s.get_result()
	print s.allList
	
	with open('tmp.txt', 'wb') as fw:
		for i in s.allList:
			fw.write(str(i))
	


