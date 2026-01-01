#!/usr/bin/env python3
"""
Dynamic AI-Powered Track Clustering using Groq LLM
Analyzes track metadata and creates intelligent music clusters
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import requests

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-70b-versatile"

def get_groq_api_key() -> str:
    """Get Groq API key from environment or file"""
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key

    # Try reading from .env file
    env_paths = [".env", "../.env", os.path.expanduser("~/.groq_api_key")]
    for path in env_paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.startswith("GROQ_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"\'')

    raise ValueError("GROQ_API_KEY not found in environment or .env file")


def call_groq(prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
    """Call Groq API with retry logic"""
    api_key = get_groq_api_key()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    for attempt in range(3):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  Groq API attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)

    raise Exception("Groq API failed after 3 attempts")


def analyze_track_batch(tracks: List[Dict], batch_num: int) -> Dict[str, Any]:
    """Analyze a batch of tracks using Groq to identify genre/mood patterns"""

    # Prepare track summaries for analysis
    track_summaries = []
    for t in tracks[:50]:  # Limit batch size for API
        summary = {
            "title": t.get("title", "")[:100],
            "artist": t.get("artist", "")[:50],
            "genre": t.get("genre", ""),
            "tags": t.get("tags", [])[:5] if isinstance(t.get("tags"), list) else []
        }
        track_summaries.append(summary)

    system_prompt = """You are a music classification expert specializing in Arabic, Middle Eastern, and world music.
Analyze the provided tracks and identify distinct musical clusters/categories.
Focus on: genre, mood, instrumentation, cultural origin, and audio characteristics.
Return valid JSON only, no markdown."""

    prompt = f"""Analyze these {len(track_summaries)} tracks and identify 2-4 distinct clusters they might belong to.

Tracks:
{json.dumps(track_summaries, ensure_ascii=False, indent=2)}

Return a JSON object with this structure:
{{
  "identified_clusters": [
    {{
      "cluster_id": "unique_snake_case_id",
      "name": "Human Readable Name",
      "description": "Brief description of this music type",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "audio_characteristics": {{
        "bass_emphasis": "low|medium|high",
        "vocal_presence": "low|medium|high",
        "energy_level": "calm|moderate|energetic"
      }},
      "matching_track_indices": [0, 1, 2]
    }}
  ]
}}"""

    try:
        response = call_groq(prompt, system_prompt)
        # Extract JSON from response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())
    except Exception as e:
        print(f"  Batch {batch_num} analysis failed: {e}")
        return {"identified_clusters": []}


def generate_eq_preset_with_ai(cluster: Dict) -> Dict:
    """Use Groq to generate optimal EQ settings for a cluster"""

    system_prompt = """You are an audio engineer specializing in EQ optimization.
Generate optimal 10-band parametric EQ settings for the described music type.
Frequencies: 32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000 Hz
Gain range: -6 to +6 dB
Return valid JSON only."""

    prompt = f"""Generate optimal EQ preset for this music cluster:

Name: {cluster['name']}
Description: {cluster['description']}
Characteristics: {json.dumps(cluster.get('audio_characteristics', {}), ensure_ascii=False)}

Return JSON with this exact structure:
{{
  "preset_name": "{cluster['name']} EQ",
  "eq_settings": {{
    "32": 0,
    "64": 0,
    "125": 0,
    "250": 0,
    "500": 0,
    "1000": 0,
    "2000": 0,
    "4000": 0,
    "8000": 0,
    "16000": 0
  }},
  "description": "Technical description of why these settings work",
  "characteristics": ["char1", "char2", "char3", "char4"]
}}"""

    try:
        response = call_groq(prompt, system_prompt, max_tokens=1024)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())
    except Exception as e:
        print(f"  EQ generation failed for {cluster['name']}: {e}")
        # Return default flat EQ
        return {
            "preset_name": f"{cluster['name']} EQ",
            "eq_settings": {str(f): 0 for f in [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]},
            "description": "Default flat EQ preset",
            "characteristics": ["Flat response", "Reference quality"]
        }


def classify_track_with_ai(track: Dict, clusters: List[Dict]) -> str:
    """Classify a single track into one of the identified clusters"""

    cluster_options = "\n".join([
        f"- {c['cluster_id']}: {c['name']} - {c['description']}"
        for c in clusters
    ])

    prompt = f"""Classify this track into one of these clusters:

