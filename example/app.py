# -*- coding:utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
import os
from tindo import Tindo, Jinja2TemplateEngine

app = Tindo(os.path.dirname(os.path.abspath(__file__)))

template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

app.template_engine = template_engine

import urls

app.add_module('urls')

if __name__ == '__main__':
    app.run()