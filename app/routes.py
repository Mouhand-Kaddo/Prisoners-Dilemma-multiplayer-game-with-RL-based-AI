import json
import os
from flask_login.utils import login_required
from app import LookingForGame, app, db, socketio, Games, send, emit, processes, MMLock, importantbool
from app.models import User, Match
from flask import jsonify,render_template, flash, redirect, url_for, session, request
from app.forms import *
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime
from app.Users import userr
from app.matchmake import Matchmake
import time
from multiprocessing import Pipe
import pickle

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.rememberMe.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # user.group = 'AI'
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/findgame', methods=['GET'])
@login_required
def findGame():
    # return Matchmake()
    return render_template('findm.html', title='Find game')


@app.route('/serveGame', methods=['GET'])
@login_required
def serveGame():
    if current_user.can_access_game == 'y':
        current_user.can_access_game = 'n'
        db.session.commit()
        return render_template('play.html', title='Play', username=current_user.username)
    else:
        return render_template('findm.html', title='Find game')


@socketio.on('find match')
def findMatchSock(data):
    Matchmake()
    current_user.can_access_game = 'y'
    db.session.commit()
    emit('redirect', {'url': url_for('serveGame')})


@socketio.on('disconnect')
def test_disconnect():
    # disconnectingfromgame = True
    try:
        MMLock.acquire()  # critical section
        for p in LookingForGame:
            if p.name == current_user.username:
                # disconnectingfromgame = False
                p.disconnected = True
                p.flag = True
                LookingForGame.remove(p)
                print(f'Deleting {p.name}')
                break
        MMLock.release()  # Release the mutex lock
    except:
        print("An exception occurred")
    finally:
        print("Done disconnecting")


@socketio.on('disfind match')
def disfindMatchSock(data):
    # game = findTheGame(current_user.username)
    MMLock.acquire()  # critical section
    for p in LookingForGame:
        if p.name == current_user.username:
            p.disconnected = True
            p.flag = True
            LookingForGame.remove(p)
            print(f'Deleting {p.name}')
            break
    MMLock.release()  # Release the mutex lock


@socketio.on('message')
def message(data):
    print(f' name is { data["username"] }')
    # Get the game
    game = findTheGame(data["username"])
    # If its an ai game call ai handler
    if game.ai == 1:
        handleAiMsg(game, data)
    # else do normal message processing (Human vs Human)
    else:
        # Check who sent a message and set their flag accordingly
        if game.player1.name == data["username"]:
            game.player1sentM = True
        elif game.player2.name == data["username"]:
            game.player2sentM = True
        messagelist, notused = parseMessage(data["msg"])
        # Unlock the action input on client after both clients sent messages
        if game.player1sentM == True and game.player2sentM == True:
            emit('unlock', "1", room=game.player2.sid)
            emit('unlock', "1", room=game.player1.sid)
            # Reset the flags
            game.player2sentM = False
            game.player1sentM = False
        # Send the message to both clients
        # If the message is empty set the message to:said nothing
        if len(messagelist) == 0:
            thisdict = {
                "mes": "said nothing",
                "un": current_user.username
            }
            emit('message', thisdict, room=game.player1.sid)
            emit('message', thisdict, room=game.player2.sid)
        # If there is an actual message then send it    
        else:
            for mes in messagelist:
                thisdict = {
                    "mes": mes,
                    "un": current_user.username
                }
                emit('message', thisdict, room=game.player1.sid)
                emit('message', thisdict, room=game.player2.sid)


