#!.venv/bin/python3
from mcstatus import MinecraftServer
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

# declarative base class
Base = declarative_base()

class Operation(Base):
    __tablename__ = 'operation'

    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    players = relationship('Player')

class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    operation_id = Column(Integer, ForeignKey('operation.id'))

engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URL'], echo=True, future=True)

# If you know the host and port, you may skip this and use MinecraftServer("example.org", 1234)
server = MinecraftServer.lookup(os.environ['MINECRAFT_SERVER_HOST'])

# 'status' is supported by all Minecraft servers that are version 1.7 or higher.
status = server.status()
print(status.players.online)

with Session(engine) as session:
  operation = Operation(count=status.players.online)
  if status.players.sample:
    print([sample.name for sample in status.players.sample])
    players = [Player(name=sample.name) for sample in status.players.sample]
    operation.players = players
    session.add_all(players)
  session.add(operation)
  session.commit()