# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx, redirect


@view('index.html')
@get('/')
def index():
    return dict(name='gaofeng')


@get('/home')
def home():
    raise redirect('/')


# @get('/name')
# def name():
#     return 'name'


# @view('register.html')
# @get('/register')
# def register():
#     ctx.response.set_cookie('name', '12')
#     return dict()
#
#
# @post('/registered')
# def registered():
#     i = ctx.request.input(name='', lastname='')
#     return dict()


# @view('name.html')
# @get('/names/:name')
# def query(name):
#     return dict(name=
# @get('/static/style.css')
# def query():
#     return dict()

