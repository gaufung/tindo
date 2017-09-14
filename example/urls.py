# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx


@view('index.html')
@get('/')
def index():
    return dict()


@view('register.html')
@get('/register')
def register():
    return dict()


@view('registered.html')
@post('/registered')
def registered():
    i = ctx.request.input(firstname='', lastname='')
    return dict(firstname=i.get('firstname', ''), lastname=i.get('lastname', ''))


@view('name.html')
@get('/user/<username>')
def user(name):
    return dict(name=name)



