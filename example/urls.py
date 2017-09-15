# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx


@view('index.html')
@get('/')
def index():
    session = ctx.response.session
    session.name = 'gaofeng'
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


@view('comment.html')
@get('/user/<name>/<group>')
def comment(name, group):
    return dict(name=name, group=group)


@view('session.html')
@get('/session')
def session():
    sess = ctx.response.session
    return dict(name=sess.name)






