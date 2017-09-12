# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
from tindo.tindo import get, view


@view('index.html')
@get('/')
def index():
    return dict(name='gaofeng')


@get('/name')
def name():
    return 'name'