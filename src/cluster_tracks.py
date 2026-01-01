#!/usr/bin/env python3
"""
Track Clustering Script
Groups tracks by audio characteristics using keyword analysis.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "data"


# Arabic detection pattern
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')

# Cluster definitions with keywords and patterns
CLUSTER_DEFINITIONS = {
    "sufi_religious": {
        "name": "Sufi / Religious",
        "keywords": [
            "sufi", "sufism", "dhikr", "zikr", "ذكر", "صوفي", "إنشاد", "inshad",
            "qawwali", "nasheeds", "nasheed", "naat", "hamd", "allah", "الله",
            "prophet", "رسول", "نبي", "sheikh", "شيخ", "mawlid", "مولد",
            "hadra", "حضرة", "sama", "سماع", "whirling", "dervish", "درويش",
            "spiritual", "روحاني", "meditation", "تأمل", "prayer", "صلاة",
            "quran", "قرآن", "recitation", "تلاوة", "islamic", "إسلامي",
            "masjid", "mosque", "مسجد", "tawhid", "توحيد"
        ],
        "duration_hint": "long",  # Often > 10 minutes
        "weight": 1.5
    },
    "arabic_classical": {
        "name": "Arabic Classical / Traditional",
        "keywords": [
            "classical", "كلاسيك", "tarab", "طرب", "oud", "عود", "qanun", "قانون",
            "ney", "ناي", "maqam", "مقام", "oriental", "شرقي", "arabic", "عربي",
            "egypt", "مصر", "lebanon", "لبنان", "syria", "سوريا", "umm kulthum",
            "أم كلثوم", "farid", "فريد", "abdel halim", "عبد الحليم", "traditional",
            "تراث", "heritage", "folkloric", "شعبي", "baladi", "بلدي", "saidi",
            "صعيدي", "levantine", "khaleeji", "خليجي", "gulf"
        ],
        "duration_hint": "medium",
        "weight": 1.3
    },
    "arabic_pop": {
        "name": "Arabic Pop / Modern",
        "keywords": [
            "pop", "بوب", "modern", "حديث", "amr diab", "عمرو دياب", "nancy",
            "نانسي", "elissa", "إليسا", "haifa", "هيفا", "rotana", "روتانا",
            "arabic pop", "عربي", "mashup", "remix عربي", "arab", "egypt pop",
            "lebanese", "لبناني"
        ],
        "duration_hint": "short",
        "weight": 1.0
    },
    "electronic_edm": {
        "name": "Electronic / EDM",
        "keywords": [
            "electronic", "edm", "house", "techno", "trance", "dubstep", "bass",
            "remix", "dj", "club", "dance", "beat", "drop", "synth", "synthesizer",
            "rave", "festival", "progressive", "deep house", "tech house",
            "minimal", "ambient electronic", "breakbeat", "drum and bass", "dnb",
            "future bass", "trap", "electro", "electronica"
        ],
        "duration_hint": "medium",
        "weight": 1.0
    },
    "instrumental": {
        "name": "Instrumental / Ambient",
        "keywords": [
            "instrumental", "piano", "guitar", "violin", "cello", "orchestra",
            "ambient", "relaxing", "meditation music", "sleep", "study",
            "concentration", "focus", "calm", "peaceful", "nature sounds",
            "acoustic", "solo", "no vocals", "cinematic", "soundtrack", "score",
            "film music", "epic", "strings", "woodwind", "brass"
        ],
        "duration_hint": None,
        "weight": 1.0
    },
    "world_fusion": {
        "name": "World Music / Fusion",
        "keywords": [
            "world", "fusion", "global", "ethnic", "tribal", "african", "indian",
            "persian", "turkish", "flamenco", "latin", "brazilian", "reggae",
            "dub", "world beat", "ethno", "multicultural", "cross-cultural",
            "traditional fusion", "contemporary world"
        ],
        "duration_hint": None,
        "weight": 0.9
    },
    "rock_alternative": {
        "name": "Rock / Alternative",
        "keywords": [
            "rock", "alternative", "indie", "metal", "punk", "grunge", "hard rock",
            "classic rock", "progressive rock", "post-rock", "shoegaze", "brit pop",
            "garage", "blues rock", "psychedelic", "stoner", "doom"
        ],
        "duration_hint": None,
        "weight": 0.8
    },
    "hip_hop_rap": {
        "name": "Hip-Hop / Rap",
        "keywords": [
            "hip hop", "hip-hop", "rap", "rapper", "beats", "flow", "rhyme",
            "mc", "emcee", "freestyle", "trap rap", "boom bap", "old school",
            "new school", "conscious", "gangsta", "drill", "mumble"
        ],
        "duration_hint": None,
        "weight": 0.8
    }
}


def has_arabic(text):
    """Check if text contains Arabic characters."""
    if not text:
        return False
    return bool(ARABIC_PATTERN.search(str(text)))


def parse_duration_seconds(duration_str):
    """Parse duration string to seconds."""
    if not duration_str:
        return None
    try:
        parts = str(duration_str).split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return None


def get_duration_ms(track):
    """Get duration in milliseconds."""
    if track.get('duration_ms'):
        return track['duration_ms']
    duration = track.get('duration')
    if duration:
        secs = parse_duration_seconds(duration)
        return secs * 1000 if secs else None
    return None


def classify_track(track):
    """Classify a single track into clusters."""
    scores = defaultdict(float)

    # Combine all text fields for keyword matching
    text_fields = [
        track.get('title', ''),
        track.get('artist', ''),
        track.get('genre', ''),
        track.get('tag_list', ''),
        track.get('description', ''),
    ]
    combined_text = ' '.join(str(f).lower() for f in text_fields if f)

    # Check for Arabic content
    is_arabic = any(has_arabic(f) for f in text_fields)
    if is_arabic:
        scores['sufi_religious'] += 0.3
        scores['arabic_classical'] += 0.3
        scores['arabic_pop'] += 0.2

    # Duration analysis
    duration_ms = get_duration_ms(track)
    if duration_ms:
        duration_min = duration_ms / 60000
        if duration_min > 10:
            scores['sufi_religious'] += 0.5
            scores['arabic_classical'] += 0.3
        elif duration_min > 6:
            scores['arabic_classical'] += 0.2
            scores['electronic_edm'] += 0.1
        elif duration_min < 3:
            scores['arabic_pop'] += 0.2
            scores['hip_hop_rap'] += 0.1

    # Keyword matching
    for cluster_id, cluster_def in CLUSTER_DEFINITIONS.items():
        keywords = cluster_def['keywords']
        weight = cluster_def.get('weight', 1.0)

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in combined_text:
                # More weight for title/artist matches
                if keyword_lower in str(track.get('title', '')).lower():
                    scores[cluster_id] += 1.5 * weight
                elif keyword_lower in str(track.get('artist', '')).lower():
                    scores[cluster_id] += 1.2 * weight
                elif keyword_lower in str(track.get('genre', '')).lower():
                    scores[cluster_id] += 1.0 * weight
                else:
                    scores[cluster_id] += 0.5 * weight

    # Get the best matching cluster
    if scores:
        best_cluster = max(scores.items(), key=lambda x: x[1])
        if best_cluster[1] >= 0.5:  # Minimum score threshold
            return best_cluster[0], best_cluster[1], dict(scores)

    return 'uncategorized', 0, dict(scores)


def cluster_tracks(tracks):
    """Cluster all tracks."""
    clusters = defaultdict(list)
    cluster_stats = defaultdict(lambda: {
        'count': 0,
        'total_duration_ms': 0,
        'artists': set(),
        'sample_tracks': []
    })

    for track in tracks:
        cluster_id, score, all_scores = classify_track(track)

        track_with_cluster = track.copy()
        track_with_cluster['cluster'] = cluster_id
        track_with_cluster['cluster_score'] = score
        track_with_cluster['all_cluster_scores'] = all_scores

        clusters[cluster_id].append(track_with_cluster)

        # Update stats
        stats = cluster_stats[cluster_id]
        stats['count'] += 1
        if track.get('duration_ms'):
            stats['total_duration_ms'] += track['duration_ms']
        if track.get('artist'):
            stats['artists'].add(track['artist'])
        if len(stats['sample_tracks']) < 5:
            stats['sample_tracks'].append({
                'title': track.get('title'),
                'artist': track.get('artist'),
                'url': track.get('url')
            })

    return clusters, cluster_stats


def main():
    print("=" * 60)
    print("Track Clustering")
    print("=" * 60)

    # Load tracks
    input_file = DATA_DIR / "soundcloud_likes.json"
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tracks = data.get('tracks', [])
    print(f"Loaded {len(tracks)} tracks")

    # Cluster tracks
    print("\nClustering tracks...")
    clusters, cluster_stats = cluster_tracks(tracks)

    # Build output
    output_clusters = []
    for cluster_id in sorted(clusters.keys(), key=lambda x: len(clusters[x]), reverse=True):
        cluster_tracks_list = clusters[cluster_id]
        stats = cluster_stats[cluster_id]

        cluster_def = CLUSTER_DEFINITIONS.get(cluster_id, {})
        cluster_name = cluster_def.get('name', cluster_id.replace('_', ' ').title())

        avg_duration_ms = stats['total_duration_ms'] / stats['count'] if stats['count'] > 0 else 0

        output_clusters.append({
            'id': cluster_id,
            'name': cluster_name,
            'track_count': len(cluster_tracks_list),
            'unique_artists': len(stats['artists']),
            'avg_duration_min': round(avg_duration_ms / 60000, 1) if avg_duration_ms else 0,
            'sample_tracks': stats['sample_tracks'],
            'tracks': cluster_tracks_list
        })

        print(f"  {cluster_name}: {len(cluster_tracks_list)} tracks from {len(stats['artists'])} artists")

    # Save results
    output = {
        'source': data.get('source'),
        'total_tracks': len(tracks),
        'cluster_count': len(output_clusters),
        'clustered_at': datetime.now().isoformat(),
        'clusters': output_clusters
    }

    output_file = OUTPUT_DIR / "track_clusters.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nClusters saved to: {output_file}")

    # Summary
    print("\n" + "=" * 60)
    print("Clustering Summary")
    print("=" * 60)
    for cluster in output_clusters:
        print(f"  {cluster['name']}: {cluster['track_count']} tracks ({cluster['track_count']/len(tracks)*100:.1f}%)")

    return output


if __name__ == "__main__":
    main()
