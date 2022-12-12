#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request, session
#from flask_sqlalchemy import SQLAlchemy
import argparse
import os
import hh_db
from sqlalchemy import select
import metrics
import hh_static_resource_links as hh_links
from time import sleep

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
# # TODO: generate secret key using random() or similar
app.secret_key = 'kiEIFJIefkjl4939jf9'

args = None


def get_current_user(_session, allow_exceptions=False):
    try:
        logged_in  = _session['logged_in']
    except Exception:
        return None
    if logged_in:
        try:
            userid = session['user']
            user = hh_db.get_user(userid)
        except Exception as e:
            if allow_exceptions:
                raise e
            else:
                return None
        else:
            return user
    else:
        return None


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


def flask_sleep(seconds):
    ## i hate that we need this, but to get a sleep without locking the gil...
    ## i'm open to suggestions on that...
    count = int(seconds / 0.01)
    for i in range(count):
        sleep(0.01)


@app.route('/', methods=['GET'])
def page_index():
    return render_template('public/index.html',
            user = get_current_user(session),
            )


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
            user = get_current_user(session),
            )


@app.route('/send_help', methods=['GET','POST'])
def send_help_page():
    print('send_help_page')
    errors_list = []
    if request.args.get('sendhelp_init'):
        ## TODO: actually process the request
        error_list.append('ERROR: Request could not be processed!')
    return render_template('public/help_me.html',
            user = get_current_user(session),
            )


@app.route('/volunteer_select', methods=['GET'])
def page_volunteer_select():
    print('volunteer_select')
    error_list = []
    request_dict = {}
    if request.args.get('search'):
        request_dict = {'volunteer': 'on'}
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
    return render_template('public/volunteer_select.html', 
            services=hh_db.Services,
            error_string='<br>'.join(error_list),
            user = get_current_user(session),
            )


@app.route('/org_rep', methods=['GET'])
def page_org_rep():
    return render_template('public/org_rep.html',
            user = get_current_user(session),
            )


@app.route('/resources', methods=['GET'])
def page_resources():
    return render_template('public/resources.html', 
            addiction=hh_links.ADDICTION_LINKS,
            health=hh_links.HEALTH_LINKS,
            mentalHealth=hh_links.MENTAL_HEALTH_LINKS,
            user = get_current_user(session),
            )


@app.route('/about', methods=['GET'])
def page_about_us():
    return render_template('public/about.html',
            user = get_current_user(session), 
            )


@app.route('/contact', methods=['GET'])
def page_contact_us():
    print('contact')
    return render_template('public/contact.html',
            user = get_current_user(session),
            )


@app.route('/login', methods=['GET','POST'])
def login_page():
    redirect_url = None
    error_list = []
    success_list = []
    allow_login = True
    try:
        logged_in  = session['logged_in']
    except Exception:
        logged_in = False
    if logged_in:
        success_list.append('ALREADY LOGGED IN. Redirecting...')
        allow_login = False
        redirect_url = '/'
    elif request.args.get('login'):
        print('XXX1')
        username=request.args.get('email')
        password=request.args.get('password')
        if username and password:
            print('XXX2')
            uid = hh_db.check_username_password(username, password)
            if uid:
                print('XXX3')
                session['logged_in'] = True
                session['user'] = uid
                ### TODO: a template to display logged in
                success_list.append('SUCCESSFULLY LOGGED IN')
                allow_login = False
            else:
                ## unsuccessful login
                flask_sleep(2)
                error_list.append('Incorrect email or password.')
    print('XXX4')
    return render_template('public/login.html', 
            redirect_url=redirect_url,
            allow_login=allow_login,
            error_string='<br>'.join(error_list),
            success_string='<br>'.join(success_list),
            user = get_current_user(session),
            )


@app.route('/register', methods=['GET', 'POST'])
def page_register():
    print('register')
    return render_template('public/register.html',
            user = get_current_user(session),
            )



@app.route('/account', methods=['GET','POST'])
def page_account():
    error_list = []
    success_list = []
    redirect_url = None
    user = None
    userid = None
    try:
        user = get_current_user(session, allow_exceptions=True)
    except Exception as e:
        print(repr(e))
        user = None
        error_list.append('Encountered an error accessing your info.')
    if user:
        logged_in = True
    else:
        error_list.append('Not logged in.')
        redirect_url = '/'
    return render_template('/public/account.html', 
            redirect_url=redirect_url,
            logged_in=logged_in,
            error_string='<br>'.join(error_list),
            success_string='<br>'.join(success_list),
            user = get_current_user(session),
            )





@app.route('/logout', methods=['GET','POST'])
def logout_page():
    session.pop('user', None)
    session['logged_in'] = False
    return redirect('/')




