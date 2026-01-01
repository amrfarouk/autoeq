#!/usr/bin/env python3
"""
SoundCloud Likes Fetcher
Uses the discovered user ID to fetch likes via API v2.
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
import requests

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# User data from hydration
USER_ID = 57658459
USERNAME = "amrfarouk75"
LIKES_COUNT = 316

# API endpoints
API_V2 = "https://api-v2.soundcloud.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://soundcloud.com/",
    "Origin": "https://soundcloud.com",
}


def get_client_id():
    """Extract client_id from SoundCloud page scripts."""
    print("Extracting client_id...")

    # Fetch the main page
    response = requests.get("https://soundcloud.com", headers=HEADERS)
    html = response.text

    # Find script URLs
    script_pattern = r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"'
    scripts = re.findall(script_pattern, html)

    print(f"Found {len(scripts)} script files to check...")

    for script_url in scripts[:10]:  # Check first 10 scripts
        try:
            script_response = requests.get(script_url, headers=HEADERS, timeout=10)
            script_content = script_response.text

            # Look for client_id patterns
            patterns = [
                r'client_id:\s*"([a-zA-Z0-9]{32})"',
                r'"client_id":\s*"([a-zA-Z0-9]{32})"',
                r'clientId:\s*"([a-zA-Z0-9]{32})"',
                r'\?client_id=([a-zA-Z0-9]{32})',
            ]

            for pattern in patterns:
                match = re.search(pattern, script_content)
                if match:
                    client_id = match.group(1)
                    # Validate by making a test request
                    test_url = f"{API_V2}/resolve?url=https://soundcloud.com/soundcloud&client_id={client_id}"
                    test_response = requests.get(test_url, headers=HEADERS, timeout=5)
                    if test_response.status_code == 200:
                        print(f"Found valid client_id: {client_id[:8]}...")
                        return client_id
        except Exception as e:
            continue

    raise Exception("Could not find valid client_id")


def fetch_likes(user_id, client_id, limit=200, max_tracks=5000):
    """Fetch liked tracks for a user, up to max_tracks."""
    all_tracks = []
    offset = 0
    page = 1

    while len(all_tracks) < max_tracks:
        url = f"{API_V2}/users/{user_id}/likes"
        params = {
            "client_id": client_id,
            "limit": limit,
            "offset": offset,
            "linked_partitioning": 1,
        }

        print(f"Fetching page {page} (offset {offset})...")

        response = requests.get(url, params=params, headers=HEADERS)

        if response.status_code == 401:
            print("Unauthorized - client_id may be invalid")
            break
        elif response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            print(response.text[:500])
            break

        data = response.json()
        collection = data.get("collection", [])

        if not collection:
            print("No more items in collection")
            break

        for item in collection:
            track = item.get("track")
            if track:
                all_tracks.append({
                    "title": track.get("title", "Unknown"),
                    "artist": track.get("user", {}).get("username", "Unknown"),
                    "artist_id": track.get("user", {}).get("id"),
                    "url": track.get("permalink_url"),
                    "duration_ms": track.get("duration"),
                    "duration": format_duration(track.get("duration")),
                    "plays": track.get("playback_count"),
                    "likes": track.get("likes_count"),
                    "reposts": track.get("reposts_count"),
                    "comments": track.get("comment_count"),
                    "genre": track.get("genre"),
                    "tag_list": track.get("tag_list", ""),
                    "description": (track.get("description") or "")[:500],
                    "created_at": track.get("created_at"),
                    "artwork_url": track.get("artwork_url"),
                    "waveform_url": track.get("waveform_url"),
                    "track_id": track.get("id"),
                    "liked_at": item.get("created_at"),
                })

        print(f"  Collected {len(all_tracks)} tracks total")

        # Check for next page
        next_href = data.get("next_href")
        if not next_href:
            print("No more pages")
            break

        offset += limit
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
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def resolve_user(username, client_id):
    """Resolve username to user ID"""
    url = f"{API_V2}/resolve"
    params = {"url": f"https://soundcloud.com/{username}", "client_id": client_id}
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_all_likes(username="amr-farouk-10", max_tracks=10000, output_dir=None):
    """Main function to fetch all likes for a username"""
    print("=" * 60)
    print("SoundCloud Likes Fetcher")
    print("=" * 60)

    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = OUTPUT_DIR
    out_dir.mkdir(exist_ok=True)

    try:
        # Get client_id
        client_id = get_client_id()

        # Resolve username to user ID
        print(f"\nResolving user: {username}")
        user_data = resolve_user(username, client_id)
        if not user_data:
            # Fallback to known user
            user_id = USER_ID
            resolved_username = USERNAME
        else:
            user_id = user_data.get("id", USER_ID)
            resolved_username = user_data.get("username", username)

        print(f"User ID: {user_id}")

        # Fetch likes
        print(f"\nFetching liked tracks (max {max_tracks})...")
        tracks = fetch_likes(user_id, client_id, max_tracks=max_tracks)

        # Save results
        output = {
            "source": f"https://soundcloud.com/{resolved_username}/likes",
            "user_id": user_id,
            "username": resolved_username,
            "track_count": len(tracks),
            "scraped_at": datetime.now().isoformat(),
            "tracks": tracks
        }

        output_file = out_dir / "soundcloud_likes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(f"SUCCESS: Collected {len(tracks)} liked tracks")
        print(f"Output: {output_file}")
        print("=" * 60)

        return output

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"tracks": [], "track_count": 0}


def main():
    return fetch_all_likes()


if __name__ == "__main__":
    main()
