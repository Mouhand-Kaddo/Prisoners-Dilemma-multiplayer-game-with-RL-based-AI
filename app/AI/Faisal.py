import os
import pickle
import sys
import time
import tester_2
from multiprocessing import Process, Manager


def run(rounds, path):  # runs the AI and give it a pipe so that the process is able to talk to it
    tester_2.run(rounds, path)


# def comm(parent, close, worker_num, player_msg_arr, AI_msg_arr, player_act_arr,
#          AI_act_arr, rounds):  # sends and receives msg and actions to and from the ai
#
#     player_msg_arr[worker_num] = "7;$ 0.00"  # gives the number of the AI the msg
#     player_act_arr[worker_num] = "1 $ 0.00"  # gives the number of the AI the act
#     for i in range(0, rounds):  # the range is the number of rounds
#         parent.send(player_msg_arr[worker_num])  # sends the msg to the AI
#         AI_msg_arr[worker_num] = parent.recv()
#         # AI_msg_arr.insert(worker_num, parent.recv())  # inserts the received action from the AI in the list
#         print(AI_msg_arr[worker_num])
#         parent.send(player_act_arr[worker_num])  # sends the msg to the AI
#         AI_act_arr[worker_num] = parent.recv()  # inserts the received action from the AI in the list
#         print(AI_act_arr[worker_num])
#     close.set()  # once all the rounds are done close the AI


# def start_AI(worker_num, player_msg_arr, AI_msg_arr, player_act_arr, AI_act_arr, rounds):
#     # close_event = multiprocessing.Event()  # very important allows the python to know if the AI is done or not by
#     # triggering an event when the AI is done
#     parent_conn, child_conn = Pipe()  # allows the sending and receiving of msg from this scripts to the AI script
#     p1 = Process(target=run, args=(child_conn, rounds))  # this starts the AI
#     p1.start()
#     # p2 = Process(target=comm, args=(parent_conn, close_event, worker_num, player_msg_arr, AI_msg_arr, player_act_arr
#     #                                 , AI_act_arr, rounds))  # starts the command sending and receiving
#     # p2.start()
#     # player_msg_arr[worker_num] = ";$ 0.00"  # gives the number of the AI the msg
#     # player_act_arr[worker_num] = "0 $ 0.00"  # gives the number of the AI the act
#     for i in range(0, rounds):  # the range is the number of rounds
#         # parent_conn.send(player_msg_arr[worker_num])  # sends the msg to the AI
#         # AI_msg_arr[worker_num] = parent_conn.recv()
#         # # AI_msg_arr.insert(worker_num, parent.recv())  # inserts the received action from the AI in the list
#         # print(AI_msg_arr[worker_num])
#         # parent_conn.send(player_act_arr[worker_num])  # sends the msg to the AI
#         # AI_act_arr[worker_num] = parent_conn.recv()  # inserts the received action from the AI in the list
#         # print(AI_act_arr[worker_num])
#     # print("Elements of given array: ")
#     # for i in range(0, len(player_msg_arr)):
#     #     print(player_msg_arr[i])
#     # print("Elements of given array: ")
#     # for i in range(0, len(AI_msg_arr)):
#     #     print(AI_msg_arr[i])
#     # print("Elements of given array: ")
#     # for i in range(0, len(player_act_arr)):
#     #     print(player_act_arr[i])
#     # print("Elements of given array: ")
#     # for i in range(0, len(AI_act_arr)):
#     #     print(AI_act_arr[i])
#     p1.terminate()
#     sys.exit(1)
#     # close_event.set()  # once all the rounds are done close the AI
#     # while True:  # this code will keep running while the game is on
#     #     if close_event.is_set():  # check if the event is set to True if it is then turn off the game
#     #         print("Elements of given array: ")
#     #         for i in range(0, len(player_msg_arr)):
#     #             print(player_msg_arr[i])
#     #         print("Elements of given array: ")
#     #         for i in range(0, len(AI_msg_arr)):
#     #             print(AI_msg_arr[i])
#     #         print("Elements of given array: ")
#     #         for i in range(0, len(player_act_arr)):
#     #             print(player_act_arr[i])
#     #         print("Elements of given array: ")
#     #         for i in range(0, len(AI_act_arr)):
#     #             print(AI_act_arr[i])
#     #         p1.terminate()
#     #         # p2.terminate()
#     #         sys.exit(1)


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
        dir_list = os.listdir("pickledgames/")
        if len(dir_list) != 0:
            for x in dir_list:
                if x == "game":
                    infile = open(f'pickledgames/{x}', 'rb')
                    new_dict = pickle.load(infile)
                    infile.close()
                    processes = []  # an array that has all the AIs that are running
                    rounds = new_dict["maxRound"]  # number of rounds
                    # for i in range(0, 250):
                    #     player_msg_arr.insert(0, "0")
                    #     AI_msg_arr.insert(0, "0")
                    #     player_act_arr.insert(0, "0")
                    #     AI_act_arr.insert(0, "0")
                    p1 = Process(target=run, args=(rounds,  x))  # this starts the AI
                    p1.start()
                    processes.append(p1)  # adds the AI to the list of AIs
                    p1.join()  # waits until all AIs are done then terminate
                    flag = False
                else:
                    time.sleep(1)
