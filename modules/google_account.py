# -*- coding: utf-8 -*-
"""
  Google account authentication implementation for web2py
"""
from modules import auth_base


class GoogleAuth(auth_base.BaseAuth,
                     auth_base.GoogleMixin):

    def login_url(self, next="/"):
        if self._request.vars.setdefault("openid.mode", None):
            if self._request.vars["openid.mode"] != "cancel":
                retval = self.get_authenticated_user(self._on_auth)
                return next
            else:
                self.redirect(self.settings['denied'])

        self.authenticate_redirect()
        self.settings['globals']['session'].flash="We's sorry something went wrong, please try again."
        #@TODO: should this be an option?
        return '/register/login'

    def logout_url(self, next="/"):
        return next

    def get_user(self):
        if self.settings['globals']['session'].googleauth_user:
            return self.settings['globals']['session'].googleauth_user

    def _on_auth(self, user):
        #print "google user" + repr(user)
        #google user{'locale': 'en-us', 'first_name': '', 'last_name': '', 'name': u'', 'email': ''}

        keys = dict([(str(k), v) for (k, v) in user.items()])

        self.settings['globals']['session'].googleauth_user = keys
        return user

