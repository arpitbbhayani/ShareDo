#############################################################################
# $Date: 2010-04-29 12:30:50 -0700 (Thu, 29 Apr 2010) $
# $Rev: 1214 $
# $Author: cfhowes $
# $URL: http://24.239.32.45:9090/svn/trunk/src/tenthrow/opt/web2py/applications/tenthrow/controllers/auth_ext.py $
#############################################################################


def twitter():
    """
    Login/auth integration with twitter.  Makes use of the OAuth login provided
    by the module.

    As part of the login steps, if the user has not logged in using this twitter
    account before they will be directed to twitemail() to provide an email
    address for the account being created.

    if there is already a logged in user, this will allow that user to associate
    a twitter account with their current account.
    """
    if auth.is_logged_in() and auth.user.twitter_id:
        redirect(URL(r=request, c='default', f='index'))
    from applications.tenthrow.modules.twitter_account import TwitterAuth
    #@TODO: put these keys elsewhere
    key = ''
    secret = ''

    auth.settings.login_form=TwitterAuth(request, response,
         **{
        'twitter_consumer_key':key,
        'twitter_consumer_secret':secret,
        'denied':URL(r=request, f='denied'),
        'globals':globals()})

    return auth.login(next=URL(r=request, c='home', f='index'))

def twitemail():
    """
    If this is the first time the twitter user has logged in with us, get an
    email address from them.  This needs to be a new email address not already in
    they system.  To add a twitter account to an existing account, the user must
    login with that account first, then add twitter to it (link on the account
    page)
    """
    if auth.is_logged_in():
        session.twitterauth_user['email'] = auth.user.email
        return twitter()

    user = db((db.auth_user.twitter_id==session.twitterauth_user['twitter_id']) &
              (db.auth_user.email!=None)).select().first()
    if user:
        session.twitterauth_user['email'] = user.email
        return twitter()

    form = SQLFORM.factory(
        Field('email', requires=[IS_EMAIL(error_message="Please enter a valid email address."),
                                 IS_NOT_IN_DB(db, 'auth_user.email')]),
        _name="emailaddyform",
        _onsubmit="return submitTwitEmail();"
        )

    if form.accepts(request.vars, session, formname="twitemail"):
        session.twitterauth_user['email'] = form.vars.email
        return twitter()
    return dict(form=form)

def facebook():
    """
    Integrate with the facebook graph API to complete user authentication and
    account creation
    """
    import facebook
    #@TODO: put these somewhere global
    facebook_appid = ''
    facebook_secret = ''

    fb_user = facebook.get_user_from_cookie(request.cookies, facebook_appid, facebook_secret)
    if fb_user:
        graph = facebook.GraphAPI(fb_user["access_token"])
        profile = graph.get_object("me")

        if profile.setdefault('email', None):
            #do login
            profile['facebook_id'] = str(fb_user['uid'])
            keys = dict([(str(k), v) for (k, v) in profile.items()])
            session.fbauth_user = keys
            from applications.tenthrow.modules.facebook_account import FacebookAuth
            auth.settings.login_form=FacebookAuth(session)
            return auth.login(next=URL(r=request, c='home', f='index'))
        else:
            return "we need your email damint"
    #@TODO: return something reasonable if we get here.
    return dict()




def google():
    """
    Complete login/account creation via the google authentication service
    """
    if auth.is_logged_in():
        redirect(URL(r=request, c='default', f='index'))
    from applications.tenthrow.modules.google_account import GoogleAuth
    auth.settings.login_form=GoogleAuth(request, response,
         **{'denied':URL(r=request, f='denied'),
            'globals':globals()})

    return auth.login(next=URL(r=request, c='home', f='index'))


def denied():
    return dict(message="User canceled the request or denied access")
