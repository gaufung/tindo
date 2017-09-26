**tindo:**

A micro-framework based on wsgiref

# 0 *install*
```shell
pip install tindo
```

# 1 **Main Components**

+ ~~*get* decorator: for HTTP GET Method~~
+ ~~*post* decorator: for HTTP POST Method~~
+ *route* decorator: for HTTP GET and POST methods
+ *Route* class: wrap the decorated functions, which contains the `match(self, url)` methods to determinate whether
the url match the route nor not.
+ *Request* class: wrap the wsgi's `environ` dictionary into more useful apis, including `methods`, `cookies`, `path`
 and `inputs` etc.
+ *Response* class: a high-level of wsgi's `status` and `response_headers`.
+ *view* decorator: a specific html template to render
+ *Tindo* class: main class of web framework. To approach the multi-thread environment, use threading module'
s `Local` class.

# 2 **Usages**

The example folder contains the minimum demo using `tindo`.

```
- example
    - static 
       - style.css
    - templates
       - index.html
       - name.html
       - register.html
       - comment.html
       - register.html
       - registered.html
       - session.html
    - app.py
    - urls.py
```

## 2.1 urls.py
This module defines the main `routes` rules of web application, 
just like `Django`.


### 2.1.1 GET Method

```python

@view('index.html')
@route('/')
def index():
    return dict()

```
Using `get` decorator to decorate a function. Using `view`
decorator to decide which template to be rendered.
If no variables in the template, just return a `dict`.

### 2.1.2 POST Method

```python
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
```
The thread-safe `ctx` variable includes current request, which
contains `posted` values in `wsgi.input` dictionary.


### 2.1.3 GET Query

```python
@view('name.html')
@route('/user/<username>')
def user(name):
    return dict(name=name)
    
@view('comment.html')
@route('/user/<name>/<group>')
def comment(name, group):
    return dict(name=name, group=group)
```

Referring `flask` route, url can contain a query variable. If 
`get` decorator with `<variable>`, the route will convert the 
url's last component as parameter and invoke the function.

### 2.1.4 Session
Session is used to keep identification of individual client. 
[This article](http://eli.thegreenplace.net/2011/06/24/django-sessions-part-i-cookies/)
points out how session works. In `tindo`, the application contain a global 
dictionary that keeps every session-id. Each session is a dictionary instance in memory.

```python
@view('session.html')
@route('/session')
def session():
    sess = ctx.response.session
    return dict(name=sess.name)
``` 

## 2.2 app.py

This module is main part of web application. Just import `tindo` and
make Tindo instance and run it. But it needs to import `url` module.
```python
import os
from tindo import Tindo
import urls
app = Tindo(os.path.dirname(os.path.abspath(__file__)))
app.add_module(urls)
if __name__ == '__main__':
    app.run()
```

# 3 RoadMaps

- [ ] Export it to Python 3.x
- [x] Add session feature
- [x] Refactor

# 4 Update Notes

+ update `route` decorator and deprecate `get` and `post` decorators. 17. Sep. 2017
+ re-organize `tindo.py` wsgi protocol using `__call__`. 18. Sep. 2017
+ add `local` module which behave like `threading.local`. 19. Sep. 2017
+ add `manage.py` script to control `test` and `app`, refactor the ugly `reload(sys)`
statement, and use absolute import features. 20. Sep. 2017
+ add Tindo's `__init__.py` to make less `import` statement.
