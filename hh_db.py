import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime, Float, Numeric, inspect, or_
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import hashlib
import random

Base = declarative_base()
Session = None

## global for the hash algo and its length
HASH_ALGO = hashlib.sha3_512
HASH_ALGO_LEN_BYTES = HASH_ALGO().digest_size
HASH_ALGO_LEN_HEX = HASH_ALGO_LEN_BYTES * 2
## so we have a static length stated for password salts
SALT_LEN_BYTES = 4
SALT_LEN_HEX = SALT_LEN_BYTES * 2


## This should match (exact spelling and case) the booleans for org/loc/prog serices
Services = ('Food', 'Shelter', 'Medicine', 'Clothing', 'Supplies', 'Addiction', 'Counseling', 'Legal', 'Veteran', 'Family')

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


def get_user(userid):
    """
    """
    with Session.begin() as session:
        session.expire_on_commit = False
        user = session.query(User).filter(User.UserID==userid).first()

    return user




def match_all_localities(services):
    """
    turn a list of services strings into a list of matching localities

    example:  hh_db.match_all_localities( ('Food','Medicine') )

    returns: list of Locality objects

    """
    locsrvcs = [ getattr(Locality, x) for x in services]
    with Session.begin() as session:
        session.expire_on_commit = False
        q = session.query(Locality).filter(or_(*locsrvcs)).all()

    return q

def match_all_organizations(services):
    """
    turn a list of services strings into a list of matching organizations

    example:  hh_db.match_al_organizations( ('Food','Medicine') )

    returns: list of Organization objects


    """
    orgsrvcs = [ getattr(Organization, x) for x in services]
    with Session.begin() as session:
        session.expire_on_commit = False
        q = session.query(Organization).filter(or_(*orgsrvcs)).all()
    return q


def match_all_programs(services):
    """
    turn a list of services strings into a list of matching programs

    example:  hh_db.match_all_program( ('Food','Medicine') )

    returns: list of Program objects

    """
    progsrvcs = [ getattr(Program, x) for x in services]
    with Session.begin() as session:
        session.expire_on_commit = False
        q = session.query(Program).filter(or_(*progsrvcs)).all()
    return q


def hash_password(password, salt):
    """

    returns str (hex of hashed password)
    """
    ## md5(hex)=32 bytes, match length of User.password
    ## TODO: change to better hashing algo if size increases
    if hasattr(salt, 'decode'):
        ## salt-hex must be a string (not bytes) for the next step to work
        salt = salt.decode()
    ## convert to raw binary (type: bytes)
    salt = bytes.fromhex(salt)
    if hasattr(password, 'encode'):
        ## convert password to encoded bytes from str if necessary...
        password = password.encode('utf-8')
    return HASH_ALGO(salt + password).hexdigest()


def gen_passwd_salt():
    """
    returns str (hex of new password salt)
    """
    _hex_digits = '01234567890abcdef'
    _hex = [random.choice(_hex_digits) for x in range(SALT_LEN_HEX)]
    return ''.join(_hex)


def check_username_password(username, password):
    """

    returns int (associated userID) or None on failure
    """
    with Session.begin() as session:
        q = session.query(User).filter_by(Email=username)
        if not q.count():
            ## user does not exist
            return None
        if q.count() > 1:
            ## there should not be multiple email/users! woops!
            raise Exception('username not unique: %s' % username)
        user = q.first()
        ## NOTE: email and password are type str (not bytes) here...
        stored_email = user.Email
        tmp_passwd_str = user.Password
        userid = user.UserID
    salt = tmp_passwd_str[:SALT_LEN_HEX]
    stored_hash = tmp_passwd_str[SALT_LEN_HEX:]
    user_hash = hash_password(password, salt)
    if stored_hash == user_hash:
        ## valid login attempt; return associated userID
        return userid
    else:
        ## passwords dont match
        return None



