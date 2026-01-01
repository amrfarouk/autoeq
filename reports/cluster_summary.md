# SoundCloud Likes Analysis - Cluster Summary

**Generated**: 2026-01-01
**Source**: https://soundcloud.com/amr-farouk-10/likes
**Total Tracks Analyzed**: 5,157

---

## Overview

Your SoundCloud likes reveal a strong preference for Arabic and Middle Eastern music, with a significant focus on classical/traditional and Sufi/religious genres. The analysis identified 8 distinct clusters with custom EQ presets for each.

---

## Cluster Distribution

| Cluster | Tracks | Percentage | Top Characteristic |
|---------|--------|------------|-------------------|
| Arabic Classical / Traditional | 2,025 | 39.3% | Oud, maqam, tarab |
| Uncategorized | 1,269 | 24.6% | Diverse/unclassified |
| Sufi / Religious | 891 | 17.3% | Dhikr, spiritual, vocal |
| Electronic / EDM | 351 | 6.8% | Bass-heavy, synths |
| Instrumental / Ambient | 216 | 4.2% | Acoustic, meditation |
| Arabic Pop / Modern | 189 | 3.7% | Contemporary Arab pop |
| World Music / Fusion | 162 | 3.1% | Cross-cultural blend |
| Rock / Alternative | 54 | 1.0% | Guitar-focused |

---

## EQ Presets

### 1. Arabic Classical (39.3% of tracks)
**Optimized for**: Oud, qanun, ney, traditional orchestras

| Frequency | Adjustment | Purpose |
|-----------|------------|---------|
| 32 Hz | 0 dB | Natural sub |
| 64 Hz | +1 dB | Warm resonance |
| 125 Hz | +2 dB | Instrument body |
| 250 Hz | +1 dB | Warmth |
| 500 Hz | +1 dB | Midrange |
| 1 kHz | +2 dB | Presence |
| 2 kHz | +2 dB | Clarity |
| 4 kHz | **+3 dB** | String sparkle |
| 8 kHz | +2 dB | Air |
| 16 kHz | +1 dB | Extension |

---

### 2. Sufi / Vocal Focus (17.3% of tracks)
**Optimized for**: Dhikr, nasheeds, spiritual chanting

| Frequency | Adjustment | Purpose |
|-----------|------------|---------|
| 32 Hz | -2 dB | Reduce rumble |
| 64 Hz | -1 dB | Clean low-end |
| 125 Hz | 0 dB | Neutral |
| 250 Hz | +1 dB | Vocal warmth |
| 500 Hz | +2 dB | Vocal body |
| 1 kHz | **+3 dB** | Vocal presence |
| 2 kHz | **+3 dB** | Arabic articulation |
| 4 kHz | +2 dB | Brightness |
| 8 kHz | +1 dB | Air |
| 16 kHz | 0 dB | Natural |

---

### 3. Electronic / EDM (6.8% of tracks)
**Optimized for**: Bass drops, synths, dance music

| Frequency | Adjustment | Purpose |
|-----------|------------|---------|
| 32 Hz | **+6 dB** | Massive sub-bass |
| 64 Hz | **+5 dB** | Bass power |
| 125 Hz | **+3 dB** | Punch |
| 250 Hz | 0 dB | Clean |
| 500 Hz | -1 dB | Reduce mud |
| 1 kHz | 0 dB | Neutral |
| 2 kHz | +1 dB | Synth presence |
| 4 kHz | +2 dB | Sparkle |
| 8 kHz | +2 dB | Hi-hat clarity |
| 16 kHz | +1 dB | Air |

---

### 4. Arabic Pop / Modern (3.7% of tracks)
**Optimized for**: Contemporary Middle Eastern pop

| Frequency | Adjustment | Purpose |
|-----------|------------|---------|
| 32 Hz | +2 dB | Modern punch |
| 64 Hz | **+3 dB** | Bass presence |
| 125 Hz | +1 dB | Warmth |
| 250 Hz | 0 dB | Neutral |
| 500 Hz | +1 dB | Vocal body |
| 1 kHz | +2 dB | Clarity |
| 2 kHz | +2 dB | Presence |
| 4 kHz | +1 dB | Brightness |
| 8 kHz | +1 dB | Shimmer |
| 16 kHz | 0 dB | Natural |

---

### 5. Instrumental / Ambient (4.2% of tracks)
**Optimized for**: Piano, acoustic, meditation music

| Frequency | Adjustment | Purpose |
|-----------|------------|---------|
| 32 Hz | 0 dB | Natural |
| 64 Hz | +1 dB | Warmth |
| 125 Hz | +2 dB | Body |
| 250 Hz | +1 dB | Fullness |
| 500 Hz | 0 dB | Neutral |
| 1 kHz | +1 dB | Presence |
| 2 kHz | +2 dB | Clarity |
| 4 kHz | **+3 dB** | Detail |
| 8 kHz | +2 dB | Air |
| 16 kHz | +1 dB | Extension |

---

## Key Insights

1. **Dominant Genre**: Arabic Classical/Traditional music makes up nearly 40% of your likes, suggesting a strong preference for traditional Middle Eastern sounds.

2. **Vocal-Centric**: Sufi/Religious tracks (17.3%) are vocal-focused, requiring EQ that enhances mid-range clarity without harsh highs.

3. **Balanced Listening**: Your music taste spans from deeply traditional (Sufi) to modern electronic (6.8%), showing eclectic preferences.

4. **Arabic Content**: Combined Arabic-related clusters (Classical + Pop + some Sufi) represent over 60% of total tracks.

---

## Files Generated

| File | Description |
|------|-------------|
| `data/soundcloud_likes.json` | Full track list with metadata (5,157 tracks) |
| `data/track_clusters.json` | Clustered tracks with assignments |
| `data/eq_presets.json` | eqMac-compatible preset file |
| `data/eq_presets_detailed.json` | Detailed preset info with sample tracks |

---

## Usage

### Importing to eqMac
The `eq_presets.json` file contains presets in eqMac-compatible format. While eqMac doesn't currently have a public API for preset import, you can:

1. Manually recreate the presets in eqMac using the values above
2. Use the preferences plist (`~/Library/Preferences/com.bitgapp.eqmac.plist`) for advanced users

### Recommended Listening

- **For focus/meditation**: Use "Sufi / Vocal Focus" preset
- **For casual Arabic music**: Use "Arabic Classical" preset
- **For electronic/party music**: Use "Electronic / EDM" preset
- **For modern Arabic pop**: Use "Arabic Pop" preset

---

*Generated by AutoEq SoundCloud Analyzer*