def handleAiMsg(game, data):
    # parsing human message
    textformsg, msgincodeform = parseMessage(data["msg"])
    # sending human message back to human
    # If human said nothing
    if len(textformsg)==0:
        thisdict = {
            "mes": "said nothing",
            "un": current_user.username
        }
        emit('message', thisdict, room=game.player1.sid)
    for mes in textformsg:
        thisdict = {
            "mes": mes,
            "un": current_user.username
        }
        emit('message', thisdict, room=game.player1.sid)
    # sending human message to ai
    path = f'app/AI/pickledgames{game.id}'
    filename = f'{path}/game'
    infile = open(filename,'rb')
    aigame = pickle.load(infile)
    infile.close()
    aigame['humanmes'] = msgincodeform
    outfile = open(filename,'wb')
    pickle.dump(aigame, outfile)
    outfile.close()
    # Create the flag to notify ai that message is sent
    flagfilename = f'{path}/flagH'
    outfile = open(flagfilename,'wb')
    # Variable just to use dump in pickle
    x = 0
    pickle.dump(x, outfile)
    outfile.close()
    # waiting for ai message
    flagg = True
    while(flagg):
        dir_list = os.listdir(path)
        for f in dir_list:
            if f =='flagA':
                time.sleep(1.5)
                print('created flag a')
                # reset the flag by removing it
                os.remove(f'{path}/flagA')
                infile = open(filename,'rb')
                aigame = pickle.load(infile)
                infile.close()
                txt, code = parseMessage(aigame['aimes'])
                # If AI said nothing
                if len(txt) == 0:
                    thisdict = {
                        "mes": "said nothing",
                        "un": ''
                    }
                    emit('message', thisdict, room=game.player1.sid)
                # If AI said something
                else:
                    for mes in txt:
                        thisdict = {
                            "mes": mes,
                            "un": ''
                        }
                        emit('message', thisdict, room=game.player1.sid)
                emit('unlock', "1", room=game.player1.sid)
                flagg = False
                break
            else:
                continue


@socketio.on('action')
def action(data):
    playernum = 0  # This variable to know if it's player 1 or 2, it's not the best way I know
    # Get the game
    game = findTheGame(data["username"])
    # If its an ai game call ai handler
    if game.ai == 1:
        handleAiact(game, data)
    # else do normal action processing (Human vs Human)
    else:
        # Check who sent an action and set their flag accordingly
        if game.player1.name == data["username"]:
            game.player1sentA = True
            game.player1choices += f'/ {data["act"]}'  # Update choices
            playernum = 1  # The hacky solution
        elif game.player2.name == data["username"]:
            game.player2sentA = True
            game.player2choices += f'/ {data["act"]}'  # Update choices
            playernum = 2  # The hacky solution

        # If both players made an action:
        if game.player1sentA == True and game.player2sentA == True:
            # Reset flags
            game.player1sentA = False
            game.player2sentA = False
            # Increment round
            game.round += 1
            # Get, update, and send score
            calScore(game)
            # Dict that holds score message
            # This is where we use the hacky solution
            if playernum == 1:
                thisdict1 = {
                    "mes": str(game.p1score),
                    "un": current_user.username
                }
                thisdict2 = {
                    "mes": str(game.p2score),
                    "un": game.player2.name
                }
                action1 = {
                "mes": action_code_to_msg(game.player1choices[-1]),
                "un": current_user.username
                }
                action2 = {
                "mes": action_code_to_msg(game.player2choices[-1]),
                "un": game.player2.name
                }
            else:
                thisdict1 = {
                    "mes": str(game.p2score),
                    "un": current_user.username
                }
                thisdict2 = {
                    "mes": str(game.p1score),
                    "un": game.player1.name
                }
                action1 = {
                "mes": action_code_to_msg(game.player2choices[-1]),
                "un": current_user.username
                }
                action2 = {
                "mes": action_code_to_msg(game.player1choices[-1]),
                "un": game.player1.name
                }
            # Send actions to clients
            emit('message', action1, room=game.player1.sid)
            emit('message', action2, room=game.player2.sid)
            emit('message', action2, room=game.player1.sid)
            emit('message', action1, room=game.player2.sid)
            # Sending both scores to both clients
            emit('score', thisdict2, room=game.player2.sid)
            emit('score', thisdict2, room=game.player1.sid)
            emit('score', thisdict1, room=game.player2.sid)
            emit('score', thisdict1, room=game.player1.sid)
            # Unlock send button
            emit('unlock send', "1", room=game.player2.sid)
            emit('unlock send', "1", room=game.player1.sid)
            # End game if rounds exceeded
            if game.round > game.maxRound:
                EndGame(game)
                current_user.left_properly = 'y'
                db.session.commit()

