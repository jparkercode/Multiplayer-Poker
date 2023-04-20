# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 22:51:23 2019

@author: parkerj12
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 20:32:35 2019

@author: parkerj12
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 19:24:46 2019

@author: parkerj12
"""
import asyncio
import nest_asyncio
import time
import array
import socket
import random
import sys
"""
Deck
Handles list of Game Cards
Shuffles Cards, aswell handles dealing cards to the players
"""
class Deck:
    global Suit
    global Ranks
    Suit = ['HEART','DIAMOND','CLOVER','SPADE']
    Ranks = [['ACE',13],['KING',12],['QUEEN',11],['JACK',10],['TEN',9],['NINE',8],['EIGHT',7],['SEVEN',6],['SIX',5],['FIVE',4],['FOUR',3],['THREE',2],['TWO',1]]
    cards = []
    def Deck(self):
        self.initializeCards()
        self.shuffle()
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self,player):
        player.hand.cards.append(self.cards.pop())
        player.hand.cards.append(self.cards.pop())
    def initializeCards(self):
        for x in range(4):
            for y in range(13):
                card = Card(Suit[x],Ranks[y])
                self.cards.append(card)
"""
Card deals with the properties and printing of cards as used in the deck
"""
class Card: 
    global suit
    global rank
    def __init__(self,suit1,rank1):
        self.suit = suit1
        self.rank = rank1
    def toString(self):
        return ("Rank: "+self.rank[0]+" Suit: "+self.suit)
        
class PlayerHands:
    
    def __init__(self):
        self.cards = []
    def getCard(self,x):
        return self.cards[x]
    def clear(self):
        self.cards.clear()
    
"""
keeps track of players game cards
"""        
class GameLoop:
    global game1
    def main(self):
       game1 = GameFlow()
       game1.setRound(0)
       players  = input('Player Amount: ')
       game1.setPlayers(int(players))
       game1.initPlayers()
       nest_asyncio.apply()
       asyncio.get_event_loop().create_task(game1.userChatLoop())
       while(not game1.gameOver):

           game1.flow()
       self.main() 
           
"""
is used to keep the game flowing
"""                
class GameFlow:
    def __init__(self):
        global Round
        Round = ['Preflop','flop','turn','river']
        global gameRound
        self.gameRound = 0
        global playerAmount
        playerAmount = 2
        global players
        players = []
        global playersTurn
        self.pot = 0
        global call
        self.call = 0
        global minraise
        self.minraise = 50
        global bigBlindSeat
        global smallBlindSeat
        self.bigBlindSeat = 1
        self.smallBlindSeat = 0
        self.bigBlind = 100
        self.smallBlind = 50
        self.toCall = 0
        self.soloLeft = False
        global deck
        self.deck = Deck()
        global cards
        self.cards = []
        self.connections = []
        self.anAllIn = False
        self.allWent = False
        self.toAllWent = 0
        self.gameOver = False
    def setPlayers(self,x):
        self.playerAmount = x
    def advanceRound(self):
        if(Round[self.gameRound]=="river"):
            Print=("checking winner")
            self.sendAll(Print)
            self.checkWinner()
        self.gameRound = (self.gameRound+1)%4
        if(Round[self.gameRound]=='Preflop'):
            Print=("preflop")
            self.sendAll(Print)
            self.resetRound()
            
        if(Round[self.gameRound]=='flop'):
            Print=("pot: "+str(self.pot))
            self.sendAll(Print)
            Print=("flop")
            self.sendAll(Print)
            for i in range(3):
                self.cards.append(self.deck.cards.pop())
                Print=(self.cards[i].toString())
                self.sendAll(Print)
            self.resetInnerRound()
            
        if(Round[self.gameRound]=='turn' or Round[self.gameRound]=='river'):
            Print=("pot: "+str(self.pot))
            self.sendAll(Print)
            Print=("turn/river")
            self.sendAll(Print)
            self.cards.append(self.deck.cards.pop())
            Print=(self.cards[-1].toString())
            self.sendAll(Print)
            self.resetInnerRound()
        
        
        
            
    def setRound(self,x):
        self.gameRound = x
    """
    InitPlayers used to setup connections with players and save here connection objects aswell as dealing the cards
    """
    def initPlayers(self):
    
        serverPort = 9999
        self.connections = []
        playerscount = 0
        gameStarted = False
        onplayer = -1
        pastplayer = -2
        serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serverSocket.bind(('',serverPort))
        serverSocket.listen(10)
        print ('The server is ready to receive')
        serverSocket.settimeout(1)
        while playerscount<self.playerAmount:
            try:
                
                sock = serverSocket.accept()
                try:
                    if(self.connections.count(sock)==0):
                        self.connections.append(sock)
                        newPlayer = Player()
                        players.append(newPlayer)
                        newPlayer.playerSeat = playerscount
                        newPlayer.connection = sock
                        if(playerscount==0):
                            newPlayer.smallBlind = True
                        if(playerscount==1):
                            newPlayer.bigBlind = True
                        playerscount = playerscount+1
                        print("new connection accepted")
                except:
                     print('wtf is wrong'+str(sys.exc_info()[0]))
                    #print ('Connected with ' + str(connections[players-1][0]) + ':' + str(connections[players-1][1]))
            except:
                print('waiting...')
                #
                #if(not pastplayer==onplayer):
                #print("Player: "+str(onplayer))
        
                #for i in range(players):
                
                 #   sentence = connections[onplayer][0].recv(1024).decode()
                 #   capitalizedSentence = sentence.upper() 
                 #   connections[onplayer][0].send(capitalizedSentence.encode())
                 #   pastplayer = onplayer
                 #   onplayer = (onplayer+1)%players
        
        self.deck.initializeCards()
        self.deck.shuffle()            
        for p in players:
            self.deck.deal(p)
            """
            part of the game flow loops through all players and recieves there bets for the current round if they are eligible to bet
            """
    def playersBet(self):
        allCalled = False
        ranOnce = False
        self.soloLeft = False
        count = 0
        ranCounter = 0
        runCount = 0
        while(not allCalled and not self.allWent):
            for p in players:
                runCount +=1
                if(self.soloLeft):
                    self.setRound(3)
                    allCalled = True
                    break
                if(self.anAllIn and self.allWent):
                    break
                if(allCalled and ranOnce):
                    break
                if(not p.getFolded() and not p.allIn and not p.lost):
                    betaccepted = False
                    while(not betaccepted):
                        
                        self.toCall = abs(self.call-p.roundBet)
                        Print=("to call: "+str(self.toCall))
                        self.sendAll(Print)
                        p.playerGetBet()
                        if(str(p.bet).upper()=="FOLD"):
                            p.fold
                            betaccepted = True
                        elif(self.validBet(p.bet) and (not p.getFolded())):
                            self.call = p.roundBet
                            p.sendBet(p.bet)
                            Print = ('Player: '+str(p.playerSeat)+' Bet: '+str(p.bet))
                            self.sendAll(Print)
                            self.pot = self.pot + p.bet
                            betaccepted = True
                            if(p.allIn and not self.anAllIn):
                                print('an All in')
                                self.anAllIn = True
                        count = 0
                        for p in players:
                            if(not p.getFolded() and (not p.allIn) and not p.lost): #and runCount>=self.playerAmount
                                count +=1
                        if(count==1 and not self.anAllIn):
                            print('Solo Left')
                            self.soloLeft = True
                            break
                        if(count==0):
                            self.allWent = True
                            allCalled = True
                            break
                        if(betaccepted and (runCount>=self.playerAmount)):
                            allEqual = True
                            for p in players:
                                if(not p.getFolded()):
                                    for q in players:
                                        if(not q.getFolded()):
                                            if(not(p.totalBet==q.totalBet)):
                                                allEqual = False
                            if(allEqual):
                                allCalled = True
                                print("All Equal")
                            if(allEqual and self.anAllIn):
                                self.allWent = True
                ranCounter +=1
                if(ranCounter>=self.playerAmount):
                    ranOnce = True
    """
    used to ensure quality of user inputted bet must be atleast equal to the toCall amount or aove the minraise
    """                      
    def validBet(self,bet):
        if bet==self.toCall or ((int(bet)>= (self.toCall+self.minraise))) :
            Print=('Accepted')
            self.sendAll(Print)
            return True
        else:
            return False 
    """
    Determines winner of betting round based on either there being one remaining player or there hand rank determined in the getRank method
    """
    def checkWinner(self):
        if(self.soloLeft):
            for p in players:
                if(not p.getFolded()):
                    Print=(str(p.playerSeat)+" Wins Round with pot of "+str(self.pot))
                    self.sendAll(Print)
                    p.balance += self.pot
                    return 0
        rankList = []
        for p in players:
            if(not p.getFolded() and not p.lost):
                card1 = p.hand.getCard(0)
                card2 = p.hand.getCard(1)
                p.rank = self.getRank(p,card1, card2)
                rankList.append(p.rank)
        maxrank = max(rankList)
        winner = []
        for p in players:
            if(not p.getFolded() and not p.lost):
                if(p.rank == maxrank):
                    winner.append(p)
       # print("Winner Length: "+str(len(winner)))
        prevMax = max(winner[0].cardsInvolved)
        maxPlayer = [winner[0]]
        if(len(winner)>1):
            for w in winner:
                if (not (w == winner[0])) and w.includesHand and max(w.cardsInvolved)>prevMax:
                   prevMax = max(w.hand.getCard(0).rank[1],w.hand.getCard(1).rank[1])
                   maxPlayer[0] = w
                if (not (w == winner[0])) and w.includesHand and max(w.cardsInvolved)==prevMax:
                    maxPlayer.append(w)
        if(len(maxPlayer)>1):
            index = 0
            for w in maxPlayer:
                if (not index == len(maxPlayer)-1) and w==maxPlayer[index+1]:
                    maxPlayer.remove(w)
                index+=1
        for w in maxPlayer:
            Print =(str(w.playerSeat)+" Wins Round with amount of "+str(self.pot/len(maxPlayer)))
            self.sendAll(Print)
            w.balance += self.pot/len(maxPlayer)
        self.checkGameWinner()
        return 0   
    def checkGameWinner(self):
        count = 0
        for p in players:
            if(p.balance == 0):
                p.lost = True
                p.sendServerEvents('gameOver')
            if(not p.lost):
               count+=1
        if(count==1):
            for p in players:
                if(not p.lost):
                    Print = ('Player '+str(p.playerSeat)+' has Won the Game!!!')
                    self.sendAll(Print)
                    p.sendServerEvents('gameOver')
                    self.gameOver = True
                    
    """
    looks at players hand and determines there strength based on the predetermined rules of poker.
    """
    def getRank(self,p,card1,card2):
        suited  = 0
        matches = 0
        matches2 = 0
        matchesboard =0
        matchesboardCards = []
        paired = False
        flush = False
        straight = False
        cardRank = []
        cardSuit = []
        self.allCards = self.cards.copy()
        self.allCards.append(card1)
        self.allCards.append(card2)
        
        for c in self.allCards:
            cardRank.append(c.rank[1])            
            cardSuit.append(c.suit)
        #get paired
        if(card1.rank == card2.rank):
            matches +=1
            paired = True
        matches += cardRank.count(card1.rank)  
        
        #check flush
        for i in range(2):
            if(cardSuit.count(card1.suit)==5):
                p.cardsInvolved.append(card1.rank[1])
                flush = True
            if(cardSuit.count(card2.suit)==5):
               p.cardsInvolved.append(card2.rank[1])
               flush = True
            if cardSuit.count(self.cards[0].suit)==5:
                flush = True
                p.includesHand= False
        #check straight and Straigh Flus
        cardRank.sort()
        sequence = 0
        index = 0
        sFlush = False
        check = True
        straightCards = []
        for c in cardRank:
            prev = cardRank[index+1]
            if(abs(prev-c==1)):
                sequence +=1
                straightCards.append(prev)
                for d in self.allCards:
                    suit1 = []
                    suit2 = []
                    if(d.rank[1]==c):
                        suit1.append(d.suit)
                    if(d.rank[1]==prev):
                        suit2.append(d.suit)
                index = 0
                if(check):
                    for s in suit1:
                        if(suit2.count(s)>=1):
                            sFlush = True
                        else:
                            sFlush = False
                        index +=1
                        if(index==len(suit1) and not sFlush):
                            check = False
            else:
                sequence =0
                straightCards.clear()
        if(sequence>=5):
            straight = True
            p.cardsInvolved = straightCards.copy()
            if not (straightCards.count(card1)==1 or straightCards.count(card2)==1):
                p.includesHand = False
        #Royal Flush
        if straight and (self.allCards.count(13)>=1 and self.allCards.count(12)>=1 and self.allCards.count(11)>=1) and flush:
            Print=(str(p.playerSeat)+" has a royal flush")
            self.sendAll(Print)
            return 10
        
        #Straight Flush
        if sFlush:
            Print=(str(p.playerSeat)+" has a straight flush")
            self.sendAll(Print)
            return 9
        fourKind = False
        #Four of a Kind
        for c in self.allCards:
            if(cardRank.count(c.rank[1])==4):
                p.cardsInvolved.append(c.rank[1])
                fourKind = True
        if(fourKind):
            Print=(str(p.playerSeat)+" has four of a kind")
            self.sendAll(Print)
            return 8
       
        #Full house
        if(cardRank.count(card1.rank[1])==3 and cardRank.count(card2.rank[1])==2) or (cardRank.count(card1.rank[1])==2 and cardRank.count(card2.rank[1])==3):
            p.cardsInvolved.append(card1.rank[1])
            p.cardsInvolved.append(card2.rank[1])
            Print=(str(p.playerSeat)+" has fullhouse")
            self.sendAll(Print)
            return 7
        #Flush
        if flush:
            Print=(str(p.playerSeat)+" has a flush")
            self.sendAll(Print)
            return 6
        #Straight
        if straight:
            Print=(str(p.playerSeat)+" has a straight")
            self.sendAll(Print)
            return 5
        #THREE OF A KIND
        threeKind = False
        for c in self.allCards:
            if(cardRank.count(c.rank[1])>=3):
                p.includesHand = True
                p.cardsInvolved.append(c.rank[1])
                threeKind = True
        if(threeKind):
            Print=(str(p.playerSeat)+" has a three of a kind")
            self.sendAll(Print)
            return 4       
        #TWO PAIR
        if(cardRank.count(card1.rank[1])==2 and cardRank.count(card2.rank[1])==2 and not paired):
            p.includesHand = True
            p.cardsInvolved.append(card1.rank[1])
            p.cardsInvolved.append(card2.rank[1])
            Print=(str(p.playerSeat)+" has two pair")
            self.sendAll(Print)
            return 3
        #PAIR
        if cardRank.count(card1.rank[1])==2 or paired:
            p.includesHand = True
            p.cardsInvolved.append(card1.rank[1])
            Print=(str(p.playerSeat)+" has a pair")
            self.sendAll(Print)
            return 2
        if cardRank.count(card2.rank[1])==2:
            p.includesHand = True
            p.cardsInvolved.append(card2.rank[1])
            Print=(str(p.playerSeat)+" has a pair")
            self.sendAll(Print)
            return 2
        #HIGH CARD
        p.cardsInvolved.append(card1.rank[1])
        p.cardsInvolved.append(card2.rank[1])
        p.includesHand = True
        Print = (str(p.playerSeat)+" has highcard")
        self.sendAll(Print)
        return 1
        
    def postBlinds(self):
        self.smallBlindSeat = (self.smallBlindSeat+1)%self.playerAmount
        self.bigBlindSeat = (self.bigBlindSeat+1)%self.playerAmount
        self.playersTurn = self.smallBlindSeat
        for p in players:
            if(p.playerSeat==self.bigBlindSeat):
                p.bigBlind = True
            elif(p.playerSeat==self.smallBlindSeat):
                p.smallBlind = True
    def resetInnerRound(self):
        for p in players:
            p.roundBet = 0
        self.call = 0
        self.toCall = 0
    def resetRound(self):
        self.resetInnerRound()
        self.deck.cards.clear()
        self.deck.initializeCards()
        self.deck.shuffle()
        for p in players:
            if(not p.lost):
                p.hand.clear()
                self.deck.deal(p)
                p.unFold()
                p.totalBet = 0
                if(p.balance<=0):
                    p.lost = True
                p.includesHand = False
                p.cardsInvolved.clear()
                p.allIn = False
        self.call = 0
        self.toCall = 0
        self.pot = 0
        self.postBlinds()
        self.cards.clear()
        self.anAllIn = False
        self.allWent = False
        p = players.pop(0)
        players.append(p)
    '''
    loops through all the players to send game events
    '''
    def sendAll(self,x):
        time.sleep(.01)
        for con in self.connections:
            con[0].send(x.encode())
    
    async def userChatLoop(self):
        while(True):
            for c in self.connections:
                c[0].send('chat?')
                chat = c[0].recv(1024).decode()
                if(chat != 'chat!'):
                    self.sendAll(chat)
    '''
    this is how the game of poker flows through with two major events betting and cards coming out with advancement of rounds.
    '''
    def flow(self):

        self.playersBet()
        self.advanceRound()
   
    
        
'''
 all info of the player is stored server side and info is transmitted to individual players based on the connection established
'''   
class Player:
    def __init__(self):
        global folded
        self.folded = False
        global balance
        self.balance = 500
        self.hand = PlayerHands()
        self.handRank = 0
        self.bigBlind = False
        self.smallBlind = False
        self.allIn = False
        self.lost = False
        self.totalBet = 0
        self.roundBet = 0
        global playerSeat
        self.playerSeat = -1
        global bet
        self.includesHand = False
        self.cardsInvolved = []
        self.bet = -1
        self.connection = None
        self.time = 0
    def getFolded(self):
        return self.folded
    def sendBet(self,x):
        self.bet = x
        self.balance -=x
    def fold(self):
        self.folded = True
    def unFold(self):
        self.folded = False
    def addBal(self,x):
        self.balance +=x
    def getBal(self):
        return self.balance
    def sendServerEvents(self,x):
        sent = False
        time.sleep(.5)
        while(not sent):
            x=self.connection[0].send(x.encode())
            if(x>0):
                sent = True
                print("sent")
                        
    def playerGetBet(self):
        #game1.sendAll(self.playerSeat)
        self.sendServerEvents('Balance: '+str(self.balance))
        self.sendServerEvents(('Cards: '+self.hand.getCard(0).toString()+" "+self.hand.getCard(1).toString()))
            
        if(self.smallBlind):
            self.smallBlind = False
            self.bet = 50
            if(self.bet>=self.balance):
                print('ALL IN')
                self.bet = self.balance
                self.allIn = True
                self.totalBet += self.balance
                self.roundBet += self.balance
                return self.balance
            self.roundBet += self.bet
            self.totalBet += self.bet
            #game1.sendAll('bet:'+str(50))
            self.sendServerEvents(('bet:'+str(50)))
            return 50
        if(self.bigBlind):
            self.bigBlind = False
            self.bet = 100
            if(self.bet>=self.balance):
                print('ALL IN')
                self.bet = self.balance
                self.allIn = True
                self.totalBet += self.balance
                self.roundBet += self.balance
                return self.balance
            self.roundBet += self.bet
            self.totalBet += self.bet
           # game1.sendAll('bet:'+str(100))
            self.sendServerEvents(('bet:'+str(100)))
            return 100
        self.sendServerEvents(('get bet'))
        userBet = 0
        recieved = False
        modifiedSentence = " "
        while(not recieved):
            modifiedSentence = self.connection[0].recv(1024).decode()
            if(not(modifiedSentence == " ")):
                recieved = True
        userBet = modifiedSentence
        if(userBet.lower()=='fold'):
            self.bet  = 'FOLD'
            self.fold()
            return 'FOLD'
        self.bet = int(userBet)
        if(self.bet>=self.balance):
            print('ALL IN')
            self.bet = self.balance
            self.allIn = True
            self.totalBet += self.balance
            self.roundBet += self.balance
            return self.balance
        self.totalBet += int(self.bet)
        self.roundBet += int(self.bet)
        return self.bet
    
GameLoop = GameLoop()
GameLoop.main()