import hh_db as hh

"""
params: pageID - PageID for which we are obtaining metric

Metrics Collection: Used to obtain NumForumPosts for a certain PageID

example: metrics.countForum( 1 )

return: int numForums
"""
def countForum(pageID):
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

"""
params: category - Vote category i.e. safe/clean/responsive 
        pageID - PageID for which we are obtaining metric

Metrics Collection: Used to obtain NumUpVotesClean/NumUpVotesSafe/NumUpVotesResponsive for a certain PageID

example: metrics.countUpVotes( hh_db.Safe_Vote, 1 )
example: metrics.countUpVotes( hh_db.Clean_Vote, 1 )
example: metrics.countUpVotes( hh_db.Responsive_Vote, 1 )

return: int numUpVotes
"""
def countUpVotes(category, pageID):
    with hh.Session.begin() as session:
        numUpVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==True).count()
        return numUpVotes

"""
params: category - Vote category i.e. safe/clean/responsive 
        pageID - PageID for which we are obtaining metric

Metrics Collection: Used to obtain NumDownVotesClean/NumDownVotesSafe/NumDownVotesResponsive for a certain PageID

example: metrics.countDownVotes( hh_db.Safe_Vote, 1 )
example: metrics.countDownVotes( hh_db.Clean_Vote, 1 )
example: metrics.countDownVotes( hh_db.Responsive_Vote, 1 )

return: int numDownVotes
"""
def countDownVotes(category, pageID):
    with hh.Session.begin() as session:
        numDownVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==False).count()
        return numDownVotes

"""
params: userType - AtRisk/Volunteer/Representative
        pageID - PageID for which we are obtaining metric

Metrics Collection: Used to obtain NumVisits for a specific userType on a certain PageID

return: int numVisits
"""
def countVisits():
    ##TODO: implement to count number of times page is accessed by a specific userType
    return 0

"""
params: pageID - PageID for which we are obtaining metric

Metrics Collection: Used to obtain AvgTimeSpent on a certain PageID by all users who visited the page

return: double timeSpent
"""
def avgTimeSpent():
    ##TODO: implement to calculate avgTimeSpent on page for total page visit
    return 0

