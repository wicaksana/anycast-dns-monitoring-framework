from flask import Flask

app = Flask(__name__)

import anycast_dns_monitoring.views