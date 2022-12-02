#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request, session
#from flask_sqlalchemy import SQLAlchemy
import argparse
import os
import hh_db

DEFAULT_CONFIG = 'hh.cfg'
SETTINGS = {
    'db_username': 'root',
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
        hh_db.initiate_db(
            user=SETTINGS['db_username'],
            password=SETTINGS['db_password'],
            host=SETTINGS['db_host'],
            dbname=SETTINGS['db_name'],
        )
    app.run()


@app.route('/', methods=['GET'])
def page_index():
    return render_template('public/index.html')


@app.route('/risk_select', methods=['GET'])
def page_risk_select():
    print('risk_select')
    error_list = []
    request_dict = {}
    if request.args.get('search'):
        request_dict = {'atrisk': 'on'}
        set_srvcs = []
        for srvc in hh_db.Services:
            if request.args.get(srvc):
                set_srvcs.append(srvc)
        if set_srvcs:
            for srvc in set_srvcs:
                request_dict[srvc] = 'on'
            return redirect(url_for('search_results_page', **request_dict))
        else:
            ## make an error and fall thru to the normal page
            error_list.append('Must pick at least one desired service first.')
    elif request.args.get('sendhelp'):
        request_dict = {'atrisk': 'on'}
        set_srvcs = []
        for srvc in hh_db.Services:
            if request.args.get(srvc):
                set_srvcs.append(srvc)
        if set_srvcs:
            for srvc in set_srvcs:
                request_dict[srvc] = 'on'
            return redirect(url_for('send_help_page', **request_dict))
        else:
            ## make an error and fall thru to the normal page
            error_list.append('Must pick at least one desired service first.')
    return render_template('public/risk_select.html', 
            services=hh_db.Services,
            error_string='<br>'.join(error_list),
            )


@app.route('/send_help', methods=['GET','POST'])
def send_help_page():
    print('send_help_page')
    errors_list = []
    if request.args.get('sendhelp_init'):
        ## TODO: actually process the request
        error_list.append('ERROR: Request could not be processed!')
    return render_template('public/help_me.html')


@app.route('/volunteer_select', methods=['GET'])
def page_volunteer_select():
    print('volunteer_select')
    request_dict = request.args.to_dict()
    if request_dict:
        ## XXX TODO: actual checks...
        request_dict['volunteer'] = 'on'
        return redirect(url_for('search_results_page', **request_dict))
    return render_template('public/volunteer_select.html', selectList=[(x,x) for x in hh_db.Services])


@app.route('/org_rep', methods=['GET'])
def page_org_rep():
    return render_template('public/org_rep.html')


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


@app.route('/search_results', methods=['GET', 'POST'])
def search_results_page():
    print('search_results')
    print(request.args.to_dict())
    srvcs = []
    for i in hh_db.Services:
        if request.args.get(i):
            srvcs.append(i)
    localities = hh_db.match_all_localities(srvcs)
    organizations = hh_db.match_all_organizations(srvcs)
    programs = hh_db.match_all_programs(srvcs)
    return render_template('public/search_results.html', 
            localities=localities, 
            organizations=organizations, 
            programs=programs,
            services=hh_db.Services,
            )


@app.route('/org', methods=['GET'])
def org_page():
    request_dict = request.args.to_dict()
    orgid = request.args.get('orgid')
    orgid = 1
    with hh_db.Session.begin() as session:
        q = session.query(hh_db.Organization).filter_by(OrganizationID=orgid)
    org = q.first()
    forumposts = [ hh_db.Forum(UserID=1, TimeStamp=1, Comment='asdf%d' % x, PageID=1) for x in range(5)]
    return render_template('public/org_resource_page.html', org=org, forumposts=forumposts)


@app.route('/login',)
def login_page():
    if session['logged_in']:
        ## TODO: something? user trying to log in when already logged in
        return
    ## TODO: match these to the html template form vars...
    username=request.get('username')
    password=request.get('password')
    if username and password:
        uid = hh_db.check_username_password(username, password)
        if uid:
            session['logged_in'] = True
            session['user'] = uid
            ### TODO: a template to display logged in
            return 'loggged in'
    return render_template('public/login.html')


if __name__ == '__main__':
    _main()
