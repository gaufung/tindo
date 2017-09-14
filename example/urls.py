# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo import get, view, post, ctx, redirect


@view('index.html')
@get('/')
def index():
    return dict()


@view('index.html')
@get('/user/<username>')
def home(name):
    return dict(name=name)

