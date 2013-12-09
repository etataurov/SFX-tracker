import os
from urllib.parse import urlparse

LOGIN = os.getenv('POSTMARK_API_KEY')
PASSWORD = os.getenv('POSTMARK_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL')

SMTP_SERVER = os.getenv('POSTMARK_SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 2525))

redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redis_url = urlparse(redis_url)
REDIS_HOST = redis_url.hostname
REDIS_PORT = redis_url.port
REDIS_PASSWORD = redis_url.password

URL_TIMEOUT = int(os.getenv('URL_TIMEOUT', 60*60))
TIMEOUT = int(os.getenv('TIMEOUT', 10*60))
