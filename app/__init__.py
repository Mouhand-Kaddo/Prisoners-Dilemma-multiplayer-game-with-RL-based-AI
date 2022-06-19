from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging, threading
from logging.handlers import SMTPHandler
from flask_bootstrap import Bootstrap
# from flask_sock import Sock
from flask_socketio import SocketIO, send, emit
# from multiprocessing import Manager


MMLock = threading.Lock() #Prevents simultanious access to the LookingForGame shared resource
LookingForGame = []
Games = []
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
socketio = SocketIO(app)

####Very important bool
importantbool = False
# ######## AI code
AI_id = 0
# player_msg_arr = Manager().list()  # a list that has the player msg for each AI so AI 0 will be looking at slot 0
# # of the list to see its msg this applies to the rest of the lists
# AI_msg_arr = Manager().list()  # a list that has the AI msg
# player_act_arr = Manager().list()  # a list that has the player action
# AI_act_arr = Manager().list()  # a list that has the AI action
processes = []  # an array that has all the AIs that are running

# # Populating mohanad's amazing array, for real it's genius, seriously, couldn't think of something better myself, google hire him
# for i in range(0, 250):
#     player_msg_arr.insert(0, "0")
#     AI_msg_arr.insert(0, "0")
#     player_act_arr.insert(0, "0")
#     AI_act_arr.insert(0, "0")
# ######## end AI code

#sock = Sock(app)
# if not app.debug:
#     if app.config['MAIL_SERVER']:
#         auth = None
#         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
#             auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#         secure = None
#         if app.config['MAIL_USE_TLS']:
#             secure = ()
#         mail_handler = SMTPHandler(
#             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
#             fromaddr='no-reply@' + app.config['MAIL_SERVER'],
#             toaddrs=app.config['ADMINS'], subject='Microblog Failure',
#             credentials=auth, secure=secure)
#         mail_handler.setLevel(logging.ERROR)
#         app.logger.addHandler(mail_handler)

from app import routes, models, errors