@app.route('/debug', methods=['GET', 'POST'])
def page_debug():
    if args.database:
        dbloc = args.database
    else:
        dbloc = '<<NONE>>'
    return render_template('debug.html',
                           dbloc=args.database,
                           reqargs=request.args.to_dict(),
                           user=get_current_user(session),
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
            user=get_current_user(session),
            )


@app.route('/org', methods=['GET'])
def org_page():
    request_dict = request.args.to_dict()
    orgid = request.args.get('orgid')
    with hh_db.Session.begin() as session:
        q = session.query(hh_db.Organization).filter_by(OrganizationID=orgid)
        pageid = select(hh_db.Organization.PageID).where(hh_db.Organization.OrganizationID==orgid)
        q2 = select(hh_db.Forum.UserID, hh_db.Forum.TimeStamp, hh_db.Forum.Comment).where(hh_db.Forum.PageID==pageid)
        ForumResult = session.execute(q2)
        forumposts = ForumResult.fetchall()
    org = q.first()
    upVoteResponsive = metrics.__getUpVotesCount(hh_db.Responsive_Vote, pageid)
    downVoteResponsive = metrics.__getDownVotesCount(hh_db.Responsive_Vote, pageid)
    return render_template('public/org_resource_page.html',
            org=org,
            upresp = upVoteResponsive,
            downresp = downVoteResponsive,
            forumposts=forumposts,
            services=hh_db.Services,
            user=get_current_user(session),
            )


@app.route('/prog', methods=['GET'])
def prog_page():
    request_dict = request.args.to_dict()
    progid = request.args.get('progid')
    with hh_db.Session.begin() as session:
        q = session.query(hh_db.Program).filter_by(ProgramID=progid)
        pageid = select(hh_db.Program.PageID).where(hh_db.Program.ProgramID==progid)
        q2 = select(hh_db.Forum.UserID, hh_db.Forum.TimeStamp, hh_db.Forum.Comment).where(hh_db.Forum.PageID==pageid)
        ForumResult = session.execute(q2)
        forumposts = ForumResult.fetchall()
    prog = q.first()
    upVoteResponsive = metrics.__getUpVotesCount(hh_db.Responsive_Vote, pageid)
    downVoteResponsive = metrics.__getDownVotesCount(hh_db.Responsive_Vote, pageid)
    return render_template('public/prog_resource_page.html',
            prog=prog,
            upresp = upVoteResponsive,
            downresp = downVoteResponsive,
            forumposts=forumposts,
            services=hh_db.Services,
            user=get_current_user(session),
            )


@app.route('/loc', methods=['GET'])
def loc_page():
    request_dict = request.args.to_dict()
    locid = request.args.get('locid')
    with hh_db.Session.begin() as session:
        q = session.query(hh_db.Locality).filter_by(LocalityID=locid)
        pageid = select(hh_db.Locality.PageID).where(hh_db.Locality.LocalityID==locid)
        q2 = select(hh_db.Forum.UserID, hh_db.Forum.TimeStamp, hh_db.Forum.Comment).where(hh_db.Forum.PageID==pageid)
        ForumResult = session.execute(q2)
        forumposts = ForumResult.fetchall()
        q3 = select(hh_db.Organization.Name).where(hh_db.Locality.OrganizationID == hh_db.Organization.OrganizationID).where(hh_db.Locality.LocalityID==locid)
        OrgResult = session.execute(q3)
        orgs = OrgResult.fetchall()
        q4 = select(hh_db.Program.Name).where(hh_db.Locality.ProgramID == hh_db.Program.ProgramID).where(hh_db.Locality.LocalityID==locid)
        ProgResult = session.execute(q4)
        progs = ProgResult.fetchall()
    loc = q.first()
    upVoteClean = metrics.__getUpVotesCount(hh_db.Clean_Vote, pageid)
    downVoteClean = metrics.__getDownVotesCount(hh_db.Clean_Vote, pageid)
    upVoteResponsive = metrics.__getUpVotesCount(hh_db.Responsive_Vote, pageid)
    downVoteResponsive = metrics.__getDownVotesCount(hh_db.Responsive_Vote, pageid)
    upVoteSafe = metrics.__getUpVotesCount(hh_db.Safe_Vote, pageid)
    downVoteSafe = metrics.__getDownVotesCount(hh_db.Safe_Vote, pageid)
    return render_template('public/loc_resource_page.html',
            loc=loc,
            upclean = upVoteClean,
            downclean = downVoteClean,
            upresp = upVoteResponsive,
            downresp = downVoteResponsive,
            upsafe = upVoteSafe,
            downsafe = downVoteSafe,
            orgs = orgs,
            progs = progs,
            forumposts=forumposts,
            services=hh_db.Services,
            user=get_current_user(session),
            )

if __name__ == '__main__':
    _main()
