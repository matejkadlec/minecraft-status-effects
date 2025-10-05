#!/usr/bin/env python3
"""
Script to scrape individual effect pages from mcmod.cn
Extracts effect information from item-text, table-scroll, and comment-floor sections

Note: Comments are loaded dynamically via JavaScript, so this script uses Selenium
to wait for them to load. You need Chrome/Chromium installed for this to work.
"""

import requests
import sys
from bs4 import BeautifulSoup
import re
import json
import time


# Optional Selenium support for loading dynamic comments
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def clean_text(text):
    """Clean up text by removing extra whitespace and newlines"""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def extract_effect_name(soup):
    """Extract effect name from the page title or item-text section"""
    # Try to get from title first
    title = soup.find("title")
    if title and title.text:
        # Extract from title like "火焰引爆 (Flaming Detonation) - [apotheosis]神化 - MC百科|最大的Minecraft中文MOD百科"
        title_text = title.text
        match = re.search(r"(.+?)\s*-\s*\[(.+?)\]", title_text)
        if match:
            effect_part = match.group(1).strip()
            mod_part = match.group(2).strip()

            # Extract English name from parentheses
            english_match = re.search(r"\(([^)]+)\)$", effect_part)
            if english_match:
                english_name = english_match.group(1).strip()
                chinese_name = effect_part.replace(f"({english_name})", "").strip()
                return {
                    "chinese_name": chinese_name,
                    "english_name": english_name,
                    "mod_info": mod_part,
                }

    # Fallback to item-text section
    item_text = soup.find("div", class_="item-text")
    if item_text:
        itemname = item_text.find("div", class_="itemname")
        if itemname:
            name_span = itemname.find("span", class_="name")
            if name_span:
                h5 = name_span.find("h5")
                if h5:
                    name_text = clean_text(h5.get_text())
                    # Try to extract English from parentheses
                    english_match = re.search(r"\(([^)]+)\)$", name_text)
                    if english_match:
                        english_name = english_match.group(1).strip()
                        chinese_name = name_text.replace(
                            f"({english_name})", ""
                        ).strip()
                        return {
                            "chinese_name": chinese_name,
                            "english_name": english_name,
                            "mod_info": "",
                        }
                    return {
                        "chinese_name": name_text,
                        "english_name": "",
                        "mod_info": "",
                    }

    return {"chinese_name": "", "english_name": "", "mod_info": ""}


def extract_item_text_info(soup):
    """Extract information from the item-text div"""
    item_text = soup.find("div", class_="item-text")
    if not item_text:
        return {}

    info = {}

    # Extract command
    command_div = item_text.find("div", class_="item-give")
    if command_div:
        command_text = clean_text(command_div.get_text())
        info["command"] = command_text

        # Extract namespace from command (e.g., apotheosis:detonation)
        command_match = re.search(r"/effect give @p (\S+)", command_text)
        if command_match:
            effect_id = command_match.group(1)
            info["effect_id"] = effect_id
            if ":" in effect_id:
                mod_namespace = effect_id.split(":")[0]
                info["mod_namespace"] = mod_namespace

    # Extract classification (positive/negative)
    tables = item_text.find_all("table", class_="table table-bordered widetable")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                header = clean_text(cells[0].get_text())
                value = clean_text(cells[1].get_text())
                if "分类" in header or "classification" in header.lower():
                    info["classification"] = value
                elif "主要名称" in header or "main name" in header.lower():
                    info["main_name"] = value
                elif "次要名称" in header or "secondary name" in header.lower():
                    info["secondary_name"] = value

    # Extract description from item-content
    content_div = item_text.find("div", class_="item-content")
    if content_div:
        # Get all paragraphs
        paragraphs = content_div.find_all("p")
        descriptions = []
        for p in paragraphs:
            text = clean_text(p.get_text())
            if text:
                descriptions.append(text)
        info["description"] = " ".join(descriptions) if descriptions else ""

    return info


def extract_table_info(soup):
    """Extract information from table-scroll sections"""
    table_info = []

    # Look for table-scroll divs
    table_scrolls = soup.find_all("div", class_="table-scroll")
    for scroll_div in table_scrolls:
        table = scroll_div.find("table")
        if not table:
            continue

        # Extract headers
        header_row = table.find("tr")
        if not header_row:
            continue

        headers = []
        for th in header_row.find_all(["th", "td"]):
            headers.append(clean_text(th.get_text()))

        # Extract data rows
        rows = table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cells = row.find_all("td")
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_data[headers[i]] = clean_text(cell.get_text())
            if row_data:
                table_info.append(row_data)

    return table_info


