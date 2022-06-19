from sqlalchemy import false


class userr():
    name=''
    usr_id=0
    sid = ''
    match_id=0
    flag = False
    disconnected = False
    CurrentlyInMatch = False
class game():
    def __init__(self,p1,p2):
        self.id = None
        self.player1=p1
        self.player2=p2
        self.player1choices=''
        self.player2choices=''
        self.player1msgs=''
        self.player2msgs=''
        self.player1sentM=False
        self.player2sentM=False
        self.player1sentA=False
        self.player2sentA=False
        self.round=1
        self.maxRound=None
        self.actions=''
        self.ai = 0
        self.parentCon = None
        self.childCon = None
        self.ai_id = None
        self.aiact = ''
        self.aimes = ''
        self.p1score = 0
        self.p2score = 0
        self.aiHandler = None

class aigame():
    def __init__(self):
        self.id = None
        self.maxRound=0
        self.aiact=''
        self.humanact=''
        self.aimes=''
        self.humanmes=''