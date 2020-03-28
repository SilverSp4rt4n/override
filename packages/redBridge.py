#!/usr/bin/python3
import threading
import socket
import random
import select
import time

#Global Constants
global_timeout = 20


#Open up the log file
logFile = open("/var/log/redbridge.log","w")

#log messages and print them
def report(msg):
	print(msg)
	logFile.write("%s\n" % (msg))
	return

class Player:
	def __init__(self, gamecode, playerID, schema):
		self.gamecode = gamecode
		self.ID = playerID
		self.schema = schema
		self.lastActive = round(time.time())

class GameRoom:
	def __init__(self, gamecode, socketObject):
		self.gamecode = gamecode
		self.socketObject = socketObject
		self.players = {}
		self.default_schema = ""
		self.deadRoom = False
		self.th_comm = threading.Thread(target=self.commThread)
		self.th_comm.daemon = True
		self.th_comm.start()

	#Send a message to the game client
	def sendMsg(self, msg):
		try:
			self.socketObject.send(msg.encode('utf-8'))
		except:
			print("Broken connection. Closing room...")
			self.kill()
			return

	def kill(self):
		self.deadRoom = True

	def isDead(self):
		return self.deadRoom

	def addPlayer(self):
		newID = 0
		while(newID in self.players):
			newID+=1
		newPlayer = Player(self.gamecode, newID, self.default_schema)
		self.players[newID] = newPlayer
		self.sendMsg("PCONNECT %s\n" % newID)
		return newID

	def removePlayer(self, playerID):
		if(playerID in self.players):
			del self.players[playerID]
		else:
			return -1
		return 0

	def updatePlayerActivity(self, playerID):
		if(playerID in self.players):
			self.players[playerID].lastActive = round(time.time())
		else:
			return -1
		return 0

	def checkPlayerTimeout(self):
		global global_timeout
		remove = []
		for pID in self.players.keys():
			inactiveTime = abs( round(time.time()) - self.players[pID].lastActive)
			if inactiveTime > global_timeout:
				report("Player timed out: gc %s pid %s" % (self.gamecode,pID))
				self.sendMsg("PDISCONNECT %s\n" % (pID))
				remove.append(pID)
		for item in remove:
			self.removePlayer(item)
			
	def parseCommand(self, msg):
		msgLines = msg.split("\n")
		return msgLines

	def assignNewSchema(self, cmd):
		#retrieve player ID from schema data
		pID = cmd[1]
		#remove pID and command information
		del cmd[0]
		del cmd[1]
		#Rejoin string and assign the schema to the appropriate player
		schema = "\n".join(cmd)
		if(pID in self.players):
			self.players[pID].schema = schema
		report("New schema for player %d: %s" % (pID, schema))

	def assignDefaultSchema(self, cmd):
		#Remove command
		del cmd[0]
		schema = "\n".join(cmd)
		self.default_schema = schema
		report("New default schema for gameroom %s: %s" % (self.gamecode, self.default_schema))

	def getSchema(self, pid):
		if(pid not in self.players):
			return ""
		return self.players[pid].schema

	def deliverCData(self,pID,wID,xVal,yVal):
		if int(pID) not in self.players:
			return -2
		msg = "CUPDATE %s %s %s %s\n" % (pID, wID, xVal, yVal)
		while(len(msg)<1024):
			msg+="A"
		self.sendMsg(msg)
		self.updatePlayerActivity(pID)
		return 0

	def commThread(self):
		while True:
			try:
				msg = self.socketObject.recv(4096)
				msg = msg.decode("utf-8")
				if(len(msg)>0):
					cmd = self.parseCommand(msg)
					if("PLAYER_SCHEMA" in cmd[0]):
						self.assignNewSchema(cmd)
					elif("DEFAULT_SCHEMA" in cmd[0]):
						schema = self.assignDefaultSchema(cmd)			
				else:
					print("Received empty string. Closing Room...")
					self.kill()
					return
			except Exception as e:
				report("%s: Closing Room %s" % (e, self.gamecode))
				self.kill()
				return #probably needs to be more than just this
		

class RedBridge:
	def __init__(self):
		#Set host and port for listening
		self.host = '0.0.0.0'
		self.port = 3764
		#Number of seconds a player can be inactive before disconnection
		self.timeout = 20 
		#Initialize gameRooms data structure
		self.gameRooms = {}
		#Create the socket
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		#Start doing stuff
		self.begin()

	#Spawn main thread and then exit
	def begin(self):
		print("starting RedBridge...")
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
					self.checkDeadRooms(pin) #FIXME
			except Exception as e:
				report(e)
			time.sleep(10)

	def addPlayer(self,pin,name):
		if pin not in self.gameRooms:
			return -1
		newID = self.gameRooms[pin].addPlayer()
		return newID

	def getSchema(self, gamecode, pid):
		if(gamecode not in self.gameRooms):
			return ""
		return self.gameRooms[gamecode].getSchema(pid)

	def checkPlayerTimeout(self,pin):
		if pin not in self.gameRooms:
			return -1
		self.gameRooms[pin].checkPlayerTimeout()
		return 0

	def checkDeadRooms(self, pin):
		remove = []
		if pin not in self.gameRooms:
			return -1
		if(self.gameRooms[pin].isDead()):
			remove.append(pin)

		for pin in remove:
			del self.gameRooms[pin]

	def updatePlayerActivity(self,pin,pID):
		if pin not in self.gameRooms:	
			return -1
		if pID not in self.gameRooms[pin].players:
			return -2
		self.gameRooms[pin].updatePlayerActivity(pID)
		#report("Updated activity for gc: %s pid: %s" % (pin,pID))

	def deliverCData(self,pin,pID,wID,xVal,yVal):
		if pin not in self.gameRooms:
			return -1
		return self.gameRooms[pin].deliverCData(pID, wID, xVal, yVal)
		

	#Create a new game room when given a new client connection
	def generateGameRoom(self,sockObj):
		pin = ""
		for i in range(4):
			pin += str(random.randint(0,9))
		while(pin in self.gameRooms):
			pin = ""
			for i in range(4):
				pin += str(random.randint(0,10))
		self.gameRooms[pin] = GameRoom(pin, sockObj)
		return pin

	#Main thread to listen for new connections
	def mainThread(self):
		report("Main thread active.")
		try:
			self.sock.bind((self.host,self.port))
		except Exception as e:
			return
		self.sock.listen(20)
		report("RedBridge TCP Server is running on port %s" % self.port)
		while True:
			clientSock, addr = self.sock.accept()
			try:
				msg = clientSock.recv(1024).decode()
			except:
				continue
			if("CREATE ROOM" in msg):
				pin = self.generateGameRoom(clientSock)
				report("New Client! Pin: %s" % (pin))
				msg = "GAMECODE %s\n" % pin
				clientSock.send(msg.encode('utf-8'))
				#th = threading.Thread(target=self.processClient,args=(clientSock,pin))
				#th.daemon = True
				#th.start()
				self.gameRooms[pin].sendMsg("CONNECTED\n")
			else:
				clientSock.send(b"Error: Malformed Request")
				clientSock.close()

