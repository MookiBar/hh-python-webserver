import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime, Float, Numeric, inspect
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

    returns: primary key of committed object (None if fail)
    """
    with Session.begin() as session:
        session.add(obj)
        session.commit()
    pkey_str = inspect(type(obj)).primary_key[0].name
    with Session.begin() as session:
        session.add(obj)
        pkey_val = getattr(obj, pkey_str)
    return pkey_val



def hash_password(password):
    ## md5(hex)=32 bytes, match length of User.password
    ## TODO: change to better hashing algo if size increases
    return hashlib.md5(password).hexdigest()


def check_username_password(username, password):
    tmphash = hash_password(password)
    with Session.begin() as session:
        q = session.query(User).filter_by(Email=username)
        if q.count():
            if q.count() > 1:
                ## there should not be multiple! woops!
                raise Exception('username not unique: %s' % username)
            user = q.first()
            if user.Email == username and user.Password == tmphash:
                return user.UserID
    ## made it this far? your login failed
    return None



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

class Resource_Page(Base):
    __tablename__ = 'RESOURCE_PAGE'
    PageID = Column(Integer, primary_key=True)
    # AcceptsWho = Column(String(length=300))
    LastUpdate = Column(DateTime)
   
    def __init__(self, LastUpdate):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.LastUpdate = LastUpdate
 
    def __repr__(self):
        return "%s" %(self.PageID) 

class Organization(Base):
    __tablename__ = 'ORGANIZATION'
    OrganizationID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    HQAddress = Column(String(length=100))
    PhoneNumber = Column(String(length=12))
    Hours = Column(String(length=200))
    AcceptingVolunteers = Column(Boolean) 
    VolunteerNotice = Column(String(length=1000)) 
    HelpSeekerNotice = Column(String(length=1000)) 
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False) 
   
    def __init__(self, Name, HQAddress, PhoneNumber, Hours, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.HQAddress = HQAddress
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.PageID = PageID
 

    def __repr__(self):
        return "%s %s" %(self.OrganizationID, self.Name) 

class Program(Base):
    __tablename__ = 'PROGRAM'
    ProgramID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    Description = Column(String(length=200))
    AcceptingVolunteers = Column(Boolean) 
    VolunteerNotice = Column(String(length=1000)) 
    HelpSeekerNotice = Column(String(length=1000)) 
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False) 
   
    def __init__(self, Name, Description, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.Description = Description
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.PageID = PageID

    def __repr__(self):
        return "%s %s" %(self.ProgramID, self.Name) 

class Locality(Base):
    __tablename__ = 'LOCALITY'
    LocalityID = Column(Integer, primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"))
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"))
    Address = Column(String(length=100), nullable=False)
    Latitude = Column(Numeric(16, 14)) 
    Longitude = Column(Numeric(16, 14)) 
    PhoneNumber = Column(String(length=12), nullable=False)
    Hours = Column(String(length=200))
    AcceptingVolunteers = Column(Boolean) 
    VolunteerNotice = Column(String(length=1000)) 
    HelpSeekerNotice = Column(String(length=1000)) 
    ProvidesTransportation = Column(Boolean) 
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False) 
   
    def __init__(self, OrganizationID, ProgramID, Address, Latitude, Longitude, PhoneNumber, Hours, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, ProvidesTransportation, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.OrganizationID = OrganizationID
        self.ProgramID = ProgramID
        self.Address = Address
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.ProvidesTransportation = ProvidesTransportation
        self.PageID = PageID
 
    def __repr__(self):
        return "%s" %(self.LocalityID) 

class Org_Representative(Base):
    __tablename__ = 'ORG_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)
   
    def __init__(self, UserID, OrganizationID, VerificationStatus):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.OrganizationID = OrganizationID
        self.VerificationStatus = VerificationStatus

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.OrganizationID, self.VerificationStatus) 

class Loc_Representative(Base):
    __tablename__ = 'LOC_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    LocalityID = Column(Integer, ForeignKey("LOCALITY.LocalityID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)
   
    def __init__(self, UserID, LocalityID, VerificationStatus):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.LocalityID = LocalityID
        self.VerificationStatus = VerificationStatus

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.LocalityID, self.VerificationStatus) 

class Prog_Representative(Base):
    __tablename__ = 'PROG_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)
   
    def __init__(self, UserID, ProgramID, VerificationStatus):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.ProgramID = ProgramID
        self.VerificationStatus = VerificationStatus

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.ProgramID, self.VerificationStatus)

class Forum(Base):
    __tablename__ = 'FORUM'
    PostID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)
    Comment = Column(String(length=200), nullable=False)
    UserID = Column(Integer, ForeignKey("USER.UserID"), nullable=False)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)
   
    def __init__(self, TimeStamp, Comment, UserID, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.TimeStamp = TimeStamp
        self.Comment = Comment
        self.UserID = UserID
        self.PageID = PageID
     
    def __repr__(self):
        return "%s" %(self.PostID) 

class Clean_Vote(Base):
    __tablename__ = 'CLEAN_VOTE'
    VoteID = Column(Integer, primary_key=True)
    Vote = Column(Boolean, nullable=False) # up=true, down=false
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)
   
    def __init__(self, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID) 

class Responsive_Vote(Base):
    __tablename__ = 'RESPONSIVE_VOTE'
    VoteID = Column(Integer, primary_key=True)
    Vote = Column(Boolean, nullable=False) # up=true, down=false
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)
   
    def __init__(self, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID) 

class Safe_Vote(Base):
    __tablename__ = 'SAFE_VOTE'
    VoteID = Column(Integer, primary_key=True)
    Vote = Column(Boolean, nullable=False) # up=true, down=false
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)
   
    def __init__(self, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID) 

class Usage_Metrics(Base):
    __tablename__ = 'USAGE_METRICS'
    MetricID = Column(Integer, primary_key=True)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False) 
    AvgTimeSpent = Column(Float(precision=10), nullable=False)
    NumVisits = Column(Integer, nullable=False)
    NumForumPosts = Column(Integer, nullable=False)
    NumUpVotes = Column(Integer, nullable=False)
    NumDownVotes = Column(Integer, nullable=False)
   
    def __init__(self, PageID, AvgTimeSpent, NumVisits, NumForumPosts, NumUpVotes, NumDownVotes):
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

class Service(Base):
    __tablename__ = 'SERVICE'
    ServiceID = Column(Integer, primary_key=True)
    Type = Column(String(length=20), nullable=False)

    def __init__(self, Type):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Type = Type

    def __repr__(self):
        return "%s %s" %(self.ServiceID, self.Type) 

class Org_Service_Link(Base):
    __tablename__ = 'ORG_SERVICE_LINK'
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"), primary_key=True)
    ServiceID = Column(Integer, ForeignKey("SERVICE.ServiceID"), primary_key=True)

    def __init__(self, OrganizationID, ServiceID):
        self.OrganizationID = OrganizationID
        self.ServiceID = ServiceID
    
    def __repr__(self):
        return "%s %s" %(self.OrganizationID, self.ServiceID) 

class Loc_Service_Link(Base):
    __tablename__ = 'LOC_SERVICE_LINK'
    LocalityID = Column(Integer, ForeignKey("LOCALITY.LocalityID"), primary_key=True)
    ServiceID = Column(Integer, ForeignKey("SERVICE.ServiceID"), primary_key=True)

    def __init__(self, LocalityID, ServiceID):
        self.LocalityID = LocalityID
        self.ServiceID = ServiceID
    
    def __repr__(self):
        return "%s %s" %(self.LocalityID, self.ServiceID) 

class Prog_Service_Link(Base):
    __tablename__ = 'PROG_SERVICE_LINK'
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"), primary_key=True)
    ServiceID = Column(Integer, ForeignKey("SERVICE.ServiceID"), primary_key=True)

    def __init__(self, ProgramID, ServiceID):
        self.ProgramID = ProgramID
        self.ServiceID = ServiceID
    
    def __repr__(self):
        return "%s %s" %(self.ProgramID, self.ServiceID) 