# Declarative mapping configurations
class User(Base):
    """
    initiate a User

    *optional attributes: PhoneNumber

    example w/ PhoneNumber:     hh_db.add_db_object( hh_db.User("Liz", "Taylor", "ltaylor@me.com", "757-555-1234", "apple1", 1, 0, 0) )
    example w/o PhoneNumber:    hh_db.add_db_object( hh_db.User("Liz", "Taylor", "ltaylor@me.com", None, "apple1", 1, 0, 0) )
    """
    __tablename__ = 'USER'
    UserID = Column(Integer, primary_key=True)
    FirstName = Column(String(length=30), nullable=False)
    LastName = Column(String(length=30), nullable=False)
    Email = Column(String(length=50), nullable=False)
    PhoneNumber = Column(String(length=12))
    Password = Column(
            String(length=HASH_ALGO_LEN_HEX + SALT_LEN_HEX), nullable=False
            )
    IsAtRisk = Column(Boolean, default=False, nullable=False)
    IsVolunteer = Column(Boolean, default=False, nullable=False)
    IsRepresentative = Column(Boolean, default=False, nullable=False)

    def __init__(self, FirstName, LastName, Email, PhoneNumber,
            Password, IsAtRisk, IsVolunteer, IsRepresentative):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        self.PhoneNumber = PhoneNumber
        _tmp_salt = gen_passwd_salt()
        self.Password = _tmp_salt + hash_password(Password, _tmp_salt)
        self.IsAtRisk = IsAtRisk
        self.IsVolunteer = IsVolunteer
        self.IsRepresentative = IsRepresentative

    def __repr__(self):
        return "%s %s" %(self.FirstName, self.LastName)

class Resource_Page(Base):
    """
    initiate a Resouce_Page

    *all attributes required
    **requires import

    example:    import datetime
                hh_db.add_db_object( hh_db.Resource_Page(datetime.datetime.now()) )
    """
    __tablename__ = 'RESOURCE_PAGE'
    PageID = Column(Integer, primary_key=True)
    LastUpdate = Column(DateTime)

    def __init__(self, LastUpdate):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.LastUpdate = LastUpdate

    def __repr__(self):
        return "%s" %(self.PageID)

