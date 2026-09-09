#!/usr/bin/env python3
# ============================================================================
#  WYR Stealth Scraper — dashboard.py
# ============================================================================

import json
import os
import random
import sys
import time
import logging
from pathlib import Path
import subprocess
import re

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

from InquirerPy import inquirer
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.console import Console

from config import (
    PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS,
    USER_AGENT, TARGET_URL,
    PAGE_LOAD_WAIT, ACTION_DELAY, SCROLL_DELAY, VOTE_REVEAL_WAIT,
)

console = Console()

# ---------------------------------------------------------------------------
#  CATEGORY MAPPING
# ---------------------------------------------------------------------------
CATEGORIES = {
    "🤔 Daily": {"text": "Daily", "file": "raw_daily.json", "prefix": "daily_"},
    "💰 Money": {"text": "Money", "file": "raw_money.json", "prefix": "money_"},
    "🎬 Celebrity": {"text": "Celebrity", "file": "raw_celebrity.json", "prefix": "celebrity_"},
    "🤢 Gross": {"text": "Gross", "file": "raw_gross.json", "prefix": "gross_"},
    "🏕 Survival": {"text": "Survival", "file": "raw_survival.json", "prefix": "survival_"},
    "🎓 School": {"text": "School", "file": "raw_school.json", "prefix": "school_"},
    "💬 Social": {"text": "Social", "file": "raw_social.json", "prefix": "social_"},
    "😈 Deal with the Devil": {"text": "Deal with the Devil", "file": "raw_deal_with_the_devil.json", "prefix": "devil_"},
    "🌶 NSFW": {"text": "NSFW", "file": "raw_nsfw.json", "prefix": "nsfw_"},
    "🍕 Food": {"text": "Food", "file": "raw_food.json", "prefix": "food_"},
    "🏆 Sports": {"text": "Sports", "file": "raw_sports.json", "prefix": "sports_"},
    "📅 Normal": {"text": "Normal", "file": "raw_normal.json", "prefix": "normal_"},
    "🔥 Extreme": {"text": "Extreme", "file": "raw_extreme.json", "prefix": "extreme_"},
    "🔮 Fantasy": {"text": "Fantasy", "file": "raw_fantasy.json", "prefix": "fantasy_"},
    "🌀 Hard": {"text": "Hard", "file": "raw_hard.json", "prefix": "hard_"},
    "💖 Love Life": {"text": "Love Life", "file": "raw_love_life.json", "prefix": "love_"},
    "⏳ Time Travel": {"text": "Time Travel", "file": "raw_time_travel.json", "prefix": "time_"},
}

# ---------------------------------------------------------------------------
#  LOGGING (Only warning+ for stealth, rich progress handles stdout)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("wyr-dashboard")

# ═══════════════════════════════════════════════════════════════════════════
#  1.  HUMAN-LIKE DELAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def human_delay(bounds: tuple[float, float]) -> None:
    time.sleep(random.uniform(*bounds))

