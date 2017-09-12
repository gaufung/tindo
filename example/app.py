# -*- coding:utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
import os
from tindo.tindo import WSGIApplication, Jinja2TemplateEngine

wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

wsgi.template_engine = template_engine

import urls

wsgi.add_module(urls)

if __name__ == '__main__':
    wsgi.run()