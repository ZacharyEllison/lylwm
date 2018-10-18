import os
# import excavator

PORT = os.getenv('WEB_PORT', 9991)
DEBUG = os.getenv('DEBUG', True)
PROD = os.getenv('WEB_PROD', False)
SERVER = os.getenv('WEB_SERVER', 'flask').lower() # gunicorn, cherrypy, flask
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if SERVER not in {'flask', 'cherrypy', 'gunicorn'}:
    raise RuntimeError('bad settings - server MUST be: flask, cherrypy, gunicorn')
if DEBUG and PROD:
    raise RuntimeError('bad settings - can NOT run production env with flask debug server')

# mongodb
DB = os.getenv('DB', 'home')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_USER = os.getenv('DB_USER', 'lylwm')
DB_PASS = os.getenv('DB_PASS', 'lylwmpwd')