class Organization(Base):
    """
    initiate an Organization

    *optional attributes: HQAddress, PhoneNumber, Hours, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, PageID

    example: hh_db.add_db_object( hh_db.Organization("Fake Org Name", "555 Main St. Norfolk, VA. 12345", "7575552224", "12-4 everyday", 1, "Apply online", "Come to location", 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1) )
    """
    __tablename__ = 'ORGANIZATION'
    OrganizationID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    HQAddress = Column(String(length=100))
    PhoneNumber = Column(String(length=20))
    Hours = Column(String(length=200))
    WebsiteLink = Column(String(length=100))
    ImageURL = Column(String(length=500))
    AcceptingVolunteers = Column(Boolean)
    VolunteerNotice = Column(String(length=1000))
    HelpSeekerNotice = Column(String(length=1000))
    Food = Column(Boolean, default=False, nullable=False)
    Shelter = Column(Boolean, default=False, nullable=False)
    Medicine = Column(Boolean, default=False, nullable=False)
    Clothing = Column(Boolean, default=False, nullable=False)
    Supplies = Column(Boolean, default=False, nullable=False)
    Addiction = Column(Boolean, default=False, nullable=False)
    Counseling = Column(Boolean, default=False, nullable=False)
    Legal = Column(Boolean, default=False, nullable=False)
    Veteran = Column(Boolean, default=False, nullable=False)
    Family = Column(Boolean, default=False, nullable=False)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=True)

    def __init__(self, Name, HQAddress, PhoneNumber, Hours, WebsiteLink, ImageURL, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, Food, Shelter, Medicine, Clothing, Supplies, Addiction, Counseling, Legal, Veteran, Family, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.HQAddress = HQAddress
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours
        self.WebsiteLink = WebsiteLink
        self.ImageURL = ImageURL
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.Food = Food
        self.Shelter = Shelter
        self.Medicine = Medicine
        self.Clothing = Clothing
        self.Supplies = Supplies
        self.Addiction = Addiction
        self.Counseling = Counseling
        self.Legal = Legal
        self.Veteran = Veteran
        self.Family = Family
        self.PageID = PageID


    def __repr__(self):
        return "%s %s" %(self.OrganizationID, self.Name)

class Program(Base):
    """
    initiate a Program

    *optional attributes: Description, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, PageID

    example: hh_db.add_db_object( hh_db.Program("Fake Prog Name", "lorem", 1, "apply online", "Come to location", 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1) )
    """
    __tablename__ = 'PROGRAM'
    ProgramID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    Description = Column(String(length=200))
    WebsiteLink = Column(String(length=100))
    ImageURL = Column(String(length=500))
    AcceptingVolunteers = Column(Boolean)
    VolunteerNotice = Column(String(length=1000))
    HelpSeekerNotice = Column(String(length=1000))
    Food = Column(Boolean, default=False, nullable=False)
    Shelter = Column(Boolean, default=False, nullable=False)
    Medicine = Column(Boolean, default=False, nullable=False)
    Clothing = Column(Boolean, default=False, nullable=False)
    Supplies = Column(Boolean, default=False, nullable=False)
    Addiction = Column(Boolean, default=False, nullable=False)
    Counseling = Column(Boolean, default=False, nullable=False)
    Legal = Column(Boolean, default=False, nullable=False)
    Veteran = Column(Boolean, default=False, nullable=False)
    Family = Column(Boolean, default=False, nullable=False)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=True)

    def __init__(self, Name, Description, WebsiteLink, ImageURL, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, Food, Shelter, Medicine, Clothing, Supplies, Addiction, Counseling, Legal, Veteran, Family, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.Description = Description
        self.WebsiteLink = WebsiteLink
        self.ImageURL = ImageURL
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.Food = Food
        self.Shelter = Shelter
        self.Medicine = Medicine
        self.Clothing = Clothing
        self.Supplies = Supplies
        self.Addiction = Addiction
        self.Counseling = Counseling
        self.Legal = Legal
        self.Veteran = Veteran
        self.Family = Family
        self.PageID = PageID

    def __repr__(self):
        return "%s %s" %(self.ProgramID, self.Name)

class Locality(Base):
    """
    initiate a Locality

    *optional attributes: OrganizationID, ProgramID, Latitude, Longitude, Hours, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, ProvidesTransportation, PageID

    example: hh_db.add_db_object( hh_db.Locality("Fake Loc Name", 1, 1, "123 Main St. Norfolk, VA. 12345", "36.89108816136752", "-76.30357733755238", "7575551111", "12-4 everyday", 1, "Apply online", "Come to location", 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) )
    """
    __tablename__ = 'LOCALITY'
    LocalityID = Column(Integer, primary_key=True)
    Name = Column(String(length=50), nullable=False)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"))
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"))
    Address = Column(String(length=100), nullable=False)
    Latitude = Column(Numeric(16, 14))
    Longitude = Column(Numeric(16, 14))
    PhoneNumber = Column(String(length=12), nullable=False)
    Hours = Column(String(length=200))
    WebsiteLink = Column(String(length=100))
    ImageURL = Column(String(length=500))
    AcceptingVolunteers = Column(Boolean)
    VolunteerNotice = Column(String(length=1000))
    HelpSeekerNotice = Column(String(length=1000))
    ProvidesTransportation = Column(Boolean)
    Food = Column(Boolean, default=False, nullable=False)
    Shelter = Column(Boolean, default=False, nullable=False)
    Medicine = Column(Boolean, default=False, nullable=False)
    Clothing = Column(Boolean, default=False, nullable=False)
    Supplies = Column(Boolean, default=False, nullable=False)
    Addiction = Column(Boolean, default=False, nullable=False)
    Counseling = Column(Boolean, default=False, nullable=False)
    Legal = Column(Boolean, default=False, nullable=False)
    Veteran = Column(Boolean, default=False, nullable=False)
    Family = Column(Boolean, default=False, nullable=False)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=True)

    def __init__(self, Name, OrganizationID, ProgramID, Address, Latitude, Longitude, PhoneNumber, Hours, WebsiteLink, ImageURL, AcceptingVolunteers, VolunteerNotice, HelpSeekerNotice, ProvidesTransportation, Food, Shelter, Medicine, Clothing, Supplies, Addiction, Counseling, Legal, Veteran, Family, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.Name = Name
        self.OrganizationID = OrganizationID
        self.ProgramID = ProgramID
        self.Address = Address
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.PhoneNumber = PhoneNumber
        self.Hours = Hours        
        self.WebsiteLink = WebsiteLink
        self.ImageURL = ImageURL
        self.AcceptingVolunteers = AcceptingVolunteers
        self.VolunteerNotice = VolunteerNotice
        self.HelpSeekerNotice = HelpSeekerNotice
        self.ProvidesTransportation = ProvidesTransportation
        self.Food = Food
        self.Shelter = Shelter
        self.Medicine = Medicine
        self.Clothing = Clothing
        self.Supplies = Supplies
        self.Addiction = Addiction
        self.Counseling = Counseling
        self.Legal = Legal
        self.Veteran = Veteran
        self.Family = Family
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.LocalityID)

