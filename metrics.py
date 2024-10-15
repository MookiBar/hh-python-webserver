import hh_db as hh
from sqlalchemy import update, select

def __getServicesSearched():
    """
    params: pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain how many users clicked on a certain pageID while searching for x services

    example: __getServicesSearched(1)
    """
    ##TODO: implement 
    return 'None'

def __getForumCount(pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumForumPosts for a certain PageID
    
    example: _getForumCount(1)

    return: int numForums
    """
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

def __getUpVotesCount(category, pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: table name->category - Vote category i.e. Safe_Vote/Clean_Vote/Responsive_Vote 
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumUpVotesClean/NumUpVotesSafe/NumUpVotesResponsive for a certain PageID

    example: __getUpVotesCount(hh.Clean_Vote, 1)

    return: int numUpVotes
    """
    with hh.Session.begin() as session:
        numUpVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==True).count()
        return numUpVotes

def __getDownVotesCount(category, pageID):
    """
    TO BE CALLED WITHIN set_Metric()
    params: table name->category - Vote category i.e. Safe_Vote/Clean_Vote/Responsive_Vote 
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumDownVotesClean/NumDownVotesSafe/NumDownVotesResponsive for a certain PageID

    example: __getDownVotesCount(hh.Clean_Vote, pageID)

    return: int numDownVotes
    """
    with hh.Session.begin() as session:
        numDownVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==False).count()
        return numDownVotes

def __updateMetric(pageID, servSearched, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe):
    """
    TO BE CALLED WITHIN set_Metric()
    params: ALL attributes of the Usage_Metrics table except numVisits for each type

    Purpose: Update a metric DB object currently stored in the Usage_Metrics table related to a certain pageID
    """
    with hh.Session.begin() as session:
        stmt = (
            update(hh.Usage_Metrics).
            where(hh.Usage_Metrics.PageID == pageID).
            values(ServicesSearched = servSearched, NumForumPosts = numForums, NumUpVotesClean = upVoteClean, NumDownVotesClean = downVoteClean, NumUpVotesResponsive = upVoteResponsive, NumDownVotesResponsive = downVoteResponsive, NumUpVotesSafe = upVoteSafe, NumDownVotesSafe = downVoteSafe)
        )
        session.execute(stmt)
        session.commit()

def set_Metric(pageID):
    """
    TO BE CALLED WHEN REP USER REQUESTS TO UPDATE RESOURCE PAGE INFO
    params: pageID - PageID for which we are adding/updating metric

    Purpose: Calls all metric functions to SET values to be stored in DB related to a certain pageID. 

    example: metrics.addMetric( 1 )
    """
    servSearched = __getServicesSearched()
    numForums = __getForumCount(pageID)
    upVoteClean = __getUpVotesCount(hh.Clean_Vote, pageID)
    downVoteClean = __getDownVotesCount(hh.Clean_Vote, pageID)
    upVoteResponsive = __getUpVotesCount(hh.Responsive_Vote, pageID)
    downVoteResponsive = __getDownVotesCount(hh.Responsive_Vote, pageID)
    upVoteSafe = __getUpVotesCount(hh.Safe_Vote, pageID)
    downVoteSafe = __getDownVotesCount(hh.Safe_Vote, pageID)

    __updateMetric(pageID, servSearched, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe)

def get_Metrics(pageID):
    """
    """
    with hh.Session.begin() as session:
        session.expire_on_commit = False
        q = session.query(hh.Usage_Metrics).filter_by(PageID=pageID)
        metric = q.first()
    return metric
    
def visitors(userType, pageID):
    """
    TO BE CALLED EVERY TIME A USER ACCESSES A RESOURCE PAGE
    params: string userType - AtRisk/Volunteer/Representative
            int pageID - PageID for which we are obtaining metric

    Purpose: Used to obtain NumVisits for every userType on a certain PageID, then incr the counter for current userType and store new value in USAGE_METRICS

    example: visitors('AtRisk', 1)
    """
    with hh.Session.begin() as session:
            #check the current stored number of visitors on a page
            stmt = select(hh.Usage_Metrics.NumVisitsAtRisk, hh.Usage_Metrics.NumVisitsVolunteer, hh.Usage_Metrics.NumVisitsRepresentative, hh.Usage_Metrics.NumVisitsOther).where(hh.Usage_Metrics.PageID==pageID)
            result = session.execute(stmt)
            value = result.fetchall()
            numVisitsAtRisk = value[0][0]
            numVisitsVolunteer = value[0][1]
            numVisitsRepresentative = value[0][2]
            numVisitsOther = value[0][3]

            #increment the number of visitors depending on the current userType & store new value
            if userType == 'AtRisk':
                incrNumVisits = numVisitsAtRisk + 1
                stmt = (
                    update(hh.Usage_Metrics).
                    where(hh.Usage_Metrics.PageID == pageID).
                    values(NumVisitsAtRisk = incrNumVisits)
                )
            elif userType == 'Volunteer':
                incrNumVisits = numVisitsVolunteer + 1
                stmt = (
                    update(hh.Usage_Metrics).
                    where(hh.Usage_Metrics.PageID == pageID).
                    values(NumVisitsVolunteer = incrNumVisits)
                )
            elif userType == 'Representative':
                incrNumVisits = numVisitsRepresentative + 1
                stmt = (
                    update(hh.Usage_Metrics).
                    where(hh.Usage_Metrics.PageID == pageID).
                    values(NumVisitsRepresentative = incrNumVisits)
                )
            else:
                incrNumVisits = numVisitsOther + 1
                stmt = (
                    update(hh.Usage_Metrics).
                    where(hh.Usage_Metrics.PageID == pageID).
                    values(NumVisitsOther = incrNumVisits)
                )
            
            session.execute(stmt)
            session.commit()
