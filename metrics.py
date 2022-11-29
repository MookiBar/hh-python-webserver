import hh_db as hh

"""
countForum('PageID') to count number of rows in a table matching a certain PageID

Metrics Collection: Used to obtain NumForumPosts

example: metrics.countForum( 1 )
returns: Forum posts on PageID==1
"""
def countForum(pageID):
    with hh.Session.begin() as session:
        numForums = session.query(hh.Forum).filter(hh.Forum.PageID==pageID).count()
        return numForums

        