Track:
- Title: {track.get('title', 'Unknown')}
- Artist: {track.get('artist', 'Unknown')}
- Genre: {track.get('genre', '')}

Clusters:
{cluster_options}

Return ONLY the cluster_id (e.g., "arabic_classical"), nothing else."""

    try:
        response = call_groq(prompt, max_tokens=50)
        cluster_id = response.strip().strip('"').lower().replace(" ", "_")
        # Validate it's a known cluster
        known_ids = [c['cluster_id'] for c in clusters]
        if cluster_id in known_ids:
            return cluster_id
        # Fuzzy match
        for cid in known_ids:
            if cid in cluster_id or cluster_id in cid:
                return cid
        return "uncategorized"
    except:
        return "uncategorized"


def dynamic_cluster_tracks(tracks: List[Dict], data_dir: str = "data") -> Dict:
    """Main function: Dynamically cluster tracks using Groq AI"""

    print(f"\n{'='*60}")
    print("DYNAMIC AI CLUSTERING WITH GROQ")
    print(f"{'='*60}")
    print(f"Total tracks to analyze: {len(tracks)}")

    # Step 1: Analyze sample batches to identify clusters
    print("\n[1/4] Analyzing track samples to identify clusters...")
    all_identified = []
    batch_size = 50
    num_batches = min(10, len(tracks) // batch_size)  # Analyze up to 10 batches

    for i in range(num_batches):
        start_idx = i * batch_size
        batch = tracks[start_idx:start_idx + batch_size]
        print(f"  Analyzing batch {i+1}/{num_batches}...")
        result = analyze_track_batch(batch, i+1)
        all_identified.extend(result.get("identified_clusters", []))
        time.sleep(0.5)  # Rate limiting

    # Step 2: Consolidate clusters
    print("\n[2/4] Consolidating cluster definitions...")
    cluster_map = {}
    for cluster in all_identified:
        cid = cluster.get("cluster_id", "").lower().replace(" ", "_")
        if cid and cid not in cluster_map:
            cluster_map[cid] = cluster
        elif cid in cluster_map:
            # Merge keywords
            existing = cluster_map[cid]
            existing["keywords"] = list(set(existing.get("keywords", []) + cluster.get("keywords", [])))

    # Add uncategorized cluster
    cluster_map["uncategorized"] = {
        "cluster_id": "uncategorized",
        "name": "Uncategorized",
        "description": "Tracks that don't fit other categories",
        "keywords": [],
        "audio_characteristics": {"bass_emphasis": "medium", "vocal_presence": "medium", "energy_level": "moderate"}
    }

    clusters = list(cluster_map.values())
    print(f"  Identified {len(clusters)} unique clusters")

    # Step 3: Classify all tracks (using keywords first, AI for ambiguous)
    print("\n[3/4] Classifying tracks into clusters...")
    clustered_tracks = {c["cluster_id"]: [] for c in clusters}

    for idx, track in enumerate(tracks):
        if idx % 500 == 0:
            print(f"  Processing track {idx+1}/{len(tracks)}...")

        # Try keyword matching first (faster)
        title = (track.get("title", "") + " " + track.get("artist", "") + " " + track.get("genre", "")).lower()
        matched = False

        for cluster in clusters:
            if cluster["cluster_id"] == "uncategorized":
                continue
            keywords = cluster.get("keywords", [])
            for kw in keywords:
                if kw.lower() in title:
                    clustered_tracks[cluster["cluster_id"]].append(track)
                    matched = True
                    break
            if matched:
                break

        if not matched:
            clustered_tracks["uncategorized"].append(track)

    # Step 4: Generate EQ presets for each cluster
    print("\n[4/4] Generating AI-powered EQ presets...")
    presets = []
    final_clusters = []

    for cluster in clusters:
        cid = cluster["cluster_id"]
        track_count = len(clustered_tracks.get(cid, []))
        if track_count == 0:
            continue

        print(f"  Generating preset for {cluster['name']} ({track_count} tracks)...")
        eq_preset = generate_eq_preset_with_ai(cluster)
        time.sleep(0.3)

        # Build final cluster data
        cluster_tracks = clustered_tracks[cid]
        unique_artists = len(set(t.get("artist", "") for t in cluster_tracks))

        final_cluster = {
            "id": cid,
            "name": cluster["name"],
            "description": cluster["description"],
            "track_count": track_count,
            "unique_artists": unique_artists,
            "keywords": cluster.get("keywords", []),
            "sample_tracks": [
                {"title": t["title"], "artist": t["artist"], "url": t.get("url", "")}
                for t in cluster_tracks[:5]
            ],
            "tracks": cluster_tracks
        }
        final_clusters.append(final_cluster)

        preset = {
            "cluster_id": cid,
            "cluster_name": cluster["name"],
            "track_count": track_count,
            "preset_name": eq_preset["preset_name"],
            "description": eq_preset["description"],
            "characteristics": eq_preset["characteristics"],
            "eq_settings": eq_preset["eq_settings"],
            "sample_tracks": final_cluster["sample_tracks"]
        }
        presets.append(preset)

    # Sort by track count
    final_clusters.sort(key=lambda x: x["track_count"], reverse=True)
    presets.sort(key=lambda x: x["track_count"], reverse=True)

    # Save results
    print("\n[SAVING] Writing output files...")
    os.makedirs(data_dir, exist_ok=True)

    clusters_output = {
        "source": "Dynamic AI Clustering with Groq",
        "model": GROQ_MODEL,
        "total_tracks": len(tracks),
        "cluster_count": len(final_clusters),
        "clustered_at": datetime.now().isoformat(),
        "clusters": final_clusters
    }

    presets_output = {
        "source": "AI-Generated EQ Presets",
        "model": GROQ_MODEL,
        "total_tracks": len(tracks),
        "generated_at": datetime.now().isoformat(),
        "presets": presets
    }

    with open(os.path.join(data_dir, "track_clusters.json"), "w", encoding="utf-8") as f:
        json.dump(clusters_output, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "eq_presets_detailed.json"), "w", encoding="utf-8") as f:
        json.dump(presets_output, f, ensure_ascii=False, indent=2)

    # Generate eqMac compatible format
    eqmac_presets = {
        "source": "AutoEQ AI-Generated Presets",
        "generated_at": datetime.now().isoformat(),
        "presets": [
            {
                "name": p["preset_name"],
                "cluster": p["cluster_id"],
                "bands": p["eq_settings"]
            }
            for p in presets
        ]
    }

    with open(os.path.join(data_dir, "eq_presets.json"), "w", encoding="utf-8") as f:
        json.dump(eqmac_presets, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("CLUSTERING COMPLETE")
    print(f"{'='*60}")
    print(f"Clusters: {len(final_clusters)}")
    print(f"Presets: {len(presets)}")
    for c in final_clusters[:5]:
        pct = (c["track_count"] / len(tracks)) * 100
        print(f"  - {c['name']}: {c['track_count']} tracks ({pct:.1f}%)")

    return clusters_output


if __name__ == "__main__":
    # Load tracks
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    likes_path = os.path.join(data_dir, "soundcloud_likes.json")

    if not os.path.exists(likes_path):
        print(f"ERROR: {likes_path} not found. Run fetch_likes.py first.")
        exit(1)

    with open(likes_path, "r", encoding="utf-8") as f:
        likes_data = json.load(f)

    tracks = likes_data.get("tracks", [])
    if not tracks:
        print("ERROR: No tracks found in soundcloud_likes.json")
        exit(1)

    dynamic_cluster_tracks(tracks, data_dir)
