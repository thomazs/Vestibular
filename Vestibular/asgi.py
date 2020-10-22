"""
ASGI config for Vestibular project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import os
import sys
import site

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#activate_this = os.path.join(ROOT, 'venv2', 'Scripts', 'activate_this.py')
## activate_this = 'C:/Users/myuser/Envs/my_application/Scripts/activate_this.py'
## execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read(),dict(__file__=activate_this))


# Add the site-packages of the chosen virtualenv to work with
# site.addsitedir('C:/Users/myuser/Envs/my_application/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
#sys.path.append('C:/Users/myuser/my_application')
#sys.path.append('C:/Users/myuser/my_application/my_application')
sys.path.insert(0, os.path.join(ROOT, 'venv2', 'Lib', 'site-packages'))
sys.path.insert(0, os.path.join(ROOT, 'venv2', 'Lib'))
sys.path.insert(0, os.path.join(ROOT, 'venv2'))

sys.path.insert(0, os.path.join(ROOT, 'venv', 'Lib', 'site-packages'))
sys.path.insert(0, os.path.join(ROOT, 'venv', 'Lib'))
sys.path.insert(0, os.path.join(ROOT, 'venv'))

sys.path.insert(0, os.path.join(ROOT, 'Vestibular'))
sys.path.insert(0, ROOT)
site.addsitedir(os.path.join(ROOT, 'venv2', 'Lib', 'site-packages'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'Vestibular.settings'

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vestibular.settings')

application = get_asgi_application()
