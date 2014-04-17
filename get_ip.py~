import sqlite3
import threading
import PingIt


mlock = threading.RLock()

class VgServer():
	def __init__(self):
		self.conn = self.conn_db()
		self.threads = []
		self.allList = []
		self.ip_list = self.get_server()


	def conn_db(self):
		print '\nConnecting to db ...'
		return sqlite3.connect('db.sqlite3')

	
	def get_server(self):
		print '\nretrieving server ip list ...'
		return self.conn.execute('select ip_addr from DB_vpnserver where region <> "China"')
	

	def get_port(self):
		ip_selected = self.allList[0][1]
		#ip_selected = '113.128.128.139'
		print '\nget port for server:%s'%ip_selected
		port = self.conn.execute('select port from DB_servstats where id=(select id from DB_vpnserver where ip_addr="%s")'%ip_selected)
		for i in port:
			return i[0]


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
		for ip in self.ip_list:
			ip = ip[0]
			t = threading.Thread(target=self.GetLegacy, args=(ip, ), name='thread-'+ip)
			t.start()
			self.threads.append(t)
	

	# return best server ip, port
	def get_result(self):
		self.GetAll()
		self.allList = sorted(self.allList)
		ip = self.allList[0][1]		
		port = self.get_port()
		return ip, port
		self.conn.close()




if __name__ == "__main__":
	s = VgServer()
	ip, port = s.get_result()
	#s.get_port()
	#print s.get_port()[2]
	print ip, port
	


