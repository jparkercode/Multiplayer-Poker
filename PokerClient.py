# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 22:51:53 2019

@author: Elise Ducharme, Kevin Mortimer, Justin Parker
"""


#If user presses T the chat will pop up if they press q it will remove it.
import socket
import nest_asyncio
import asyncio
import keyboard
import os
class client:
    #Initializes connection with the server which is already running.
    def __init__(self):
        self.serverName = '127.0.0.1' #insert IP address here
        self.inGame = True
        self.serverPort = 9999
        self.sent = False
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.serverName,self.serverPort))
        self.sentence = ""
        self.fileChatLog = open('pokerChatLog','w+') #used for dual chat and game console
        self.filePokerLog = open('pokerGameLog','w+')
        nest_asyncio.apply()
        asyncio.get_event_loop().create_task(self.userChatLoop())
        self.gameLoop()
    #Prints everthing from the server unless it is a chat message(chat isnt working tho.).
    def recieve(self):   
        recieved = False
        while(not recieved):
            modifiedSentence = self.clientSocket.recv(1024).decode()
            if(not(modifiedSentence == " ")):
                recieved = True
            self.sentence = modifiedSentence
            if(not self.sentence[0-3] == 'CHAT'):
                print('From Server:', modifiedSentence) 
                self.filePokerLog.write(self.sentence)
    #Returns information back to the Server.
    def send(self,x):
        sent = False
        while(not sent):
            x = self.clientSocket.send(x)
            if(x>0):
                sent = True
                print("sent")
    #USER WAITS FOR INSTRUCTION FROM SERVER, TO COMMANDS get bet and gameOver will cause user Action.
    def gameLoop(self):
        while(self.inGame):
           self.recieve()
           if(self.sentence=='get bet'):
               bet = input('Enter Bet: ')
               self.clientSocket.send(bet.encode())
           if(self.sentence=='gameOver'):
               self.inGame = False
    #NOT USED           
    async def userChatLoop(self):
        chat = False
        sentence = ''
        while(self.inGame):
            self.recieve()
            if(self.sentence=='CHAT?'and chat):
                self.send('CHAT'+sentence)
                chat = False
            else:
                self.send('CHAT!')
            if(self.sentence[0-3]=='CHAT'):
                self.fileChatLog.write(self.sentence+'\n')
            try:
                if(keyboard.is_pressed('t')):
                    os.system('cls')
                    for s in self.fileChatLog:
                        print(s)
                    sentence = input('Enter Chat: ')
                    chat =  True
            except:
                print()
            if(keyboard.press('q')):
                os.system('cls')
                for s in self.filePokerLog:
                    print(s)
cli = client()