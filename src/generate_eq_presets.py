#!/usr/bin/env python3
"""
EQ Preset Generator
Generates optimal EQ presets for each track cluster based on audio characteristics.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# EQ frequency bands (standard 10-band equalizer)
EQ_BANDS = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

# EQ presets for each cluster type
# Values are in dB (-12 to +12 typical range)
EQ_PRESETS = {
    "sufi_religious": {
        "name": "Sufi / Vocal Focus",
        "description": "Optimized for spiritual vocals, Sufi music, and religious chanting. Enhances mid-range clarity for vocals while reducing bass rumble.",
        "bands": {
            32: -2,      # Reduce sub-bass rumble
            64: -1,      # Slight bass reduction
            125: 0,      # Neutral low-mids
            250: +1,     # Warm the lower vocals
            500: +2,     # Enhance vocal body
            1000: +3,    # Boost vocal presence
            2000: +3,    # Clarity for Arabic articulation
            4000: +2,    # Brightness without harshness
            8000: +1,    # Subtle air
            16000: 0     # Neutral highs
        },
        "characteristics": [
            "Vocal-focused",
            "Enhanced mid-range",
            "Clear Arabic diction",
            "Reduced low-end rumble"
        ]
    },
    "arabic_classical": {
        "name": "Arabic Classical",
        "description": "Tailored for traditional Arabic instruments like oud, qanun, and ney. Balances the warm resonance of strings with clear high-end for intricate melodies.",
        "bands": {
            32: 0,       # Natural sub-bass
            64: +1,      # Warm oud resonance
            125: +2,     # Enhance instrument body
            250: +1,     # Warmth
            500: +1,     # Midrange fullness
            1000: +2,    # Presence
            2000: +2,    # Clarity for ney/qanun
            4000: +3,    # Sparkle for strings
            8000: +2,    # Air and shimmer
            16000: +1    # Extended highs
        },
        "characteristics": [
            "Oud resonance enhanced",
            "Clear ney/qanun",
            "Warm maqam tones",
            "Natural dynamics"
        ]
    },
    "arabic_pop": {
        "name": "Arabic Pop",
        "description": "Modern Arabic pop with punchy bass, clear vocals, and crisp highs. Suitable for contemporary Middle Eastern music.",
        "bands": {
            32: +2,      # Modern punch
            64: +3,      # Bass presence
            125: +1,     # Low-mid warmth
            250: 0,      # Neutral
            500: +1,     # Vocal body
            1000: +2,    # Vocal clarity
            2000: +2,    # Presence
            4000: +1,    # Brightness
            8000: +1,    # Shimmer
            16000: 0     # Natural highs
        },
        "characteristics": [
            "Punchy modern bass",
            "Clear Arabic vocals",
            "Radio-friendly",
            "Contemporary sound"
        ]
    },
    "electronic_edm": {
        "name": "Electronic / EDM",
        "description": "Heavy bass, powerful sub-frequencies, and crisp highs for electronic dance music. The drop hits harder.",
        "bands": {
            32: +6,      # Massive sub-bass
            64: +5,      # Bass power
            125: +3,     # Low-end punch
            250: 0,      # Neutral low-mids
            500: -1,     # Reduce muddiness
            1000: 0,     # Neutral mids
            2000: +1,    # Synth presence
            4000: +2,    # Synth sparkle
            8000: +2,    # Hi-hat clarity
            16000: +1    # Air
        },
        "characteristics": [
            "Massive sub-bass",
            "Powerful drops",
            "Clear synths",
            "Club-ready sound"
        ]
    },
    "instrumental": {
        "name": "Instrumental / Ambient",
        "description": "Balanced and natural for acoustic instruments, piano, and ambient music. Minimal coloration, maximum fidelity.",
        "bands": {
            32: 0,       # Natural
            64: +1,      # Subtle warmth
            125: +2,     # Instrument body
            250: +1,     # Low-mid fullness
            500: 0,      # Neutral
            1000: +1,    # Presence
            2000: +2,    # Clarity
            4000: +3,    # Detail
            8000: +2,    # Air
            16000: +1    # Extended response
        },
        "characteristics": [
            "Natural tonality",
            "Acoustic detail",
            "Wide soundstage",
            "Minimal coloration"
        ]
    },
    "world_fusion": {
        "name": "World / Fusion",
        "description": "Versatile preset for world music with diverse instrumentation. Balances ethnic instruments with modern production.",
        "bands": {
            32: +1,      # Global bass
            64: +2,      # Warm foundation
            125: +1,     # Body
            250: +1,     # Warmth
            500: +1,     # Midrange
            1000: +2,    # Presence
            2000: +2,    # Clarity
            4000: +2,    # Detail
            8000: +1,    # Air
            16000: +1    # Extension
        },
        "characteristics": [
            "Balanced across genres",
            "Ethnic instrument clarity",
            "Modern production support",
            "Versatile"
        ]
    },
    "rock_alternative": {
        "name": "Rock / Alternative",
        "description": "Guitar-focused with punchy drums and clear vocals. Cuts through the mix without being harsh.",
        "bands": {
            32: +1,      # Sub presence
            64: +3,      # Kick drum
            125: +2,     # Bass guitar
            250: +1,     # Warmth
            500: 0,      # Reduce mud
            1000: +2,    # Guitar presence
            2000: +3,    # Guitar bite
            4000: +2,    # Clarity
            8000: +1,    # Cymbal shimmer
            16000: 0     # Natural
        },
        "characteristics": [
            "Guitar-forward",
            "Punchy drums",
            "Clear vocals",
            "Energy without harshness"
        ]
    },
    "hip_hop_rap": {
        "name": "Hip-Hop / Rap",
        "description": "Deep bass, clear vocals, and crisp hi-hats. Optimized for beats and flow.",
        "bands": {
            32: +5,      # Deep 808s
            64: +4,      # Bass punch
            125: +2,     # Low-end power
            250: 0,      # Neutral
            500: +1,     # Vocal warmth
            1000: +2,    # Vocal presence
            2000: +2,    # Clarity
            4000: +1,    # Brightness
            8000: +2,    # Hi-hat snap
            16000: +1    # Air
        },
        "characteristics": [
            "Deep 808 bass",
            "Clear vocal flow",
            "Crisp hi-hats",
            "Beat-focused"
        ]
    },
    "uncategorized": {
        "name": "Flat / Reference",
        "description": "Neutral preset with minimal adjustment. Use when track type is unknown or for reference listening.",
        "bands": {
            32: 0,
            64: 0,
            125: 0,
            250: 0,
            500: 0,
            1000: 0,
            2000: 0,
            4000: 0,
            8000: 0,
            16000: 0
        },
        "characteristics": [
            "Flat response",
            "Reference quality",
            "No coloration",
            "True to source"
        ]
    }
}


def generate_eqmac_preset(preset_data, preset_id):
    """Generate eqMac-compatible preset format."""
    bands = preset_data['bands']

    return {
        "id": preset_id,
        "name": preset_data['name'],
        "isDefault": False,
        "gains": {
            "global": 0,
            "bands": [
                {"frequency": freq, "gain": bands[freq]}
                for freq in EQ_BANDS
            ]
        }
    }


def main():
    print("=" * 60)
    print("EQ Preset Generator")
    print("=" * 60)

    # Load clusters
    clusters_file = DATA_DIR / "track_clusters.json"
    if not clusters_file.exists():
        print(f"Error: {clusters_file} not found")
        print("Please run cluster_tracks.py first")
        return

    with open(clusters_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)

    clusters = cluster_data.get('clusters', [])
    print(f"Loaded {len(clusters)} clusters")

    # Generate presets
    presets = []
    preset_details = []

    for cluster in clusters:
        cluster_id = cluster['id']
        if cluster_id in EQ_PRESETS:
            preset_data = EQ_PRESETS[cluster_id]
            eqmac_preset = generate_eqmac_preset(preset_data, cluster_id)
            presets.append(eqmac_preset)

            preset_details.append({
                'cluster_id': cluster_id,
                'cluster_name': cluster['name'],
                'track_count': cluster['track_count'],
                'preset_name': preset_data['name'],
                'description': preset_data['description'],
                'characteristics': preset_data['characteristics'],
                'eq_settings': preset_data['bands'],
                'sample_tracks': cluster.get('sample_tracks', [])[:3]
            })

            print(f"  Generated preset: {preset_data['name']} ({cluster['track_count']} tracks)")

    # Save eqMac presets
    eqmac_output = {
        "name": "SoundCloud Auto-EQ Presets",
        "description": "Auto-generated presets based on SoundCloud likes analysis",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "presets": presets
    }

    eqmac_file = OUTPUT_DIR / "eq_presets.json"
    with open(eqmac_file, 'w', encoding='utf-8') as f:
        json.dump(eqmac_output, f, indent=2)
    print(f"\neqMac presets saved to: {eqmac_file}")

    # Save detailed preset info
    detailed_output = {
        "source": cluster_data.get('source'),
        "total_tracks": cluster_data.get('total_tracks'),
        "generated_at": datetime.now().isoformat(),
        "presets": preset_details
    }

    detailed_file = OUTPUT_DIR / "eq_presets_detailed.json"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_output, f, ensure_ascii=False, indent=2)
    print(f"Detailed presets saved to: {detailed_file}")

    # Print summary table
    print("\n" + "=" * 60)
    print("EQ Presets Summary")
    print("=" * 60)
    print(f"{'Preset':<25} {'Tracks':<10} {'Key EQ Adjustments'}")
    print("-" * 60)
    for detail in preset_details:
        bands = detail['eq_settings']
        # Find notable adjustments
        notable = []
        for freq, gain in bands.items():
            if abs(gain) >= 3:
                notable.append(f"{freq}Hz: {gain:+d}dB")
        notable_str = ", ".join(notable[:3]) or "Subtle adjustments"
        print(f"{detail['preset_name']:<25} {detail['track_count']:<10} {notable_str}")

    return presets


if __name__ == "__main__":
    main()