class Org_Representative(Base):
    """
    initiate an Org_Representative

    *all attributes required
    **caveat:   VerificationStatus can NOT and will NOT be set to True upon initialization of Representative user.
                Verification needs to take place after Representative user initialization takes place and before VerificationStatus is updated to True.
                Therefore it defaults to False and is EXCLUDED from add_db_object command

    example: hh_db.add_db_object( hh_db.Org_Representative(1, 1) )
    """
    __tablename__ = 'ORG_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    OrganizationID = Column(Integer, ForeignKey("ORGANIZATION.OrganizationID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)

    def __init__(self, UserID, OrganizationID):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.OrganizationID = OrganizationID

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.OrganizationID, self.VerificationStatus)

class Loc_Representative(Base):
    """
    initiate a Loc_Representative

    *all attributes required
    **caveat:   VerificationStatus can NOT and will NOT be set to True upon initialization of Representative user.
                Verification needs to take place after Representative user initialization takes place and before VerificationStatus is updated to True.
                Therefore it defaults to False and is EXCLUDED from add_db_object command

    example: hh_db.add_db_object( hh_db.Loc_Representative(1, 1) )
    """
    __tablename__ = 'LOC_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    LocalityID = Column(Integer, ForeignKey("LOCALITY.LocalityID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)

    def __init__(self, UserID, LocalityID):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.LocalityID = LocalityID

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.LocalityID, self.VerificationStatus)

class Prog_Representative(Base):
    """
    initiate a Prog_Representative

    *all attributes required
    **caveat:   VerificationStatus can NOT and will NOT be set to True upon initialization of Representative user.
                Verification needs to take place after Representative user initialization takes place and before VerificationStatus is updated to True.
                Therefore it defaults to False and is EXCLUDED from add_db_object command

    example: hh_db.add_db_object( hh_db.Prog_Representative(1, 1) )
    """
    __tablename__ = 'PROG_REPRESENTATIVE'
    UserID = Column(Integer, ForeignKey("USER.UserID"), primary_key=True)
    ProgramID = Column(Integer, ForeignKey("PROGRAM.ProgramID"), primary_key=True)
    VerificationStatus = Column(Boolean, default=False, nullable=False)

    def __init__(self, UserID, ProgramID):
        ## add all required/cannot-be-empty params
        self.UserID = UserID
        self.ProgramID = ProgramID

    def __repr__(self):
        return "%s %s %s" %(self.UserID, self.ProgramID, self.VerificationStatus)

class Forum(Base):
    """
    initiate a Forum post

    *all attributes required
    **requires import

    example:    import datetime
                hh_db.add_db_object( hh_db.Forum(datetime.datetime.now(), "Great staff!", 1, 1) )
    """
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
    """
    initiate a Clean_Vote

    *all attributes required
    **Key for Vote attribute: True = Up-Vote  False = Down-Vote

    example: hh_db.add_db_object( hh_db.Clean_Vote(1, 1, 1) )
    """
    __tablename__ = 'CLEAN_VOTE'
    VoteID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey("USER.UserID"), nullable=False)
    Vote = Column(Boolean, nullable=False)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)

    def __init__(self, UserID, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.UserID = UserID
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID)

