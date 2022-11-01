import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = None


def initiate_db(user, password, host='127.0.0.1', port=3306, dbname='HH'):
    """
    must be run after every time module is imported

    example: hh_db.initiate_db('root','password1')

    user: <str> username for authentication to db
    password: <str> for authentication to db
    host: <str> ip or url where db service is reachable
    port: <int> network port where db service is reachable
    dbname: <str> name of database used in db service
    """
    global Base
    global Session
    # Define the MariaDB engine using MariaDB Connector/Python
    # Don't forget to update user and password here 
    engine = sqlalchemy.create_engine(
            "mysql://{user}:{password}@{host}:{port}/{dbname}".format(
                user=user, password=password, 
                host=host, port=port, dbname=dbname,
                )
            )
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)


def add_db_object(obj):
    """
    add one filled-in db-model object at a time to the database

    example:  hh_db.add_db_object( hh_db.User(*user_args) )
    """
    with Session.begin() as session:
        session.add(obj)
        session.commit()


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

    def __init__(self, FirstName, LastName, Email, PhoneNumber, 
            Password, IsAtRisk, IsVolunteer, IsRepresentative, ):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        self.PhoneNumber = PhoneNumber
        self.Password = Password
        self.IsAtRisk = IsAtRisk
        self.IsVolunteer = IsVolunteer
        self.IsRepresentative = IsRepresentative

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
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.HQAdress = HQAdress
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours
 

    def __repr__(self):
        return "%s %s" %(self.OrganizationID, self.Name) 

class Representative(Base):
    __tablename__ = 'REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)
   
    def __init__(self, UserID, OrganizationID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
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
        ## add all required/cannot-be-empty params

        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.Description = Description

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
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.OrganizationID = OrganizationID
        self.ProgramID = ProgramID
        self.Address = Address
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours
 
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
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.OrganizationID = OrganizationID
        self.ProgramID = ProgramID
        self.LocalityID = LocalityID
        self.AcceptsWho = AcceptsWho
        self.ProvidesTransportation = ProvidesTransportation
        self.LastUpdate = LastUpdate
 
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
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.TimeStamp = TimeStamp
        self.Comment = Comment
        self.UserID = UserID
        self.PageID = PageID
     
    def __repr__(self):
        return "%s" %(self.PostID) 

class Vote(Base):
    __tablename__ = 'VOTE'
    VoteID = Column(Integer, primary_key=True)
    Vote = Column(Boolean, nullable=False)
    PageID = Column(Integer, ForeignKey("PAGE.PageID"), nullable=False)
   
    def __init__(self, VoteID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Vote = Vote
        self.PageID = PageID

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
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.PageID = PageID
        self.AvgTimeSpent = AvgTimeSpent
        self.NumVisits = NumVisits
        self.NumForumPosts = NumForumPosts
        self.NumUpVotes = NumUpVotes
        self.NumDownVotes = NumDownVotes
     
    def __repr__(self):
        return "%s" %(self.MetricID) 



