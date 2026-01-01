#!/usr/bin/env python3
"""
SoundCloud Likes Scraper using API v2
More reliable than browser-based scraping.
"""

import json
import time
import re
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, quote

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# SoundCloud API configuration
BASE_API = "https://api-v2.soundcloud.com"
USER_PROFILE = "amr-farouk-10"

def get_client_id():
    """Extract client_id from SoundCloud's main page."""
    print("Extracting client_id from SoundCloud...")

    # Try to get client_id from the main page
    response = requests.get(
        "https://soundcloud.com",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    )

    # Look for client_id in script tags
    matches = re.findall(r'client_id["\s:=]+([a-zA-Z0-9]{32})', response.text)
    if matches:
        client_id = matches[0]
        print(f"Found client_id: {client_id[:8]}...")
        return client_id

    # Try fetching one of the JS bundles
    js_urls = re.findall(r'https://[^"]+\.js', response.text)
    for js_url in js_urls[:5]:
        try:
            js_response = requests.get(js_url, timeout=10)
            js_matches = re.findall(r'client_id["\s:=]+["\']?([a-zA-Z0-9]{32})["\']?', js_response.text)
            if js_matches:
                client_id = js_matches[0]
                print(f"Found client_id in JS: {client_id[:8]}...")
                return client_id
        except:
            continue

    # Known working client_ids (may expire)
    known_ids = [
        "iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX",
        "a3e059563d7fd3372b49b37f00a00bcf",
    ]

    for cid in known_ids:
        test_url = f"{BASE_API}/users?q=test&client_id={cid}"
        try:
            resp = requests.get(test_url, timeout=5)
            if resp.status_code == 200:
                print(f"Using known client_id: {cid[:8]}...")
                return cid
        except:
            continue

    raise Exception("Could not find valid client_id")


def resolve_user(username, client_id):
    """Resolve username to user ID."""
    url = f"{BASE_API}/resolve"
    params = {
        "url": f"https://soundcloud.com/{username}",
        "client_id": client_id
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        raise Exception(f"Could not resolve user: {response.status_code}")


def get_user_likes(user_id, client_id, limit=200):
    """Fetch all liked tracks for a user."""
    all_tracks = []
    next_href = f"{BASE_API}/users/{user_id}/likes?client_id={client_id}&limit={limit}"

    page = 1
    while next_href:
        print(f"Fetching page {page}...")

        response = requests.get(next_href)
        if response.status_code != 200:
            print(f"Error fetching likes: {response.status_code}")
            break

        data = response.json()
        collection = data.get("collection", [])

        for item in collection:
            # Each item has a "track" or "playlist" key
            track = item.get("track")
            if track:
                all_tracks.append({
                    "title": track.get("title", "Unknown"),
                    "artist": track.get("user", {}).get("username", "Unknown"),
                    "artist_id": track.get("user", {}).get("id"),
                    "url": track.get("permalink_url"),
                    "duration_ms": track.get("duration"),
                    "duration": format_duration(track.get("duration", 0)),
                    "plays": track.get("playback_count"),
                    "likes": track.get("likes_count"),
                    "reposts": track.get("reposts_count"),
                    "comments": track.get("comment_count"),
                    "genre": track.get("genre"),
                    "tag_list": track.get("tag_list", ""),
                    "description": track.get("description", "")[:500] if track.get("description") else None,
                    "created_at": track.get("created_at"),
                    "artwork_url": track.get("artwork_url"),
                    "waveform_url": track.get("waveform_url"),
                    "track_id": track.get("id"),
                    "liked_at": item.get("created_at"),
                })

        print(f"  Collected {len(all_tracks)} tracks so far")

        # Get next page URL
        next_href = data.get("next_href")
        if next_href and "client_id" not in next_href:
            next_href += f"&client_id={client_id}"

        page += 1
        time.sleep(0.5)  # Rate limiting

    return all_tracks


def format_duration(ms):
    """Convert milliseconds to MM:SS format."""
    if not ms:
        return None
    seconds = ms // 1000
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def save_tracks(tracks, filename="soundcloud_likes.json"):
    """Save tracks to JSON file."""
    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "source": f"https://soundcloud.com/{USER_PROFILE}/likes",
            "track_count": len(tracks),
            "scraped_at": datetime.now().isoformat(),
            "tracks": tracks
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(tracks)} tracks to {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("SoundCloud Likes Scraper (API v2)")
    print("=" * 60)

    try:
        # Get client_id
        client_id = get_client_id()

        # Resolve user
        print(f"\nResolving user: {USER_PROFILE}")
        user_data = resolve_user(USER_PROFILE, client_id)
        user_id = user_data.get("id")
        print(f"User ID: {user_id}")
        print(f"Username: {user_data.get('username')}")
        print(f"Followers: {user_data.get('followers_count')}")
        print(f"Likes count: {user_data.get('likes_count', 'N/A')}")

        # Fetch likes
        print(f"\nFetching liked tracks...")
        tracks = get_user_likes(user_id, client_id)

        # Save results
        output_file = save_tracks(tracks)

        print("\n" + "=" * 60)
        print(f"SUCCESS: Collected {len(tracks)} liked tracks")
        print(f"Output: {output_file}")
        print("=" * 60)

        return tracks

    except Exception as e:
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
