# -*- coding: utf-8 -*-
"""
  Facebook connect implementation for web2py
"""
import logging

class FacebookAuth():
    """
    Authentication integration with Facebook graph API javascript SDK.  The user 
    is authentication client side using javascript and a cookie.  as part of the 
    javascript callback they are redirected to a controller that saves the cookie
    content in the session.  therefore, there is no login or logout to implement
    here, only get_user, and then we can plug this into Auth.
    """

    session = None
    def __init__(self, session):
        self.session = session

    def login_url(self, next="/"):
        """
        unused
        """
        return next

    def logout_url(self, next="/"):
        """
        unused
        """
        return next

    def get_user(self):
        if self.session.fbauth_user:
            return self.session.fbauth_user

