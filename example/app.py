# -*- coding:utf-8 -*-
import os
from tindo import Tindo
from example import urls
app = Tindo(os.path.dirname(os.path.abspath(__file__)))
app.add_module(urls)

