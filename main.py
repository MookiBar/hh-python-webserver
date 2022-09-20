#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request
#from flask_sqlalchemy import SQLAlchemy
import argparse
import os
import hh_db

DEFAULT_CONFIG = 'hh.cfg'
SETTINGS = {
    'db_username': 'XXX',
    'db_password': 'XXX',
    'db_host': 'XXX',
    'db_port': '12345',
    'db_name': 'XXX',
}


parser = argparse.ArgumentParser(description='HTML Flask application for HelpingHands')
parser.add_argument('-c','--config', metavar='FILE',
                    type=str, help='add a non-default filename for the config')
parser.add_argument('--database', metavar='FILE',
                    type=str, help='use a non-default location for the database')

# # initialize the Flask runtime
app = Flask(__name__)
# # borrow the uninitialized db obj from hh_db
db = hh_db.db
# # location of sql db, e.g. mysql://mydb.db
db_uri = None

def _main():
    global app, db, db_uri
    args = parser.parse_args()
    ## XXX TODO: do stuff with configs files, etc....
    if args.database:
        # # use custom database filename from command line arg
        db_uri = 'mysql://%s' % args.database
        if not os.path.exists(args.database):
            #hh_db.create_fake_database(args.database)
            raise Exception('file does not exist: %s' % args.database)
    else:
        # # use database URI derived from settings
        db_uri = 'mysql://{username}:{password}@{host}:{port}/{name}'.format(
            username=SETTINGS['db_username'],
            password=SETTINGS['db_password'],
            host=SETTINGS['db_host'],
            name=SETTINGS['db_name'],
        )
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.Model.metadata.reflect(db.engine)
    # # finally initialize the db from hh_db
    db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('woops.html')

@app.route('/debug', methods=['GET', 'POST'])
def debug_page():
    args = request.args
    return render_template('debug.html')

@app.route('/search', methods=['GET', 'POST']):
def search_page():
    return render_template('woops.html')

@app.route('/org', methods=['GET'])
def org_page():
    return render_template('woops.html')

@app.route('/login',)
def login_page():
    return render_template('woops.html')


if __name__ == '__main__':
    _main()
