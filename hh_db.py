import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy_utils import database_exists, create_database

# Define the MariaDB engine using MariaDB Connector/Python
# Don't forget to update user and password here 
engine = sqlalchemy.create_engine("mysql://user:password@127.0.0.1:3306/HH")
if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()

# Declarative mapping configurations
class User(Base):
    __tablename__ = 'USER'
    UserID = Column(Integer, primary_key=True)
    FirstName = Column(String(length=30), nullable=False)
    LastName = Column(String(length=30), nullable=False)
    Email = Column(String(length=50), nullable=False)
    PhoneNumber = Column(String(length=12))
    Password = Column(String(length=32), nullable=False)
    IsAtRisk = Column(Boolean, default=False, nullable=False)
    IsVolunteer = Column(Boolean, default=False, nullable=False)
    IsRepresentative = Column(Boolean, default=False, nullable=False)

    def __init__(self, FirstName, LastName):
        self.FirstName = FirstName
        self.LastName = LastName

    def __repr__(self):
        return "%s %s" %(self.FirstName, self.LastName) 

class Organization(Base):
    __tablename__ = 'ORGANIZATION'
    OrganizationID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    HQAdress = Column(String(length=100))
    PhoneNumber = Column(String(length=12))
    Hours = Column(String(length=200))
   
    def __init__(self, OrganizationID, Name):
        self.OrganizationID = OrganizationID
        self.Name = Name

    def __repr__(self):
        return "%s %s" %(self.OrganizationID, self.Name) 

class Representative(Base):
    __tablename__ = 'REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)
   
    def __init__(self, UserID, OrganizationID):
        self.UserID = UserID
        self.OrganizationID = OrganizationID

    def __repr__(self):
        return "%s %s" %(self.UserID, self.OrganizationID) 

class Program(Base):
    __tablename__ = 'PROGRAM'
    ProgramID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    Description = Column(String(length=200))
   
    def __init__(self, ProgramID, Name):
        self.ProgramID = ProgramID
        self.Name = Name

    def __repr__(self):
        return "%s %s" %(self.ProgramID, self.Name) 

class Locality(Base):
    __tablename__ = 'LOCALITY'
    LocalityID = Column(Integer, primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"))
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"))
    Address = Column(String(length=100), nullable=False)
    PhoneNumber = Column(String(length=12), nullable=False)
    Hours = Column(String(length=200))
   
    def __init__(self, LocalityID):
        self.LocalityID = LocalityID

    def __repr__(self):
        return "%s" %(self.LocalityID) 

class Page(Base):
    __tablename__ = 'PAGE'
    PageID = Column(Integer, primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"))
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"))
    LocalityID = Column(Integer, ForeignKey("LOCALITY.LocalityID")) 
    AcceptsWho = Column(String(length=100))
    ProvidesTransportation = Column(Boolean)
    LastUpdate = Column(DateTime)
   
    def __init__(self, PageID):
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.PageID) 

class Forum(Base):
    __tablename__ = 'FORUM'
    PostID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)
    Comment = Column(String(length=200), nullable=False)
    UserID = Column(Integer, ForeignKey("USER.UserID"), nullable=False)
    PageID = Column(Integer, ForeignKey("PAGE.PageID"), nullable=False)
   
    def __init__(self, PostID):
        self.PostID = PostID

    def __repr__(self):
        return "%s" %(self.PostID) 

class Vote(Base):
    __tablename__ = 'VOTE'
    VoteID = Column(Integer, primary_key=True)
    Vote = Column(Boolean, nullable=False)
    PageID = Column(Integer, ForeignKey("PAGE.PageID"), nullable=False)
   
    def __init__(self, VoteID):
        self.VoteID = VoteID

    def __repr__(self):
        return "%s" %(self.VoteID) 

class Usage_Metrics(Base):
    __tablename__ = 'USAGE_METRICS'
    MetricID = Column(Integer, primary_key=True)
    PageID = Column(Integer, ForeignKey("PAGE.PageID"), nullable=False) 
    AvgTimeSpent = Column(Float(precision=10), nullable=False)
    NumVisits = Column(Integer, nullable=False)
    NumForumPosts = Column(Integer, nullable=False)
    NumUpVotes = Column(Integer, nullable=False)
    NumDownVotes = Column(Integer, nullable=False)
   
    def __init__(self, MetricID):
        self.MetricID = MetricID

    def __repr__(self):
        return "%s" %(self.MetricID) 

Base.metadata.create_all(engine)

