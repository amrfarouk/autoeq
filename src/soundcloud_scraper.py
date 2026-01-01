#!/usr/bin/env python3
"""
SoundCloud Likes Scraper
Scrapes all liked tracks from a SoundCloud user profile and extracts metadata.
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
TARGET_URL = "https://soundcloud.com/amr-farouk-10/likes"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_track_data(track_element):
    """Extract metadata from a single track element."""
    try:
        # Track title
        title_el = track_element.query_selector('.soundTitle__title')
        title = title_el.inner_text().strip() if title_el else "Unknown"

        # Track URL
        link_el = track_element.query_selector('a.soundTitle__title')
        track_url = link_el.get_attribute('href') if link_el else None
        if track_url and not track_url.startswith('http'):
            track_url = f"https://soundcloud.com{track_url}"

        # Artist name
        artist_el = track_element.query_selector('.soundTitle__username')
        artist = artist_el.inner_text().strip() if artist_el else "Unknown"

        # Duration (if visible)
        duration_el = track_element.query_selector('.playbackTimeline__duration span:last-child')
        duration = duration_el.inner_text().strip() if duration_el else None

        # Play count
        plays_el = track_element.query_selector('.sc-ministats-item[title*="plays"] span:last-child, .soundStats__plays')
        plays = plays_el.inner_text().strip() if plays_el else None

        # Genre/tags (from badge if visible)
        genre_el = track_element.query_selector('.sc-tag')
        genre = genre_el.inner_text().strip() if genre_el else None

        return {
            "title": title,
            "artist": artist,
            "url": track_url,
            "duration": duration,
            "plays": plays,
            "genre": genre,
            "scraped_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error extracting track: {e}")
        return None


def scroll_and_collect(page, max_scrolls=100, scroll_pause=2):
    """Scroll the page and collect all track elements."""
    tracks = []
    seen_urls = set()
    last_height = 0
    no_new_content_count = 0

    print("Starting to scroll and collect tracks...")

    for scroll_num in range(max_scrolls):
        # Get current track elements
        track_elements = page.query_selector_all('.soundList__item, .sound.streamContext')

        new_tracks_count = 0
        for el in track_elements:
            track_data = extract_track_data(el)
            if track_data and track_data.get('url') and track_data['url'] not in seen_urls:
                seen_urls.add(track_data['url'])
                tracks.append(track_data)
                new_tracks_count += 1

        print(f"Scroll {scroll_num + 1}: Found {len(tracks)} total tracks ({new_tracks_count} new)")

        # Scroll down
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(scroll_pause)

        # Check if we've reached the bottom
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            no_new_content_count += 1
            if no_new_content_count >= 3:
                print("Reached end of page (no new content after 3 scrolls)")
                break
        else:
            no_new_content_count = 0

        last_height = new_height

        # Save progress periodically
        if scroll_num % 10 == 0 and tracks:
            save_progress(tracks)

    return tracks


def save_progress(tracks):
    """Save current progress to file."""
    output_file = OUTPUT_DIR / "soundcloud_likes_progress.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "track_count": len(tracks),
            "last_updated": datetime.now().isoformat(),
            "tracks": tracks
        }, f, ensure_ascii=False, indent=2)
    print(f"Progress saved: {len(tracks)} tracks")


def main():
    print(f"Starting SoundCloud Likes Scraper")
    print(f"Target: {TARGET_URL}")
    print(f"Output: {OUTPUT_DIR}")
    print("-" * 50)

    with sync_playwright() as p:
        # Launch browser (headless for speed, set to False to debug)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Navigate to likes page
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

        # Wait for content to load
        print("Waiting for content to load...")
        try:
            page.wait_for_selector('.soundList__item, .sound.streamContext', timeout=30000)
        except:
            print("Warning: Could not find track elements with expected selectors")
            # Try alternative selectors
            page.wait_for_selector('.soundList, .userStream', timeout=30000)

        # Collect all tracks
        tracks = scroll_and_collect(page)

        # Save final results
        output_file = OUTPUT_DIR / "soundcloud_likes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "source_url": TARGET_URL,
                "track_count": len(tracks),
                "scraped_at": datetime.now().isoformat(),
                "tracks": tracks
            }, f, ensure_ascii=False, indent=2)

        print("-" * 50)
        print(f"Scraping complete!")
        print(f"Total tracks collected: {len(tracks)}")
        print(f"Output saved to: {output_file}")

        browser.close()

    return tracks


if __name__ == "__main__":
    main()
