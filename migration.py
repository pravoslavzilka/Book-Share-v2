from database import db_session
from models import *

g1 = Grade("Prima")
g2 = Grade("Sekunda")
g3 = Grade("Tercia")
g4 = Grade("Kvarta")
g5 = Grade("Kvinta")
g6 = Grade("Sexta")
g7 = Grade("Septima")
g8 = Grade("Oktava")
g9 = Grade("1.A")
g10 = Grade("1.B")
g11 = Grade("2.A")
g12 = Grade("2.B")
g13 = Grade("3.A")
g14 = Grade("3.B")
g15 = Grade("4.A")
g16 = Grade("4.B")


db_session.add(g1)
db_session.add(g2)
db_session.add(g3)
db_session.add(g4)
db_session.add(g5)
db_session.add(g6)
db_session.add(g7)
db_session.add(g8)
db_session.add(g9)
db_session.add(g10)
db_session.add(g11)
db_session.add(g12)
db_session.add(g13)
db_session.add(g14)
db_session.add(g15)
db_session.add(g16)

db_session.commit()



