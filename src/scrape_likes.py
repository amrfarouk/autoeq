#!/usr/bin/env python3
"""
SoundCloud Likes Scraper using Playwright
Scrapes directly from the browser with proper rendering.
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_URL = "https://soundcloud.com/amr-farouk-10/likes"


def parse_duration(duration_str):
    """Parse duration string like '3:45' to seconds."""
    if not duration_str:
        return None
    parts = duration_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return None


def main():
    print("=" * 60)
    print("SoundCloud Likes Scraper")
    print("=" * 60)
    print(f"Target: {TARGET_URL}")

    with sync_playwright() as p:
        # Launch browser in headed mode to avoid crashes
        print("\nLaunching browser...")
        browser = p.chromium.launch(
            headless=False,  # Visible browser
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        # Navigate to likes page
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, timeout=60000)

        # Wait for initial content
        print("Waiting for content to load...")
        time.sleep(5)

        # Try to find any track elements
        tracks = []
        seen_urls = set()
        last_count = 0
        no_change_count = 0

        print("Starting to scroll and collect tracks...")

        for scroll_num in range(100):
            # Get page HTML and parse tracks
            html = page.content()

            # Find all track links with titles
            # SoundCloud uses various structures, let's try to find tracks
            track_links = page.query_selector_all('a.soundTitle__title, a[class*="trackItem__trackTitle"]')

            for link in track_links:
                try:
                    href = link.get_attribute('href')
                    title = link.inner_text().strip()

                    if href and href not in seen_urls and title:
                        full_url = f"https://soundcloud.com{href}" if not href.startswith('http') else href

                        # Get artist - try to find nearby username element
                        artist = "Unknown"
                        parent = link.evaluate('el => el.closest(".soundList__item, .sound")')
                        if parent:
                            artist_el = page.query_selector(f'[data-item] a.soundTitle__username')

                        # Try to find artist from the URL
                        if '/' in href:
                            parts = href.strip('/').split('/')
                            if len(parts) >= 1:
                                artist = parts[0]

                        tracks.append({
                            "title": title,
                            "artist": artist,
                            "url": full_url,
                            "scraped_at": datetime.now().isoformat()
                        })
                        seen_urls.add(href)

                except Exception as e:
                    continue

            print(f"Scroll {scroll_num + 1}: {len(tracks)} tracks found")

            if len(tracks) == last_count:
                no_change_count += 1
                if no_change_count >= 5:
                    print("No new tracks found after 5 scrolls, stopping.")
                    break
            else:
                no_change_count = 0
                last_count = len(tracks)

            # Scroll down
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Try alternative approach: intercept network requests
        print("\nAttempting to extract from page data...")

        # Look for embedded JSON data
        scripts = page.query_selector_all('script')
        for script in scripts:
            try:
                text = script.inner_text()
                if 'collection' in text and 'track' in text:
                    # Try to parse as JSON
                    matches = re.findall(r'\{[^{}]*"kind"\s*:\s*"track"[^{}]*\}', text)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if data.get('permalink_url') and data['permalink_url'] not in seen_urls:
                                tracks.append({
                                    "title": data.get('title', 'Unknown'),
                                    "artist": data.get('user', {}).get('username', 'Unknown'),
                                    "url": data.get('permalink_url'),
                                    "duration": data.get('duration'),
                                    "genre": data.get('genre'),
                                    "plays": data.get('playback_count'),
                                    "scraped_at": datetime.now().isoformat()
                                })
                                seen_urls.add(data['permalink_url'])
                        except:
                            continue
            except:
                continue

        # Save results
        output = {
            "source": TARGET_URL,
            "track_count": len(tracks),
            "scraped_at": datetime.now().isoformat(),
            "tracks": tracks
        }

        output_file = OUTPUT_DIR / "soundcloud_likes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(f"Scraped {len(tracks)} tracks")
        print(f"Saved to: {output_file}")
        print("=" * 60)

        # Take screenshot for debugging
        screenshot_path = OUTPUT_DIR / "soundcloud_screenshot.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")

        browser.close()

        return tracks


if __name__ == "__main__":
    main()
