#############################################################################
# $Date:$
# $Rev: $
# $Author: $
# $URL:$
#############################################################################


from gluon.tools import Auth
from gluon.sqlhtml import *
from gluon.http import *
import datetime
DEFAULT = lambda : None
T = None

class CustomAuth(Auth):

    """
    The Custom version of the Auth class.  Adds some custom fields, mainly
    for integration of multiple logins with accounts
    """

    def __init__(self, environment, p, db=None, migrate=True):
        Auth.__init__(self, environment, db)
        global T
        T = p
        self.messages.invalid_login = T("We're sorry. " + \
            "The email or password you entered didn't match our records.  " + \
            "Please try again.")
        self.messages.lock_keys = False
        self.messages.disabled_login = T('Sorry. Your account has been disabled. Please contact support.')
        self.messages.lock_keys = True
        self.settings.table_user = db.define_table(
            self.settings.table_user_name,
            db.Field('first_name', length=128,default=''),
            db.Field('last_name', length=128,default=''),
            db.Field('email', length=128,default='',unique=True),
            db.Field('twitter_id', length=128,default=None,unique=True),
            db.Field('facebook_id', length=128,default=None,unique=True),
            db.Field('password', 'password', readable=False),
            db.Field('marketing', 'boolean', default=False),
            db.Field('zipcode', 'integer'),
            db.Field('birthday', 'date'),
            db.Field('registration_key', length=128, writable=False,
                     readable=False,default=''),
            migrate=migrate)
        table = self.settings.table_user
        table.first_name.requires = IS_NOT_EMPTY()
        table.last_name.requires = IS_NOT_EMPTY()
        table.password.requires = [IS_LENGTH(minsize=6,
                                    error_message="We're sorry.  Please " + \
                                    "enter a password with at least six " + \
                                    "characters."),
                                   CRYPT()]
        table.email.requires = [IS_EMAIL(error_message=T("Please enter a valid email address.")),
                             IS_NOT_IN_DB(db, '%s.email'
                             % self.settings.table_user._tablename,
                             error_message=T("We're sorry. " + \
                             "That email address already exists in our system. " + \
                             "Please login or choose another email address."))]
        table.zipcode.requires = IS_NULL_OR(IS_INT_IN_RANGE(1, 99999,
                                                 error_message=T("Invalid Zip Code")))
        table.birthday.requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d'),
                                        error_message=T('must be YYYY-MM-DD!')))
        table.registration_key.default = ''

    def get_or_create_user(self, keys):
        """
        Used for alternate login methods:
            If the user exists already then password is updated.
            If the user doesn't yet exist, then they are created.
        """
        if 'username' in keys:
            username = 'username'
        elif 'email' in keys:
            username = 'email'
        else:
            raise SyntaxError, "user must have username or email"
        table_user = self.settings.table_user
        passfield = self.settings.password_field
        user = self.db(table_user[username] == keys[username]).select().first()
        if user:
            if passfield in keys and keys[passfield]:
                user.update_record(**{passfield: keys[passfield],
                                      'registration_key': ''})
            if 'facebook_id' in keys and keys['facebook_id']:
                if user.facebook_id and user.facebook_id != keys['facebook_id']:
                    #something is wrong
                    return None
                else:
                    user.update_record(facebook_id=keys['facebook_id'])
            if 'twitter_id' in keys and keys['twitter_id']:
                if user.twitter_id and user.twitter_id != keys['twitter_id'] and \
                  self.db((table_user[username] == keys[username]) & 
                    (table_user['twitter_id'] == keys['twitter_id'])).count() > 0:
                    #either the twitter id saved with the email address does not 
                    # match the one passed in, or the one passed in already is in 
                    # the database with another user
                    #something is wrong
                    return None
                else:
                    user.update_record(twitter_id=keys['twitter_id'])
        else:
            d = {username: keys[username],
               'first_name': keys.get('first_name', keys[username]),
               'last_name': keys.get('last_name', ''),
               'registration_key': ''}
            keys = dict([(k, v) for (k, v) in keys.items() \
                           if k in table_user.fields])
            if keys.has_key('id'):
                del keys['id']
            d.update(keys)
            user_id = table_user.insert(**d)
            if self.settings.create_user_groups:
                group_id = self.add_group("user_%s" % user_id)
                self.add_membership(group_id, user_id)
            user = table_user[user_id]
        return user


