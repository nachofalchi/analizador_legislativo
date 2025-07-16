from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from .connections import Base

class VotationMetadata(Base):
    __tablename__ = 'votation_metadata'
    
    id = Column(String, primary_key=True, index=True)
    date = Column(Date)
    title = Column(String)
    type = Column(String)
    result = Column(String)
    loaded = Column(Boolean, default=False)
    analyzed = Column(Boolean, default=False)

class DeputiesVoting(Base):
    __tablename__ = 'deputies_votes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vote_id = Column(String, ForeignKey('votation_metadata.id'))
    deputy = Column(String)
    block = Column(String)
    province = Column(String)
    vote = Column(String)