#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy

## this is a placeholder activation that needs to attach to a flask app later (in main.py)
db = SQLAlchemy()

## XXX TODO: make sure every string value pulled from the dict in
##      db.Model.metadata.tables matches the name of the actual table in the db!!
##      Also make sure the value used in repr exists and is the right type!

class User(db.Model):
    """
    Any person (user, representative, etc)...
    """
    db.Model.metadata.tables['User']

    def __repr__(self):
        return repr(self.UserID)

class Representative(db.Model):
    """
    User (rel) who represents an Organization
    """
    db.Model.metadata.tables['Representative']

    def __repr__(self):
        return repr(self.UserID)

class Organization(db.Model):
    """
    Any group, optionally linked by any Representative or Locality
    """
    db.Model.metadata.tables['Organization']

    def __repr__(self):
        return repr(self.OrganizationID)

class Locality(db.Model):
    """
    Physial location/address linked to an Organization or Program
    """
    db.Model.metadata.tables['Locality']

    def __repr__(self):
        return repr(self.LocalityID)

class Program(db.Model):
    """
    Initiative (optionally sub'd to an Organization) linked to a Locality
    """
    db.Model.metadata.tables['Program']

    def __repr__(self):
        return repr(self.ProgramID)

class Status(db.Model):
    """
    Status of ranks and voting associated with a Page
    """
    db.Model.metadata.tables['Program']

    def __repr__(self):
        return repr(self.ProgramID)

class Ratings(db.Model):
    """
    possibly defunct?
    """
    db.Model.metadata.tables['Ratings']

    def __repr__(self):
        return repr(self.RatingID)

class Forum(db.Model):
    """
    user-submitted posts attached to a Page
    """
    db.Model.metadata.tables['Forum']

    def __repr__(self):
        return repr(self.ForumID)

class Page(db.Model):
    """
    aggregation of all elements to display for an Organization/Program/Locality
    """
    db.Model.metadata.tables['Page']

    def __repr__(self):
        return repr(self.PageID)


class UsageMetrics(db.Model):
    """
    statistics derived from a Page
    """
    db.Model.metadata.tables['Usage_Metrics']

    def __repr__(self):
        return repr(self.MetricID)




