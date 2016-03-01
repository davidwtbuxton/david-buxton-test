import os

import dbux.boot


dbux.boot.setup()


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbux.settings')

application = get_wsgi_application()
