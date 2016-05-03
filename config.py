# define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

# define the database

# application threads. A common general assumption is using 2 per available processor cores. To handle incoming requests
# using one and performing background operations using the other
THREADS_PER_PAGE = 2

# enable protection againts CSRF
CSRF_ENABLED = True

# using a secure, unique, and absolutely secret key for signing the data
CSRF_SESSION_KEY = 'secret'

# secret key for signing cookies
SECRET_KEY = 'secret'
