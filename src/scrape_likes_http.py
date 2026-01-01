#!/usr/bin/env python3
"""
SoundCloud Likes Scraper using HTTP requests
Parses the initial page data without browser automation.
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
import requests

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_URL = "https://soundcloud.com/amr-farouk-10/likes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def extract_hydration_data(html):
    """Extract __sc_hydration data from HTML."""
    # Look for the hydration script
    pattern = r'<script>window\.__sc_hydration\s*=\s*(\[.*?\]);</script>'
    match = re.search(pattern, html, re.DOTALL)

    if match:
        try:
            data = json.loads(match.group(1))
            return data
        except json.JSONDecodeError:
            pass

    # Try alternative pattern
    pattern2 = r'window\.__sc_hydration\s*=\s*(\[[\s\S]*?\]);'
    match2 = re.search(pattern2, html)
    if match2:
        try:
            # Clean up the JSON string
            json_str = match2.group(1)
            # Fix common issues
            json_str = re.sub(r',\s*]', ']', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")

    return None


def extract_client_id(html):
    """Extract client_id from page."""
    patterns = [
        r'"clientId"\s*:\s*"([a-zA-Z0-9]+)"',
        r'client_id=([a-zA-Z0-9]+)',
        r'"client_id"\s*:\s*"([a-zA-Z0-9]+)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)

    return None


def fetch_api_v2(endpoint, client_id, params=None):
    """Fetch from SoundCloud API v2."""
    base_url = "https://api-v2.soundcloud.com"
    url = f"{base_url}{endpoint}"

    if params is None:
        params = {}
    params['client_id'] = client_id

    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API error: {response.status_code}")
        return None


def main():
    print("=" * 60)
    print("SoundCloud Likes Scraper (HTTP)")
    print("=" * 60)
    print(f"Target: {TARGET_URL}")

    session = requests.Session()
    session.headers.update(HEADERS)

    # Fetch the likes page
    print("\nFetching likes page...")
    response = session.get(TARGET_URL)

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return

    html = response.text
    print(f"Page size: {len(html)} bytes")

    # Extract hydration data
    print("\nExtracting embedded data...")
    hydration = extract_hydration_data(html)

    tracks = []

    if hydration:
        print(f"Found {len(hydration)} hydration entries")

        for entry in hydration:
            hydratable = entry.get('hydratable')

            if hydratable == 'user':
                user_data = entry.get('data', {})
                print(f"\nUser: {user_data.get('username')}")
                print(f"User ID: {user_data.get('id')}")
                print(f"Likes count: {user_data.get('likes_count')}")

            elif hydratable == 'playlist':
                # This might be a likes collection
                data = entry.get('data', {})
                collection = data.get('collection', data.get('tracks', []))

                for item in collection:
                    track = item.get('track', item) if isinstance(item, dict) else item
                    if isinstance(track, dict) and track.get('kind') == 'track':
                        tracks.append({
                            "title": track.get('title', 'Unknown'),
                            "artist": track.get('user', {}).get('username', 'Unknown'),
                            "artist_id": track.get('user', {}).get('id'),
                            "url": track.get('permalink_url'),
                            "duration_ms": track.get('duration'),
                            "duration": format_duration(track.get('duration')),
                            "plays": track.get('playback_count'),
                            "likes": track.get('likes_count'),
                            "genre": track.get('genre'),
                            "tag_list": track.get('tag_list', ''),
                            "description": (track.get('description') or '')[:500],
                            "created_at": track.get('created_at'),
                            "artwork_url": track.get('artwork_url'),
                            "track_id": track.get('id'),
                        })

            # Check for soundCollection (likes)
            elif hydratable in ['soundCollection', 'collection']:
                data = entry.get('data', {})
                collection = data.get('collection', [])

                for item in collection:
                    track = item.get('track', item)
                    if isinstance(track, dict) and track.get('kind') == 'track':
                        tracks.append({
                            "title": track.get('title', 'Unknown'),
                            "artist": track.get('user', {}).get('username', 'Unknown'),
                            "artist_id": track.get('user', {}).get('id'),
                            "url": track.get('permalink_url'),
                            "duration_ms": track.get('duration'),
                            "duration": format_duration(track.get('duration')),
                            "plays": track.get('playback_count'),
                            "likes": track.get('likes_count'),
                            "genre": track.get('genre'),
                            "tag_list": track.get('tag_list', ''),
                            "description": (track.get('description') or '')[:500],
                            "created_at": track.get('created_at'),
                            "artwork_url": track.get('artwork_url'),
                            "track_id": track.get('id'),
                            "liked_at": item.get('created_at'),
                        })
    else:
        print("No hydration data found")

        # Try to find tracks in JSON-LD or other embedded data
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        for match in re.finditer(json_ld_pattern, html, re.DOTALL):
            try:
                ld_data = json.loads(match.group(1))
                if isinstance(ld_data, dict) and ld_data.get('@type') == 'MusicRecording':
                    tracks.append({
                        "title": ld_data.get('name', 'Unknown'),
                        "artist": ld_data.get('byArtist', {}).get('name', 'Unknown'),
                        "url": ld_data.get('url'),
                        "duration": ld_data.get('duration'),
                    })
            except json.JSONDecodeError:
                continue

    # Remove duplicates
    seen = set()
    unique_tracks = []
    for track in tracks:
        key = track.get('url') or track.get('title')
        if key and key not in seen:
            seen.add(key)
            unique_tracks.append(track)

    # Save results
    output = {
        "source": TARGET_URL,
        "track_count": len(unique_tracks),
        "scraped_at": datetime.now().isoformat(),
        "tracks": unique_tracks
    }

    output_file = OUTPUT_DIR / "soundcloud_likes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"Scraped {len(unique_tracks)} tracks")
    print(f"Saved to: {output_file}")
    print("=" * 60)

    # Also save raw hydration for debugging
    if hydration:
        debug_file = OUTPUT_DIR / "soundcloud_hydration.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(hydration, f, ensure_ascii=False, indent=2)
        print(f"Debug data saved to: {debug_file}")

    return unique_tracks


def format_duration(ms):
    """Convert milliseconds to MM:SS format."""
    if not ms:
        return None
    seconds = ms // 1000
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


if __name__ == "__main__":
    main()
