#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request
#from flask_sqlalchemy import SQLAlchemy
import argparse
import os
import hh_db

DEFAULT_CONFIG = 'hh.cfg'
SETTINGS = {
    'db_username': 'admin',
    'db_password': 'password123',
    'db_host': '127.0.0.1',
    'db_port': 3306,
    'db_name': 'HH',
}


parser = argparse.ArgumentParser(description='HTML Flask application for HelpingHands')
parser.add_argument('-c', '--config', metavar='FILE',
                    type=str, help='add a non-default filename for the config')
parser.add_argument('--database', metavar='FILE',
                    type=str, help='use a non-default location for the database')

# # initialize the Flask runtime
app = Flask(__name__)

args = None


def _main():
    global app, db, db_uri, args
    args = parser.parse_args()
    ## XXX TODO: do stuff with configs files, etc....
    if args.database:
        raise Exception('not yet supported (error 2752)')
        # # use custom database filename from command line arg
        #db_uri = 'mysql://%s' % args.database
        #if not os.path.exists(args.database):
        #    #hh_db.create_fake_database(args.database)
        #    raise Exception('file does not exist: %s' % args.database)
    else:
        # # use database URI derived from settings
        hh_db.initiate_mysql_engine(
            user=SETTINGS['db_username'],
            password=SETTINGS['db_password'],
            hostname=SETTINGS['db_host'],
            dbname=SETTINGS['db_name'],
        )
    app.run()


@app.route('/', methods=['GET'])
def page_index():
    return render_template('public/index.html')


@app.route('/risk_select', methods=['GET'])
def page_risk_select():
    print(repr(request.args.to_dict()))
    return render_template('public/content/risk_select.html')


@app.route('/volunteer_select', methods=['GET'])
def page_volunteer_select():
    return render_template('public/content/volunteer_select.html')


@app.route('/org_rep', methods=['GET'])
def page_org_rep():
    return render_template('public/content/org_rep.html')


@app.route('/about', methods=['GET'])
def page_about_us():
    return render_template('public/about.html')


@app.route('/debug', methods=['GET', 'POST'])
def page_debug():
    if args.database:
        dbloc = args.database
    else:
        dbloc = '<<NONE>>'
    return render_template('debug.html',
                           dbloc=args.database,
                           reqargs=request.args.to_dict(),
                           )


@app.route('/search', methods=['GET', 'POST'])
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
