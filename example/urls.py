# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
import random
from tindo.tindo import get, view, post, ctx, route
from tindo.http import redirect

@view('index.html')
@route('/')
def index():
    session = ctx.response.session
    session.number = random.randint(1, 100)
    session.times = 10
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


@view('game.html')
@route('/game', methods=['GET', 'POST'])
def game():
    i = ctx.request.input(number=None)
    times = ctx.response.session.times
    number = ctx.response.session.number
    guess_number = i.get('number')
    if guess_number is not None:
        guess_number = int(guess_number)
        if times:
            times -= 1
            ctx.response.session.times = times
            if guess_number > number:
                return dict(success=False, status='Too Big', times=times)
            elif guess_number < number:
                return dict(success=False, status='Too Small', times=times)
            else:
                return dict(success=True)
        else:
            redirect('/')
    else:
        return dict(times=times, status='')







