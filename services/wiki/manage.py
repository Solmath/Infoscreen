from moin.app import create_app
from waitress import serve
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

application = create_app('./INSTANCE-DIRECTORY/wikiconfig.py')

if __name__ == "__main__":
    serve(application)
