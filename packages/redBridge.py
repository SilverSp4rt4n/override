#!/usr/bin/python3
import threading
import socket
import random
import select
import time

class redBridge:
	def __init__(self):
		#Set host and port for listening
		self.host = '0.0.0.0'
		self.port = 3764
		#Number of seconds a player can be inactive before disconnection
		self.timeout = 20 
		#Initialize gameRooms data structure
		self.gameRooms = {}
		#Open up the log file
		self.logFile = open("/var/log/redbridge.log","w")
		#Create the socket
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		#Start doing stuff
		self.begin()

	#Spawn main thread and then exit
	def begin(self):
		print("starting redBridge...")
		th1 = threading.Thread(target=self.mainThread)
		th1.daemon = True
		th1.start()
		
		th2 = threading.Thread(target=self.timeoutDaemon)
		th2.daemon = True
		th2.start()

	def timeoutDaemon(self):
		print("timeout daemon running.")
		while True:
			pins = self.gameRooms.keys()
			try:
				for pin in pins:
					self.checkPlayerTimeout(pin)
			except:
				continue
			time.sleep(10)

	#log messages and print them
	def report(self,msg):
		print(msg)
		self.logFile.write("%s\n" % (msg))
		return

	def addPlayer(self,pin,name):
		if pin not in self.gameRooms:
			return -1
		newID = 0
		while(newID in self.gameRooms[pin]["players"]):
			newID+=1
		currentTime = round(time.time())
		self.gameRooms[pin]["players"][newID] = {"schema":0,"lastActive":currentTime}
		self.sendMsg(pin,"PCONNECT %s\n" % newID)
		return newID

	def checkPlayerTimeout(self,pin):
		if pin not in self.gameRooms:
			return -1
		remove = []
		for pID in self.gameRooms[pin]["players"].keys():
			if abs(round(time.time())-self.gameRooms[pin]["players"][pID]["lastActive"]) > self.timeout:
				self.report("Player timed out: gc %s pid %s" % (pin,pID))
				self.sendMsg(pin,"PDISCONNECT %s\n" % (pID))
				remove.append(pID)
		for item in remove:
			if(pin in self.gameRooms):
				del self.gameRooms[pin]["players"][item]
		return 0

	def updatePlayerActivity(self,pin,pID):
		if pin not in self.gameRooms:	
			return -1
		if pID not in self.gameRooms[pin]["players"]:
			return -2
		self.gameRooms[pin]["players"][pID]["lastActive"] = round(time.time())
		#self.report("Updated activity for gc: %s pid: %s" % (pin,pID))

	def deliverCData(self,pin,pID,wID,xVal,yVal):
		if pin not in self.gameRooms:
			return -1
		if int(pID) not in self.gameRooms[pin]["players"]:
			return -2
		msg = "CUPDATE %s %s %s %s\n" % (pID, wID, xVal, yVal)
		while(len(msg)<1024):
			msg+="A"
		self.sendMsg(pin,msg)
		self.updatePlayerActivity(pin,pID)
		return 0

	#Create a new game room when given a new client connection
	def generateGameRoom(self,sockObj):
		pin = ""
		for i in range(4):
			pin += str(random.randint(0,9))
		while(pin in self.gameRooms):
			pin = ""
			for i in range(4):
				pin += str(random.randint(0,10))
		self.gameRooms[pin] = {"socket":sockObj,"players":{}}
		return pin
		
	#Listen for client requests
	def processClient(self,sock,pin):	
		while True:
			try:
				msg = sock.recv(4096)
				if(len(msg)>0):
					print(msg) #Need to do processing
				else:
					print("Received empty string. Closing Room...")
					del self.gameRooms[pin]
					return
			except:
				return #probably needs to be more than just this

	#Send a message to the game client
	def sendMsg(self,pin,msg):
		if(pin not in self.gameRooms):
			return -1
		try:
			self.gameRooms[pin]["socket"].send(msg.encode('utf-8'))
		except:
			print("Broken connection. Closing room...")
			del self.gameRooms[pin]
			return

	#Main thread to listen for new connections
	def mainThread(self):
		self.report("Main thread active.")
		try:
			self.sock.bind((self.host,self.port))
		except Exception as e:
			return
		self.sock.listen(20)
		self.report("RedBridge TCP Server is running on port %s" % self.port)
		while True:
			clientSock, addr = self.sock.accept()
			try:
				msg = clientSock.recv(1024).decode()
			except:
				continue
			if("CREATE ROOM" in msg):
				pin = self.generateGameRoom(clientSock)
				self.report("New Client! Pin: %s" % (pin))
				msg = "GAMECODE %s\n" % pin
				clientSock.send(msg.encode('utf-8'))
				th = threading.Thread(target=self.processClient,args=(clientSock,pin))
				th.daemon = True
				th.start()
				self.sendMsg(pin,"connected.\n")
			else:
				clientSock.send(b"Error: Malformed Request")
				clientSock.close()

