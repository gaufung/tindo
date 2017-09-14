# -*- coding:utf-8 -*-
import sys
sys.path.insert(0, '../')
reload(sys)
import os
from tindo import Tindo

app = Tindo(os.path.dirname(os.path.abspath(__file__)))

import urls

app.add_module(urls)

if __name__ == '__main__':
    app.run()