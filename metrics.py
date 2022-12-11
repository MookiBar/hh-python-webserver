import hh_db as hh
from sqlalchemy import update

def __countForum(pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumForumPosts for a certain PageID
    
    example: _countForum(1)

    return: int numForums
    """
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

def __countUpVotes(category, pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: table name->category - Vote category i.e. Safe_Vote/Clean_Vote/Responsive_Vote 
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumUpVotesClean/NumUpVotesSafe/NumUpVotesResponsive for a certain PageID

    example: __countUpVotes(hh.Clean_Vote, 1)

    return: int numUpVotes
    """
    with hh.Session.begin() as session:
        numUpVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==True).count()
        return numUpVotes

def __countDownVotes(category, pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: table name->category - Vote category i.e. Safe_Vote/Clean_Vote/Responsive_Vote 
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumDownVotesClean/NumDownVotesSafe/NumDownVotesResponsive for a certain PageID

    example: __countDownVotes(hh.Clean_Vote, pageID)

    return: int numDownVotes
    """
    with hh.Session.begin() as session:
        numDownVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==False).count()
        return numDownVotes

def __countVisits():
    """
    TO BE CALLED WITHIN set_Metric()
    params: string userType - AtRisk/Volunteer/Representative
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumVisits for a specific userType on a certain PageID

    example: __countVisits(AtRisk, 1)

    return: int numVisits
    """
    ##TODO: implement to count number of times page is accessed by a specific userType
    return 0

def __servicesSearched():
    """
    TO BE CALLED WITHIN set_Metric()
    params: pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain the services the user was searching when they acceessed a certain PageID

    example: __servicesSearched(1)

    return: array containing all services user searched
    """
    ##TODO: implement to calculate avgTimeSpent on page for total page visit
    return 0

def __updateMetric(pageID, servSearched, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe):
    """
    TO BE CALLED WITHIN set_Metric()
    params: ALL attributes of the Usage_Metrics table

    Purpose: Update a metric DB object currently stored in the Usage_Metrics table related to a certain pageID
    """
    with hh.Session.begin() as session:
        stmt = (
            update(hh.Usage_Metrics).
            where(hh.Usage_Metrics.PageID == pageID).
            values(ServicesSearched = servSearched, NumVisitsAtRisk = visitsAtRisk, NumVisitsVolunteer = visitsVolunteer, NumVisitsRepresentative = visitsRep, NumVisitsOther = visitsOther, NumForumPosts = numForums, NumUpVotesClean = upVoteClean, NumDownVotesClean = downVoteClean, NumUpVotesResponsive = upVoteResponsive, NumDownVotesResponsive = downVoteResponsive, NumUpVotesSafe = upVoteSafe, NumDownVotesSafe = downVoteSafe)
        )
        session.execute(stmt)
        session.commit()

def set_Metric(pageID):
    """
    params: pageID - PageID for which we are adding/updating metric

    Purpose: Calls all metric functions to SET values to be stored in DB related to a certain pageID. 
    Querys the Usage_Metrics table to see if a certain pageID already has a stored Metric: 
    -if yes, update the Usage Metrics for a certain page. 
    -if no, add the Usage Metrics for a certain pageID.

    example: metrics.addMetric( 1 )
    """
    with hh.Session.begin() as session:
        servSearched = __servicesSearched()
        visitsAtRisk = __countVisits()
        visitsVolunteer = __countVisits()
        visitsRep = __countVisits()
        visitsOther = __countVisits()
        numForums = __countForum(pageID)
        upVoteClean = __countUpVotes(hh.Clean_Vote, pageID)
        downVoteClean = __countDownVotes(hh.Clean_Vote, pageID)
        upVoteResponsive = __countUpVotes(hh.Responsive_Vote, pageID)
        downVoteResponsive = __countDownVotes(hh.Responsive_Vote, pageID)
        upVoteSafe = __countUpVotes(hh.Safe_Vote, pageID)
        downVoteSafe = __countDownVotes(hh.Safe_Vote, pageID)

        metric = session.query(hh.Usage_Metrics).filter(hh.Usage_Metrics.PageID == pageID).count()

        if metric == 0:
            hh.add_db_object( hh.Usage_Metrics(pageID, servSearched, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe) )
        else:
            __updateMetric(pageID, servSearched, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe)