import os
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv('API_URL', 'http://127.0.0.1:8001/api/articles')
USER_AGENT = os.getenv('USER_AGENT', 'ActuVerseScraper/1.0 (+https://actuverse.example)')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
DRY_RUN = False
