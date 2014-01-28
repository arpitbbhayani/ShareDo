# -*- coding: utf-8 -*-
"""
  Twitter authentication implementation for web2py
"""
import logging
from modules import auth_base


class TwitterAuth(auth_base.BaseAuth,
                     auth_base.TwitterMixin):

    def login_url(self, next="/"):
        if self._request.vars.setdefault("oauth_token", None):
                retval = self.get_authenticated_user(self._on_auth)
                logging.info("just verified")
                logging.info(repr(self.settings['globals']['session'].twitterauth_user))
                logging.info("redirecting to: " + next)
                return next
        if self._request.vars.setdefault("denied", None):
            self.redirect(self.settings['denied'])
        self.authorize_redirect()
        logging.info("no auth yet redirecting to: " + next)
        self.settings['globals']['session'].flash="We's sorry something went wrong, please try again."
        #@TODO: should this be an option?
        return '/register/login'

    def logout_url(self, next="/"):
        return next

    def get_user(self):
        logging.info("checking for user info")
        if self.settings['globals']['session'].twitterauth_user and \
           self.settings['globals']['session'].twitterauth_user.has_key('email'):
            logging.info("returning user info")
            return self.settings['globals']['session'].twitterauth_user

    def _on_auth(self, user):
        #print "twitter user" + repr(user)
        #twitter user{u'id': <int>, u'verified': False, u'profile_sidebar_fill_color': u'e0ff92', u'profile_text_color': u'000000', u'followers_count': 6, u'protected': True, u'location': u'', u'profile_background_color': u'9ae4e8', 'username': u'', u'utc_offset': -28800, u'statuses_count': 0, u'description': u'', u'friends_count': 0, u'profile_link_color': u'0000ff', u'profile_image_url': u'http://s.twimg.com/a/1271213136/images/default_profile_0_normal.png', u'notifications': False, u'geo_enabled': False, u'profile_background_image_url': u'http://s.twimg.com/a/1271213136/images/themes/theme1/bg.png', u'name': u'', u'lang': u'en', u'profile_background_tile': False, u'favourites_count': 0, u'screen_name': u'', u'url': None, u'created_at': u'Wed Jul 08 18:27:49 +0000 2009', u'contributors_enabled': False, u'time_zone': u'Pacific Time (US & Canada)', 'access_token': {'secret': 'IuwByjwDlF6deKvi1TIvgatJNG1hEwhwvJNgK9zMHrc', 'user_id': '54981822', 'screen_name': '', 'key': '54981822-OgsiU9LW99HiP2Sq5DON8WPQ5IDUMn5BWL3ZBJz6u'}, u'profile_sidebar_border_color': u'87bc44', u'following': False}

        if not user:
            self.settings['globals']['session'].flash="We's sorry something went wrong, please try again."
            #@TODO: should this be an option?
            self.redirect('/register/login')

        keys = dict([(str(k), v) for (k, v) in user.items()])
        keys['first_name'] = keys['username']
        del keys['username']
        keys['twitter_id'] = str(keys['id'])

        logging.info(keys.keys)
        self.settings['globals']['session'].twitterauth_user = keys
        if not keys.has_key('email'):
            self.redirect('/auth_ext/twitemail')

        return user
