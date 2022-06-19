from app.models import User
from app import db
users = User.query.all()
# i=1
# for u in users:
#     if i%2==0:
#         u.group = "pvp"
#     else:
#         u.group = "AI"
#     i+=1

# db.session.commit()
for u in users:
    print(u.group)