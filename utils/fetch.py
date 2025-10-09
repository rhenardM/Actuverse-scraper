import requests
from requests.adapters import HTTPAdapter, Retry
from config.settings import USER_AGENT, REQUEST_TIMEOUT

def get_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': USER_AGENT,
        'Accept-Language': 'en-US,en;q=0.9'
    })
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(['GET', 'POST'])
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))
    s.mount('http://', HTTPAdapter(max_retries=retries))
    return s