def action_code_to_msg(code):
    if code == '1':
        return 'defected'
    else:
        return 'cooperated'
def calScore(game):
    # Both defect
    if game.player1choices[-1] == '1' and game.player2choices[-1] == '1':
        game.p1score += 20
        game.p2score += 20
    # Both coop
    elif game.player1choices[-1] == '0' and game.player2choices[-1] == '0':
        game.p1score += 60
        game.p2score += 60
    # player 1 defects but player 2 coop
    elif game.player1choices[-1] == '1' and game.player2choices[-1] == '0':
        game.p1score += 100
        game.p2score += 0
    # player 1 coop but player 2 defects
    elif game.player1choices[-1] == '0' and game.player2choices[-1] == '1':
        game.p1score += 0
        game.p2score += 100


def handleAiact(game, data):
    # saving human choice
    game.player1choices += f'/ {data["act"]}'
    # sending human choice back to human to display
    thisdict = {
        "mes": data["msg"],
        "un": current_user.username
    }
    emit('message', thisdict, room=game.player1.sid)
    # parsing human message to send to ai
    actstr = f'{data["act"]} $ 0.00'
    # sending human message to ai
    path = f'app/AI/pickledgames{game.id}'
    filename = f'{path}/game'
    infile = open(filename,'rb')
    aigame = pickle.load(infile)
    infile.close()
    aigame['humanact'] = actstr
    outfile = open(filename,'wb')
    pickle.dump(aigame, outfile)
    outfile.close()
    # Create the flag to notify ai that action is sent
    flagfilename = f'{path}/flagH'
    outfile = open(flagfilename,'wb')
    # Variable just to use dump in pickle
    x = 0
    pickle.dump(x, outfile)
    outfile.close()
    # waiting for ai act
    outerFlag = True
    while(outerFlag):
        dir_list = os.listdir(path)
        for f in dir_list:
            if f =='flagA':
                print(f'file is {f}')
                # reset the flag by removing it
                time.sleep(3)
                os.remove(f'{path}/flagA')
                infile = open(filename,'rb')
                aigame = pickle.load(infile)
                infile.close()
                aiact = aigame['aiact']
                # saving ai choice
                game.player2choices += f'/ {aiact[2]}'
                # Parsing ai choice
                tempact = ''
                if aiact[2] == '0':
                    tempact = "cooperated"
                else:
                    tempact = 'defected'
                thisdict = {
                    "mes": tempact,
                    "un": ''
                }
                # Sending ai message to player
                emit('message', thisdict, room=game.player1.sid)
                # Calculating and sending scores
                calScore(game)
                thisdict1 = {
                    "mes": str(game.p1score),
                    "un": current_user.username
                }
                thisdict2 = {
                    "mes": str(game.p2score),
                    "un": ''
                }
                emit('score', thisdict1, room=game.player1.sid)
                emit('score', thisdict2, room=game.player1.sid)
                # unlock messaging for client
                emit('unlock send', "1", room=game.player1.sid)
                # Increment round
                game.round += 1
                # End game if rounds exceeded
                if game.round > game.maxRound:
                    EndGameAI(game)
                    current_user.left_properly = 'y'
                    db.session.commit()
                outerFlag = False
                break


@socketio.on('register sid')
def registerSid(data):
    current_user.left_properly = 'n'
    db.session.commit()
    print(f'the user is{current_user.left_properly}')
    try:
        for game in Games:
            if game.player1.name == data:
                game.player1.sid = request.sid
            elif game.player2.name == data:
                game.player2.sid = request.sid
            else:
                continue
    except:
        print('Not an error just being cute')



def findPlayer(data):
    for game in Games:
        if game.player1.name == data:
            return game.player2.sid
        elif game.player2.name == data:
            return game.player1.sid
        else:
            continue
    return None


def findTheGame(data):
    print(f'Current games {len(Games)}')
    for game in Games:
        print(f'game is {game.player1.name}')
        if game.player1.name == data or game.player2.name == data:
            return game
    print("here is")
    return None
    


