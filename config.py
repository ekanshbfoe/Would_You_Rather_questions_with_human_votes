# ============================================================================
#  WYR Stealth Scraper — config.py
#  Central configuration for proxy, browser, and scraping parameters.
# ============================================================================

# ---------------------------------------------------------------------------
#  PROXY CONFIGURATION
#  Fill these in with your residential proxy credentials.
#  Leave PROXY_HOST as "" to disable proxy routing entirely (for local testing).
#
#  Recommended providers: Bright Data, Oxylabs, Smartproxy, IPRoyal
#  Example:
#      PROXY_HOST = "gate.smartproxy.com"
#      PROXY_PORT = "7000"
#      PROXY_USER = "spxxxx"
#      PROXY_PASS = "your_password"
# ---------------------------------------------------------------------------
PROXY_HOST = ""          # e.g. "gate.smartproxy.com"
PROXY_PORT = ""          # e.g. "7000"
PROXY_USER = ""          # e.g. "spxxxx"
PROXY_PASS = ""          # e.g. "your_password"


# ---------------------------------------------------------------------------
#  BROWSER CONFIGURATION
# ---------------------------------------------------------------------------
HEADLESS_MODE = False     # Set True for cloud/server deployment, False for local debugging
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
#  SCRAPING PARAMETERS
# ---------------------------------------------------------------------------
TARGET_URL         = "https://wouldyourather.app/"
MAX_QUESTIONS      = 100          # How many questions to scrape before stopping
PAGE_LOAD_WAIT     = (5.0, 9.0)   # Random wait (min, max) seconds for initial page load
ACTION_DELAY       = (2.5, 5.5)   # Random wait between clicking / scrolling actions
SCROLL_DELAY       = (1.8, 4.0)   # Random wait between scroll-to-next-question
VOTE_REVEAL_WAIT   = (2.0, 4.0)   # Wait after voting to let percentage animation finish
OUTPUT_FILE        = "data/questions_sfw.json"
