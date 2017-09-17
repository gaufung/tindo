# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo.tindo import get, view, post, ctx, route


@view('index.html')
@route('/')
def index():
    session = ctx.response.session
    session.name = 'gaofeng'
    return dict()


@view('register.html')
@route('/register', methods=['GET', 'POST'])
def register():
    i = ctx.request.input(firstname=None, lastname=None)
    firstname = i.get('firstname')
    lastname = i.get('lastname')
    if firstname is None and lastname is None:
        return dict(register=True)
    else:
        return dict(firstname=firstname, lastname=lastname)


@view('name.html')
@route('/user/<username>')
def user(name):
    return dict(name=name)


@view('comment.html')
@route('/user/<name>/<group>')
def comment(name, group):
    return dict(name=name, group=group)


@view('session.html')
@route('/session')
def session():
    sess = ctx.response.session
    return dict(name=sess.name)