def extract_comments(soup):
    """Extract user comments from comment-floor (static HTML fallback)"""
    comments = []

    comment_floor = soup.find("ul", class_="comment-floor")
    if not comment_floor:
        return comments

    comment_rows = comment_floor.find_all("li", class_="comment-row")
    for row in comment_rows:
        comment_data = {}

        # Extract username
        username_links = row.find_all("a", {"data-uid": True})
        if username_links:
            comment_data["username"] = clean_text(username_links[0].get_text())
            comment_data["uid"] = username_links[0].get("data-uid")

        # Extract comment text
        text_content = row.find("div", class_="comment-row-text-content")
        if text_content:
            comment_data["text"] = clean_text(text_content.get_text())

        # Extract timestamp
        time_element = row.find("li", class_="comment-reply-row-time")
        if time_element:
            comment_data["timestamp"] = clean_text(time_element.get_text())

        if comment_data:
            comments.append(comment_data)

    return comments


def extract_comments_with_selenium(url, timeout=10):
    """Extract comments using Selenium to wait for JavaScript to load them

    Optimized for speed with minimal wait times and disabled unnecessary features.
    """
    if not SELENIUM_AVAILABLE:
        print(
            "Warning: Selenium not available, skipping dynamic comment loading",
            file=sys.stderr,
        )
        return []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    # Disable images for faster loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for the comment block to appear (reduced timeout)
        try:
            comment_block = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "common-comment-block"))
            )

            # Scroll to the comment block to trigger lazy loading
            driver.execute_script("arguments[0].scrollIntoView(true);", comment_block)

            # Wait for comment-floor with explicit check (faster than time.sleep)
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "comment-floor"))
            )

            # Check if comments are actually present
            # If comment-floor exists but has no comment-row children, return immediately
            try:
                # Wait briefly for at least one comment to appear
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "comment-row"))
                )
                # Comments found, give them a moment to fully render
                time.sleep(0.5)
            except TimeoutException:
                # No comments found after 2 seconds, return immediately with empty list
                driver.quit()
                return []

        except TimeoutException:
            print("Warning: Timed out waiting for comments to load", file=sys.stderr)

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        driver.quit()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")
        return extract_comments(soup)

    except Exception as e:
        print(f"Warning: Error using Selenium: {e}", file=sys.stderr)
        try:
            driver.quit()
        except:
            pass
        return []


def determine_max_level(table_info, item_info, comments):
    """Determine max level from various sources"""
    max_level = 1

    # Check table info for effect levels (I, II, III, IV, V)
    roman_levels = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}

    for row in table_info:
        for key, value in row.items():
            if "等级" in key or "level" in key.lower():
                for roman, num in roman_levels.items():
                    if roman in value:
                        max_level = max(max_level, num)

    # Check command for level hints
    if "command" in item_info:
        # Look for level in command like "/effect give @p effect 30 2"
        command_match = re.search(
            r"/effect give @p \S+ \d+ (\d+)", item_info["command"]
        )
        if command_match:
            level_from_command = (
                int(command_match.group(1)) + 1
            )  # Command uses 0-based indexing
            max_level = max(max_level, level_from_command)

    return max_level


def determine_effect_type(item_info, comments):
    """Determine if effect is positive or negative"""
    # Check classification
    if "classification" in item_info:
        classification = item_info["classification"].lower()
        if "负面" in classification or "negative" in classification:
            return "negative"
        elif "正面" in classification or "positive" in classification:
            return "positive"

    # Look for keywords in description
    if "description" in item_info:
        desc = item_info["description"].lower()
        negative_keywords = [
            "伤害",
            "损伤",
            "减少",
            "damage",
            "harm",
            "reduce",
            "爆炸",
            "explode",
        ]
        positive_keywords = [
            "增加",
            "提升",
            "治疗",
            "increase",
            "boost",
            "heal",
            "benefit",
        ]

        negative_score = sum(1 for keyword in negative_keywords if keyword in desc)
        positive_score = sum(1 for keyword in positive_keywords if keyword in desc)

        if negative_score > positive_score:
            return "negative"
        elif positive_score > negative_score:
            return "positive"

    # Default fallback
    return "negative"  # Most mod effects tend to be negative/debuffs


def scrape_effect_page(url, use_selenium=True):
    """Main function to scrape an effect page

    Args:
        url: The URL of the effect page to scrape
        use_selenium: If True, use Selenium to load dynamic comments (recommended)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all information
        name_info = extract_effect_name(soup)
        item_info = extract_item_text_info(soup)
        table_info = extract_table_info(soup)

        # Try to load comments with Selenium (since they're loaded dynamically)
        comments = []
        if use_selenium and SELENIUM_AVAILABLE:
            comments = extract_comments_with_selenium(url)
        else:
            # Fallback: try static HTML parsing (likely won't work for dynamic comments)
            comments = extract_comments(soup)

        # Determine max level and type
        max_level = determine_max_level(table_info, item_info, comments)
        effect_type = determine_effect_type(item_info, comments)

        # Compile result
        result = {
            "url": url,
            "name_info": name_info,
            "item_info": item_info,
            "table_info": table_info,
            "comments": comments,
            "analysis": {"max_level": max_level, "effect_type": effect_type},
        }

        return result

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python scrape_effect.py <effect_url>")
        sys.exit(1)

    url = sys.argv[1]
    result = scrape_effect_page(url)

    if result:
        # Pretty print the result
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Failed to scrape effect page")
        sys.exit(1)


if __name__ == "__main__":
    main()
