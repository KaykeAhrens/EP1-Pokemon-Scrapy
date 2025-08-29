BOT_NAME = 'pokemon_scraper'

SPIDER_MODULES = ['pokemon_scraper.spiders']
NEWSPIDER_MODULE = 'pokemon_scraper.spiders'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = False

AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 5
CONCURRENT_REQUESTS_PER_DOMAIN = 16
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0

ITEM_PIPELINES = {
    'pokemon_scraper.pipelines.JsonPipeline': 300,
}

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

LOG_LEVEL = 'INFO'