def EndGameAI(game):
    # End game for client
    print('done termi')
    emit('end game', "1", room=game.player1.sid, namespace='/')
    # For debugging
    print(f'Player 1 choices {game.player1choices}')
    print(f'Player 2 choices {game.player2choices}')
    print(f'Current round {game.round} out of {game.maxRound}')
    # Save match info to database
    m = Match.query.get(game.id)
    m.player1choices = game.player1choices
    m.player2choices = game.player2choices
    m.player1messages = game.player1msgs
    m.player2messages = game.player2msgs
    m.aimatch = game.ai
    m.player1score = game.p1score
    m.player2score = game.p2score

    db.session.commit()
    # Remove the game
    path = f'app/AI/pickledgames{game.id}'
    game.aiHandler.terminate()
    Games.remove(game)
    os.remove(f"{path}/game")



def fetchProcess(name):
    for p in processes:
        print(f'process is {p.name}')
        if p.name == str(name):
            return p


def EndGame(game):
    emit('end game', "1", room=game.player1.sid, namespace='/')
    emit('end game', "1", room=game.player2.sid, namespace='/')
    print(f'Player 1 choices {game.player1choices}')
    print(f'Player 2 choices {game.player2choices}')
    print(f'Current round {game.round} out of {game.maxRound}')
    # Save match info to database
    m = Match.query.get(game.id)
    m.player1choices = game.player1choices
    m.player2choices = game.player2choices
    m.player1messages = game.player1msgs
    m.player2messages = game.player2msgs
    m.aimatch = game.ai
    m.player1score = game.p1score
    m.player2score = game.p2score
    db.session.commit()
    # Remove the game
    Games.remove(game)

# When they leave the match while it's running
@app.route('/end',methods = ['POST', 'GET'])
@login_required
def ImproperLeave():
    print('disconnecting')
    game = findTheGame(current_user.username)
    if game == None:
        print("Other player disconnected first")
        return "The other player already closed the game"
    if game.ai == 1:
        EndGameAI(game)
        print("Ended an AI game improperly")
    else:
        EndGame(game)
        print("Ended a pvp game improperly")
    return "Success"


Acts = ['AC', 'AD', 'BC', 'BD']
Acts2 = ['-AC', '-AD', '-BC', '-BD']
Messages = ['Do as I say or I will punish you', 'I accept you last proposal', 'I dont accept your prposal', 'That is not fair', 'I dont trust you', 'Excellent!', 'Sweet. We are getting rich', 'Give me another chance', 'Okay. I forgive you',
            'I\'m changing my strategy', 'We can both do better than this', 'Curse you', 'You betrayed me', 'You will pay for this', 'In your face', 'Let\'s always play', 'This round, let\'s play', 'Don\'t play', 'Let\'s alternate between and']


def parseMessage(message):
    listf = []
    aimess = ''
    meslist = message.split(";")
    # meslist = meslist.split(" ")
    newlist = []
    for x in meslist:
        x = x.split(" ")
        newlist.append(x)

    flat_list = [item for sublist in newlist for item in sublist]
    print(flat_list)

    i = 0
    for x in flat_list:
        print(x)
        try:
            if int(x) in range(0, 15):
                listf.append(Messages[int(x)])
                aimess = aimess+";"+x
            elif int(x) in range(15, 18):
                listf.append(f'{Messages[int(x)]} {flat_list[i+1]}')
                aimess = aimess+";"+x+' '+flat_list[i+1]
            elif x == "18":
                # print(flat_list[i+1])
                # print(flat_list[i+2])
                if flat_list[i+1] in Acts and flat_list[i+2] in Acts2:
                    listf.append(
                        f'{Messages[int(x)]} {flat_list[i+1]} {flat_list[i+2].lstrip("-")}')
                    aimess = aimess+";"+x+' ' + \
                        flat_list[i+1]+' '+flat_list[i+2].lstrip("-")

        except:
            print('normal day')
        i += 1
    newaimess = aimess[1:]
    newaimess += ';$ 0.00'
    print(listf)
    print(newaimess)
    return listf, newaimess
