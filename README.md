<div align="center">

# 🕵️ WYR Stealth Scraper

**The most powerful open-source scraper for [wouldyourather.app](https://wouldyourather.app/) — bypass Cloudflare, scrape 17 categories, and build your own question database.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/ekanshbfoe/Would-You-Rather-questions-with-human-votes/pulls)
[![Stars](https://img.shields.io/github/stars/ekanshbfoe/Would-You-Rather-questions-with-human-votes?style=social)](https://github.com/ekanshbfoe/Would-You-Rather-questions-with-human-votes)

<br>

![demo](https://img.shields.io/badge/Interactive_CLI-InquirerPy_+_Rich-blueviolet?style=for-the-badge)

</div>

---

## ✨ Features

- 🛡️ **Cloudflare Bypass** — Uses `undetected-chromedriver` to strip all automation fingerprints
- 🎯 **17 Categories** — Daily, Money, Celebrity, Gross, Survival, School, Social, Deal with the Devil, NSFW, Food, Sports, Normal, Extreme, Fantasy, Hard, Love Life, Time Travel
- 🖥️ **Interactive CLI** — Beautiful terminal UI powered by `InquirerPy` and `rich` progress bars
- 🔄 **Auto-Save** — Saves every 10 questions so you never lose data mid-scrape
- ⛔ **Graceful Exit** — Press `CTRL+C` anytime to safely save and close the browser
- 🌐 **Proxy Support** — Optional residential proxy routing for repeated large-scale scrapes
- 🧹 **Built-in Data Pipeline** — Clean, deduplicate, and merge raw data with `migrate.py`

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/ekanshbfoe/Would-You-Rather-questions-with-human-votes.git
cd Would-You-Rather-questions-with-human-votes/Scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the interactive dashboard
python dashboard.py
```

You'll be prompted to:
1. **Select a category** (e.g., 🌶 NSFW, 💖 Love Life, 🏆 Sports...)
2. **Set target quantity** (e.g., 500 questions)
3. **Choose browser mode** (Headless or Visible)

The scraper launches, navigates to the category, and starts harvesting questions with a live progress bar.

---

## 🏗️ Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Browser Masking** | `undetected-chromedriver` | Strips automation flags, spoofs navigator, plugins, and languages |
| **Network Camouflage** | Residential Proxy (optional) | Masks origin IP through residential endpoints |
| **Behavioral Jitter** | `random.uniform()` delays | Mimics human reading speed and interaction timing |
| **DOM Parsing** | `BeautifulSoup` + `lxml` | Robust extraction from JS-rendered HTML |
| **Interactive UI** | `InquirerPy` + `rich` | Category selection, progress bars, and styled output |

---

## 🎯 Supported Categories

| # | Category | Output File |
|---|---|---|
| 1 | 🤔 Daily | `raw_daily.json` |
| 2 | 💰 Money | `raw_money.json` |
| 3 | 🎬 Celebrity | `raw_celebrity.json` |
| 4 | 🤢 Gross | `raw_gross.json` |
| 5 | 🏕 Survival | `raw_survival.json` |
| 6 | 🎓 School | `raw_school.json` |
| 7 | 💬 Social | `raw_social.json` |
| 8 | 😈 Deal with the Devil | `raw_deal_with_the_devil.json` |
| 9 | 🌶 NSFW | `raw_nsfw.json` |
| 10 | 🍕 Food | `raw_food.json` |
| 11 | 🏆 Sports | `raw_sports.json` |
| 12 | 📅 Normal | `raw_normal.json` |
| 13 | 🔥 Extreme | `raw_extreme.json` |
| 14 | 🔮 Fantasy | `raw_fantasy.json` |
| 15 | 🌀 Hard | `raw_hard.json` |
| 16 | 💖 Love Life | `raw_love_life.json` |
| 17 | ⏳ Time Travel | `raw_time_travel.json` |

---

## 📦 Output Schema

All scraped files are saved to `data/` with this JSON structure:

```json
[
  {
    "id": "celebrity_0001",
    "question": "Would you rather be known for a viral blooper or a viral dance trend?",
    "option_blue": "be known for a viral blooper",
    "option_red": "a viral dance trend",
    "global_votes_blue": 32,
    "global_votes_red": 68
  }
]
```

---

## 🧹 Data Pipeline (`migrate.py`)

After scraping, use the built-in migration tool to clean and merge your data:

```bash
python migrate.py
```

**What it does:**
1. **Filters** — Removes questions with 0/0 votes and empty text fields
2. **Deduplicates** — Checks against existing production data to prevent duplicates
3. **Re-Indexes** — Assigns clean sequential IDs (e.g., `celebrity_0201`, `celebrity_0202`...)
4. **Merges** — Appends new questions to your production JSON files
5. **Cleans Up** — Deletes the processed raw files from staging

```
Celebrity: Merged 180 new questions. Filtered 20 zeroes. Dropped 5 duplicates. New total: 385.
NSFW: Merged 210 new questions. Filtered 15 zeroes. Dropped 8 duplicates. New total: 467.
```

---

## 🌐 Proxy Configuration (Optional)

For large-scale scraping, configure a residential proxy in `config.py`:

```python
PROXY_HOST = "gate.smartproxy.com"
PROXY_PORT = "7000"
PROXY_USER = "spxxxx"
PROXY_PASS = "your_password"
```

**Recommended providers:** [Bright Data](https://brightdata.com/) · [Oxylabs](https://oxylabs.io/) · [Smartproxy](https://smartproxy.com/) · [IPRoyal](https://iproyal.com/)

> **Note:** The scraper works without a proxy for local testing, but you risk IP throttling on repeated runs.

---

## ⚙️ Tuning Parameters

All timing jitter is configurable in `config.py`:

| Parameter | Default | Purpose |
|---|---|---|
| `PAGE_LOAD_WAIT` | `(5.0, 9.0)` | Initial page load delay range (seconds) |
| `ACTION_DELAY` | `(2.5, 5.5)` | Delay before clicking an option |
| `SCROLL_DELAY` | `(1.8, 4.0)` | Delay between scrolling to next question |
| `VOTE_REVEAL_WAIT` | `(2.0, 4.0)` | Wait after voting for percentages to appear |

---

## 📁 File Structure

```
wyr-scraper/
├── dashboard.py        # Interactive CLI scraper (main entry point)
├── migrate.py          # Data cleaning & merge pipeline
├── config.py           # Proxy, browser, and timing configuration
├── requirements.txt    # Python dependencies
├── README.md
├── LICENSE
└── data/               # Scraped output (auto-created)
    ├── raw_celebrity.json
    ├── raw_nsfw.json
    └── ...
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use only**. Respect the website's Terms of Service and use responsibly. The authors are not responsible for any misuse.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**If this tool helped you, please consider giving it a ⭐ on GitHub!**

Made with ❤️ by [ACL](https://t.me/OceanHave)

</div>
