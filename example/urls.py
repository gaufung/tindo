# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx, redirect


@view('index.html')
@get('/')
def index():
    return dict()


@view('register.html')
@get('/register')
def register():
    return dict()


@view('name.html')
@get('/user/<username>')
def user(name):
    return dict(name=name)