class Responsive_Vote(Base):
    """
    initiate a Responsive_Vote

    *all attributes required
    **Key for Vote attribute: True = Up-Vote  False = Down-Vote

    example: hh_db.add_db_object( hh_db.Responsive_Vote(1, 1, 1) )
    """
    __tablename__ = 'RESPONSIVE_VOTE'
    VoteID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey("USER.UserID"), nullable=False)
    Vote = Column(Boolean, nullable=False) # up=true, down=false
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)

    def __init__(self, UserID, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.UserID = UserID
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID)

class Safe_Vote(Base):
    """
    initiate a Safe_Vote

    *all attributes required
    **Key for Vote attribute: True = Up-Vote  False = Down-Vote

    example: hh_db.add_db_object( hh_db.Safe_Vote(1, 1, 1) )
    """
    __tablename__ = 'SAFE_VOTE'
    VoteID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey("USER.UserID"), nullable=False)
    Vote = Column(Boolean, nullable=False) # up=true, down=false
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)

    def __init__(self, UserID, Vote, PageID):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.UserID = UserID
        self.Vote = Vote
        self.PageID = PageID

    def __repr__(self):
        return "%s" %(self.VoteID)

class Usage_Metrics(Base):
    """
    initiate a Usage_Metric

    *all attributes required

    example: hh_db.add_db_object( hh_db.Usage_Metrics(1, FoodShelterMedicine, 10, 10, 10, 10, 2, 5, 3, 4, 5, 3, 1) )
    """
    __tablename__ = 'USAGE_METRICS'
    MetricID = Column(Integer, primary_key=True)
    PageID = Column(Integer, ForeignKey("RESOURCE_PAGE.PageID"), nullable=False)
    ServicesSearched = Column(String(length=150), nullable=False)
    NumVisitsAtRisk = Column(Integer, nullable=False)
    NumVisitsVolunteer = Column(Integer, nullable=False)
    NumVisitsRepresentative = Column(Integer, nullable=False)
    NumVisitsOther = Column(Integer, nullable=False)
    NumForumPosts = Column(Integer, nullable=False)
    NumUpVotesClean = Column(Integer, nullable=False)
    NumDownVotesClean = Column(Integer, nullable=False)
    NumUpVotesResponsive = Column(Integer, nullable=False)
    NumDownVotesResponsive = Column(Integer, nullable=False)
    NumUpVotesSafe = Column(Integer, nullable=False)
    NumDownVotesSafe = Column(Integer, nullable=False)

    def __init__(self, PageID, ServicesSearched, NumVisitsAtRisk, NumVisitsVolunteer, NumVisitsRepresentative, NumVisitsOther, NumForumPosts, NumUpVotesClean, NumDownVotesClean, NumUpVotesResponsive, NumDownVotesResponsive, NumUpVotesSafe, NumDownVotesSafe):
        ## add all required/cannot-be-empty params
        ## primary_key *should* auto-increment on create by default
        self.PageID = PageID
        self.ServicesSearched = ServicesSearched
        self.NumVisitsAtRisk = NumVisitsAtRisk
        self.NumVisitsVolunteer = NumVisitsVolunteer
        self.NumVisitsRepresentative = NumVisitsRepresentative
        self.NumVisitsOther = NumVisitsOther
        self.NumForumPosts = NumForumPosts
        self.NumUpVotesClean = NumUpVotesClean
        self.NumDownVotesClean = NumDownVotesClean
        self.NumUpVotesResponsive = NumUpVotesResponsive
        self.NumDownVotesResponsive = NumDownVotesResponsive
        self.NumUpVotesSafe = NumUpVotesSafe
        self.NumDownVotesSafe = NumDownVotesSafe

    def __repr__(self):
        return "%s" %(self.MetricID)

