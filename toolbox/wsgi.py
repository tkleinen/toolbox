import os, sys

sys.path.append('/home/tarik/src/toolbox')
os.environ['DJANGO_SETTINGS_MODULE'] = 'toolbox.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
