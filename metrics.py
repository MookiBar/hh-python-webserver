import hh_db as hh
from sqlalchemy import update

def countForum(pageID):
    """
    params: pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain NumForumPosts for a certain PageID

    return: int numForums
    """
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

def countUpVotes(category, pageID):
    """
    params: category - Vote category i.e. safe/clean/responsive 
            pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain NumUpVotesClean/NumUpVotesSafe/NumUpVotesResponsive for a certain PageID

    return: int numUpVotes
    """
    with hh.Session.begin() as session:
        numUpVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==True).count()
        return numUpVotes

def countDownVotes(category, pageID):
    """
    params: category - Vote category i.e. safe/clean/responsive 
            pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain NumDownVotesClean/NumDownVotesSafe/NumDownVotesResponsive for a certain PageID

    return: int numDownVotes
    """
    with hh.Session.begin() as session:
        numDownVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==False).count()
        return numDownVotes

def countVisits():
    """
    params: userType - AtRisk/Volunteer/Representative
            pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain NumVisits for a specific userType on a certain PageID

    return: int numVisits
    """
    ##TODO: implement to count number of times page is accessed by a specific userType
    return 0

def avgTimeSpent():
    """
    params: pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain AvgTimeSpent on a certain PageID by all users who visited the page

    return: double timeSpent
    """
    ##TODO: implement to calculate avgTimeSpent on page for total page visit
    return 0

def updateMetric(pageID, avgTime, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe):
    """
    params: pageID - PageID for which we are obtaining metric

    Metrics Collection: Used to obtain AvgTimeSpent on a certain PageID by all users who visited the page

    return: double timeSpent
    """
    with hh.Session.begin() as session:
        stmt = (
            update(hh.Usage_Metrics).
            where(hh.Usage_Metrics.PageID == pageID).
            values(AvgTimeSpent = avgTime, NumVisitsAtRisk = visitsAtRisk, NumVisitsVolunteer = visitsVolunteer, NumVisitsRepresentative = visitsRep, NumVisitsOther = visitsOther, NumForumPosts = numForums, NumUpVotesClean = upVoteClean, NumDownVotesClean = downVoteClean, NumUpVotesResponsive = upVoteResponsive, NumDownVotesResponsive = downVoteResponsive, NumUpVotesSafe = upVoteSafe, NumDownVotesSafe = downVoteSafe)
        )
        session.execute(stmt)
        session.commit()

def addMetric(pageID):
    """
    params: pageID - PageID for which we are adding/updating metric

    Metrics Collection: Adds/Updates the Usage Metrics for a certain page

    example: metrics.addMetric( 1 )
    """
    with hh.Session.begin() as session:
        avgTime = avgTimeSpent()
        visitsAtRisk = countVisits()
        visitsVolunteer = countVisits()
        visitsRep = countVisits()
        visitsOther = countVisits()
        numForums = countForum(pageID)
        upVoteClean = countUpVotes(hh.Clean_Vote, pageID)
        downVoteClean = countDownVotes(hh.Clean_Vote, pageID)
        upVoteResponsive = countUpVotes(hh.Responsive_Vote, pageID)
        downVoteResponsive = countDownVotes(hh.Responsive_Vote, pageID)
        upVoteSafe = countUpVotes(hh.Safe_Vote, pageID)
        downVoteSafe = countDownVotes(hh.Safe_Vote, pageID)

        metric = session.query(hh.Usage_Metrics).filter(hh.Usage_Metrics.PageID == pageID).count()

        if metric == 0:
            hh.add_db_object( hh.Usage_Metrics(pageID, avgTime, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe) )
        else:
            updateMetric(pageID, avgTime, visitsAtRisk, visitsVolunteer, visitsRep, visitsOther, numForums, upVoteClean, downVoteClean, upVoteResponsive, downVoteResponsive, upVoteSafe, downVoteSafe)