# ═══════════════════════════════════════════════════════════════════════════
#  2.  BROWSER FACTORY
# ═══════════════════════════════════════════════════════════════════════════
def detect_chrome_version() -> int | None:
    reg_paths = [
        r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon",
    ]
    for reg_path in reg_paths:
        try:
            result = subprocess.run(
                ["reg", "query", reg_path, "/v", "version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                match = re.search(r"(\d+)\.\d+\.\d+\.\d+", result.stdout)
                if match:
                    return int(match.group(1))
        except Exception:
            continue

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True, text=True, timeout=10
                )
                match = re.search(r"(\d+)\.\d+\.\d+\.\d+", result.stdout)
                if match:
                    return int(match.group(1))
            except Exception:
                continue

    return None

def create_stealth_browser(headless: bool) -> uc.Chrome:
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    options.add_argument(f"--user-agent={USER_AGENT}")

    if PROXY_HOST and PROXY_PORT:
        options.add_argument(f"--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}")

    chrome_major = detect_chrome_version()
    driver = uc.Chrome(
        options=options,
        use_subprocess=True,
        version_main=chrome_major,
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """
        },
    )
    return driver

# ═══════════════════════════════════════════════════════════════════════════
#  3.  DOM PARSING & INTERACTION
# ═══════════════════════════════════════════════════════════════════════════
def _parse_percentage(el) -> int:
    if el is None: return 0
    text = el.get_text(strip=True).replace("%", "").replace(",", "").strip()
    try:
        return int(text)
    except (ValueError, TypeError):
        return 0

def parse_visible_statements(page_source: str, prefix: str) -> list[dict]:
    soup = BeautifulSoup(page_source, "lxml")
    results = []
    statements = soup.select("div.statement, .statement") or soup.select("[class*='statement']")

    for stmt in statements:
        try:
            option_els = stmt.select(".option-text-wrapper h2") or stmt.select(".option h2") or stmt.select("h2")
            if len(option_els) < 2: continue

            option_blue = option_els[0].get_text(strip=True)
            option_red = option_els[1].get_text(strip=True)
            if not option_blue or not option_red: continue

            pct_els = stmt.select(".percentage")
            votes_blue = _parse_percentage(pct_els[0]) if len(pct_els) > 0 else 0
            votes_red = _parse_percentage(pct_els[1]) if len(pct_els) > 1 else 0

            results.append({
                "id": f"{prefix}{random.randint(1000, 999999)}",
                "question": f"Would you rather {option_blue} or {option_red}?",
                "option_blue": option_blue,
                "option_red": option_red,
                "global_votes_blue": votes_blue,
                "global_votes_red": votes_red,
            })
        except Exception:
            continue
    return results

def vote_on_current_question(driver: uc.Chrome) -> bool:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".statement.active .option")))
        options = driver.find_elements(By.CSS_SELECTOR, ".statement.active .option") or driver.find_elements(By.CSS_SELECTOR, ".option")
        if len(options) < 2: return False

        target = random.choice(options[:2])
        human_delay(ACTION_DELAY)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", target)
        human_delay(VOTE_REVEAL_WAIT)
        return True
    except Exception:
        return False

def scroll_to_next_question(driver: uc.Chrome) -> bool:
    try:
        human_delay(SCROLL_DELAY)
        driver.execute_script("""
            const wrapper = document.querySelector('.statements-wrapper');
            if (wrapper) wrapper.scrollBy({ top: window.innerHeight, behavior: 'smooth' });
            else window.scrollTo(0, document.body.scrollHeight);
        """)
        human_delay((2.0, 4.0))
        return True
    except Exception:
        return False

def dismiss_overlays(driver: uc.Chrome) -> None:
    selectors = [".banner", "[class*='cookie']", "[class*='consent']", "[class*='overlay']", ".modal"]
    for sel in selectors:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    driver.execute_script("arguments[0].remove();", el)
        except Exception:
            pass

def save_to_json(questions: list[dict], filepath: str, prefix: str) -> None:
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for idx, q in enumerate(questions, start=1):
        q["id"] = f"{prefix}{idx:04d}"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════════════════
#  4.  MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def main():
    console.print("[bold blue]🚀 Would You Rather — Scraper Dashboard[/bold blue]")
    
    # 1. Interactive Prompts
    category_label = inquirer.select(
        message="Select target category:",
        choices=list(CATEGORIES.keys()),
    ).execute()
    
    target_qty_str = inquirer.number(
        message="Target Quantity:",
        min_allowed=1,
        max_allowed=100000,
        default=500,
    ).execute()
    target_qty = int(target_qty_str)
    
    mode = inquirer.select(
        message="Browser Mode:",
        choices=["Headless", "Visible"],
        default="Visible"
    ).execute()
    
    cat_data = CATEGORIES[category_label]
    output_file = f"data/{cat_data['file']}"
    
    console.print(f"\n[bold green]Configuration Loaded![/bold green]")
    console.print(f" • Category : {category_label}")
    console.print(f" • Target   : {target_qty} questions")
    console.print(f" • Output   : {output_file}")
    console.print(f" • Mode     : {mode}\n")
    
    all_questions = []
    seen_options = set()
    driver = None
    consecutive_failures = 0
    MAX_FAILURES = 5

    try:
        console.print("[yellow]Launching browser and bypassing anti-bot...[/yellow]")
        driver = create_stealth_browser(headless=(mode == "Headless"))
        
        driver.get(TARGET_URL)
        human_delay(PAGE_LOAD_WAIT)
        
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".statements-wrapper")))
        except TimeoutException:
            console.print("[red]❌ Timed out waiting for page. Possible Cloudflare block.[/red]")
            return
            
        dismiss_overlays(driver)
        
        # Navigate Category
        if category_label != "🤔 Daily":
            console.print(f"[yellow]Navigating to '{category_label}'...[/yellow]")
            burger_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".burger-menu")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", burger_menu)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", burger_menu)
            time.sleep(2)
            
            # Use XPath to find the correct category text
            cat_xpath = f"//li[contains(., '{cat_data['text']}')]"
            cat_option = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, cat_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cat_option)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", cat_option)
            time.sleep(3) # Wait for deck to mount

        console.print("[green]Ready to scrape![/green]")
        
        # Progress Bar setup
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping...", total=target_qty)
            
            while len(all_questions) < target_qty:
                voted = vote_on_current_question(driver)
                if not voted:
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_FAILURES:
                        progress.console.print("[red]❌ Too many consecutive failures. Aborting.[/red]")
                        break
                    scroll_to_next_question(driver)
                    continue

                parsed = parse_visible_statements(driver.page_source, cat_data['prefix'])
                new_count = 0
                for q in parsed:
                    dedup = f"{q['option_blue']}||{q['option_red']}"
                    if dedup not in seen_options:
                        seen_options.add(dedup)
                        all_questions.append(q)
                        new_count += 1
                
                if new_count > 0:
                    consecutive_failures = 0
                    progress.update(task, advance=new_count)
                    
                    # Auto-save chunk
                    if len(all_questions) % 10 == 0 or len(all_questions) >= target_qty:
                        save_to_json(all_questions, output_file, cat_data['prefix'])
                else:
                    consecutive_failures += 1
                    
                if consecutive_failures >= MAX_FAILURES:
                    progress.console.print("[red]❌ Too many consecutive failures (No new questions). Aborting.[/red]")
                    break

                scroll_to_next_question(driver)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]⛔ Interrupted by user — Gracefully stopping...[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]💥 Unexpected error: {e}[/bold red]")
    finally:
        if len(all_questions) > 0:
            save_to_json(all_questions, output_file, cat_data['prefix'])
            console.print(f"[bold green]💾 Final Save: {len(all_questions)} questions saved to {output_file}[/bold green]")
        
        if driver:
            try:
                driver.quit()
            except:
                pass
            console.print("[dim]Browser closed.[/dim]")

if __name__ == "__main__":
    # Ensure working directory is Scraper
    if os.path.basename(os.getcwd()) != "Scraper":
        # Check if Scraper exists in cwd
        if os.path.isdir("Scraper"):
            os.chdir("Scraper")
    main()
