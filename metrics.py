import hh_db as hh

"""
countForum('PageID') to count number of rows in Forum table matching a certain PageID

Metrics Collection: Used to obtain NumForumPosts

example: metrics.countForum( 1 )
returns: Forum posts on PageID==1
"""
def countForum(pageID):
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

"""
countUpVotes('Vote_table_name', 'PageID') to count number of up votes in a Vote table matching a certain PageID

Metrics Collection: Used to obtain NumUpVotesClean/NumUpVotesSafe/NumUpVotesResponsive

example: metrics.countUpVotes( hh_db.Safe_Vote, 1 )
example: metrics.countUpVotes( hh_db.Clean_Vote, 1 )
example: metrics.countUpVotes( hh_db.Responsive_Vote, 1 )
returns: Up Votes on PageID==1
"""
def countUpVotes(category, pageID):
    with hh.Session.begin() as session:
        numUpVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==True).count()
        return numUpVotes

"""
countDownVotes('Vote_table_name', 'PageID') to count number of down votes in a Vote table matching a certain PageID

Metrics Collection: Used to obtain NumDownVotesClean/NumDownVotesSafe/NumDownVotesResponsive

example: metrics.countDownVotes( hh_db.Safe_Vote, 1 )
example: metrics.countDownVotes( hh_db.Clean_Vote, 1 )
example: metrics.countDownVotes( hh_db.Responsive_Vote, 1 )
returns: Down Votes on PageID==1
"""
def countDownVotes(category, pageID):
    with hh.Session.begin() as session:
        numDownVotes = session.query(category).filter(category.PageID==pageID).filter(category.Vote==False).count()
        return numDownVotes