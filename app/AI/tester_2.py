import multiprocessing
import os
from re import X
import socket
import subprocess
import sys
import time
from multiprocessing import Process, Lock
import pickle


def server_func(start_command_Server, start_command_AI):  # Starts the server
    server = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, bufsize=0)  # creates a cmd for the server
    server.stdin.write(b"wsl\r\n")  # enters wsl via cmd
    server.stdin.flush()  # need to flush after each input
    server.stdin.write(bytes(start_command_Server, encoding='utf8'))  # enter the command to start the game
    server.stdin.flush()
    server.stdin.close()  # close input
    ai = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, bufsize=0)  # creates a cmd for the AI
    ai.stdin.write(b"wsl\r\n")  # enters wsl via cmd
    ai.stdin.flush()
    ai.stdin.write(bytes(start_command_AI, encoding='utf8'))  # enter the command to start the AI
    ai.stdin.flush()
    ai.stdin.close()
    server.wait()  # wait until process is done
    ai.wait()


def human_func(sock, server_address, close_event, rounds, path):  # starts the human player
    human = "human"  # name of player
    sock.connect(server_address)  # the socket connects to the server using the ip and port
    sock.send(human.encode())
    go_message = sock.recv(1024)  # receive a go message
    print("first msg: ", go_message.decode())
    x = 0
    # self.id = None
    # self.maxRound = 0
    # self.aiact = ''
    # self.humanact = ''
    # self.aimes = ''
    # self.humanmes = ''
    flagA = "flagA"
    for i in range(0, rounds):
        flag = True
        flag2 = True
        while flag:
            dir_list = os.listdir(f'pickledgames{path}/')
            for f in dir_list:
                if f != "flagH":
                    time.sleep(1.5)
                else:
                    os.remove(f"pickledgames{path}/flagH")
                    infile = open(f'pickledgames{path}/game', 'rb')
                    pkl = pickle.load(infile)
                    infile.close()
                    print("send player msg")
                    player_msg = pkl["humanmes"]  # gets the msg from the main script
                    sock.send(player_msg.encode())  # sends a msg to the AI
                    # time.sleep(5)  # can be removed maybe
                    print("player msg was recived")
                    print("before receiving the chat ...............")
                    ai_msg = sock.recv(1024)  # receives a msg
                    pkl["aimes"] = ai_msg.decode()    # sends the msg to the main script
                    outfile = open(f'pickledgames{path}/game', 'wb')
                    pickle.dump(pkl, outfile)
                    outfile.close()
                    outfile = open(f'pickledgames{path}/{flagA}', 'wb')
                    pickle.dump(x, outfile)
                    outfile.close()
                    # time.sleep(5)
                    print("this is the chat received: " + "*" * 15)
                    print(ai_msg.decode())
                    while flag2:
                        dir_list = os.listdir(f'pickledgames{path}/')
                        for g in dir_list:
                            print(g)
                            if g != "flagH":
                                time.sleep(1.5)
                            else:
                                os.remove(f"pickledgames{path}/flagH")
                                infile = open(f'pickledgames{path}/game', 'rb')
                                pkl = pickle.load(infile)
                                infile.close()
                                player_action = pkl ["humanact"]  # gets a player action
                                sock.send(player_action.encode())  # sends the action to the AI
                                print(f"before receiving the action ....... {player_action}")
                                ai_action = sock.recv(1024)  # gets the AI action
                                print("action received: " + "$" * 15)
                                pkl ["aiact"] = ai_action.decode()  # sends the msg to the main script
                                outfile = open (f'pickledgames{path}/game', 'wb')
                                pickle.dump(pkl, outfile)
                                outfile.close()
                                outfile = open(f'pickledgames{path}/{flagA}', 'wb')
                                pickle.dump(x, outfile)
                                outfile.close()
                                print(ai_action.decode())
                                print(i)
                                flag2 = False
                                flag = False
    sock.close()  # closes the connection
    close_event.set()  # sets an event to true so that the program closes


# def ai_func():  # starts the AI player


def run(rounds, path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates a socket named sock
    host = "localhost"  # gets the needed ip from the cmd input
    close_event = multiprocessing.Event()  # event variable that lets us know if the game is done
    server_start = "./CheapTalk prisoners " + str(rounds) + " 0 cheaptalk"
    AI_start = "./Solver prisoners " + str(rounds) + " S++ 1 localhost 0 cheaptalk"
    lock = Lock()
    lock.acquire()
    with open("sock.txt",
              "r+") as f:  # the port to get it we read a file that has the port number then we remove the old
        # port and put in a new one
        for line in f:
            for i in line.split():
                if i.isdigit():
                    checker = True
                    while checker:
                        port = int(i) + 10
                        result = sock.connect_ex(('localhost', port))
                        if result == 0:
                            print("Port is open")
                        else:
                            print("Port is not open")
                            checker = False

    with open("sock.txt",
              "r+") as f:
        f.truncate(0)
        f.write(str(port).strip())
        lock.release()

    server_address = (host, port)

    p1 = Process(target=server_func, args=(server_start, AI_start))  # makes the server p1
    p1.start()  # starts p1
    time.sleep(2)

    p2 = Process(target=human_func,
                 args=(
                     sock, server_address, close_event, rounds, path))  # makes the player p2 and passes them the
    # event variable
    p2.start()
    # p3 = Process(target=ai_func, args=(AI_start,))  # makes the AI p3
    # p3.start()

    while True:  # this code will keep running while the game is on
        if close_event.is_set():  # check if the event is set to True if it is then turn off the game
            p1.terminate()
            p2.terminate()
            # p3.terminate()
            sys.exit(1)

# if __name__ == '__main__':
#     run()

if __name__ == '__main__':
    # player_msg_arr = Manager().list()  # a list that has the player msg for each AI so AI 0 will be looking at slot 0
    # # of the list to see its msg this applies to the rest of the lists
    # AI_msg_arr = Manager().list()  # a list that has the AI msg
    # player_act_arr = Manager().list()  # a list that has the player action
    # AI_act_arr = Manager().list()  # a list that has the AI action
    # class aigame():
    #     def __init__(self):
    # self.id = None
    # self.maxRound = 0
    # self.aiact = ''
    # self.humanact = ''
    # self.aimes = ''
    # self.humanmes = ''
    flag = True
    while flag:
        dir_list = os.listdir("youpath/")
        if len(dir_list) != 0:
            for x in dir_list:
                print(f'this is X:{x}')
                if x == "game":
                    infile = open(f'youpath/{x}', 'rb')
                    new_dict = pickle.load(infile)
                    infile.close()
                    processes = []  # an array that has all the AIs that are running
                    rounds = new_dict["maxRound"]  # number of rounds
                    path = new_dict ["gameid"]
                    # for i in range(0, 250):
                    #     player_msg_arr.insert(0, "0")
                    #     AI_msg_arr.insert(0, "0")
                    #     player_act_arr.insert(0, "0")
                    #     AI_act_arr.insert(0, "0")
                    os.remove(f'youpath/{x}')
                    run(rounds,path)
                    flag = False
                else:
                    time.sleep(1)