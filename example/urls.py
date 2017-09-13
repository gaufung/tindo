# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx


@view('index.html')
@get('/')
def index():
    return dict(name='gaofeng')


# @get('/name')
# def name():
#     return 'name'


@view('register.html')
@get('/register')
def register():
    ctx.response.set_cookie('name', '12')
    return dict()


@post('/registered')
def registered():
    i = ctx.request.input(name='', lastname='')
    return dict()
