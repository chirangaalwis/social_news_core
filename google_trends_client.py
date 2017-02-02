import os
import sys
from pytrends.request import TrendReq

def get_pytrends():

    try:
        google_username = os.environ['GOOGLE_USERNAME']
        google_password = os.environ['GOOGLE_SECRET']
    except KeyError:
        sys.stderr.write("GOOGLE_* environment variables not set\n")
        sys.exit(1)

    pytrends = TrendReq(google_username, google_password, custom_useragent=None)

    return pytrends
