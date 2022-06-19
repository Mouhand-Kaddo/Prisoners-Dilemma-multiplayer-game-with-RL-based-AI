from app import  db, LookingForGame, MMLock, Games, processes
import app
from app.models import Match, User
from flask import render_template
from app.forms import *
from flask_login import current_user
from app.Users import *
import time, random
from app.AI import tester_2
import pickle
import subprocess
from pathlib import Path

def Matchmake():
    # Check which group the user belongs to
    chkusr = User.query.get(current_user.id)
    if chkusr.group == 'AI':
        prob = random.randint(1, 10)
        # Proability for AI match
        if prob in range(1, 11):
            time.sleep(1)
            return matchmakeAI()
        # prob = random.randint(1, 10)
        # # Proability for AI match
        # if prob in range(1, 11):
        #     return matchmakeAI()
        # else get human player
    print('############################')
    time.sleep(1) #sleep so two threads don't acquire at the same time
    MMLock.acquire() #critical section
    #If list is empty, wait until someone joins
    if len(LookingForGame) == 0:
        thissuser = userr()
        thissuser.name = current_user.username
        thissuser.usr_id = current_user.id
        LookingForGame.append(thissuser)
        MMLock.release() #Release the mutex lock
        while (True):
            if thissuser.flag:
                if thissuser.disconnected:
                    break
                else:
                    return "1"
                    
    #If list isn't empty, create the match
    else:
        match = Match(user1_id = current_user.id, user2_id = LookingForGame[0].usr_id)   
        LookingForGame[0].match_id = match.id
        # create a user
        thissuser = userr()
        thissuser.name = current_user.username
        thissuser.usr_id = current_user.id
        ## end create user
        # create game
        g = makegame(thissuser,0,thissuser)
        ## end create game
        db.session.add(match)
        db.session.commit()
        g.id = match.id
        LookingForGame[0].flag = True
        LookingForGame.remove(LookingForGame[0])
        MMLock.release() #Release the mutex lock
        return "1"


def matchmakeAI():
    # create a user
    thissuser = userr()
    thissuser.name = current_user.username
    thissuser.usr_id = current_user.id
    u2 = userr()
    ## end create user
    # create game
    MMLock.acquire() #critical section
    ai_id = app.AI_id
    app.AI_id+=1
    MMLock.release() #Release the mutex lock
    u2.name = str(ai_id)
    thisgame = makegame(thissuser,1,u2)
    match = Match(user1_id = current_user.id, user2_id = ai_id)
    db.session.add(match)
    db.session.commit()
    thisgame.id = match.id
    thisgame.ai_id = ai_id
    createTheAImatch(thisgame)
    return "1"

def createTheAImatch(game):
    thisgame = aigame()
    thisg = {'maxRound':game.maxRound,'aiact':'','humanact':'','aimes':'','humanmes':'', 'gameid': game.id}
    thisgame.maxRound = game.maxRound
    thisgame.id = game.ai_id
    temp = thisg ['gameid']
    print(f'this is the ai game {thisgame.id}')
    path = f'app/AI/pickledgames{temp}'
    Path(path).mkdir(parents=True, exist_ok=True)
    filename = f'app/AI/youpath/game'
    outfile = open(filename,'wb')
    pickle.dump(thisg, outfile)
    filename = f'{path}/game'
    outfile = open(filename,'wb')
    pickle.dump(thisg, outfile)
    outfile.close()

# AI code 
def AIrun(child, rounds):  # runs the AI and give it a pipe so that the process is able to talk to it
    tester_2.run(child, rounds)
       

# ai is a bool to indicate match type
def makegame(thissuser, ai, g):
    # ai vs human
    if ai == 1:
        AI = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, bufsize=0)  # creates a cmd for the server
        AI.stdin.write(b"cd app/AI\r\n")
        AI.stdin.flush()
        AI.stdin.write(b"python tester_2.py\r\n")
        thisgame = game(p1 = thissuser, p2 = g)
        thisgame.aiHandler = AI
        thisgame.ai = 1
        thisgame.maxRound = random.randint(8, 12)
        # thisgame.maxRound = 3 # Expire
        Games.append(thisgame)
    # human vs human
    else:
        thisgame = game(p1 = thissuser, p2 = LookingForGame[0])
        thisgame.maxRound = random.randint(8, 12)
        # thisgame.maxRound = 3 # Expire
        Games.append(thisgame)
    return thisgame   