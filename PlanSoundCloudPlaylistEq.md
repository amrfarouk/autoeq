```
## Task: SoundCloud Likes Scraper + Genre Clustering for Auto-EQ

### Objective
Scrape full likes list from SoundCloud, extract metadata, cluster by audio characteristics, and define optimal EQ presets for each cluster.

### Target URL
https://soundcloud.com/amr-farouk-10/likes

### Phase 1: Scrape All Liked Tracks

Use Puppeteer or Playwright (SoundCloud requires JS rendering + infinite scroll):

1. Navigate to likes page
2. Scroll to bottom repeatedly until no new tracks load
3. For each track, extract:
   - Track title
   - Artist name
   - Track URL
   - Genre tags (if visible)
   - Duration
   - Play count
   - Upload date

### Phase 2: Enrich Metadata

For each track URL, fetch the track page and extract:
- SoundCloud's genre/tags (in page metadata or JSON-LD)
- Description keywords
- Waveform characteristics (if accessible via API)
- Related tracks (hints at genre)

Also try SoundCloud's oEmbed endpoint:
```
https://soundcloud.com/oembed?format=json&url=TRACK_URL
```

### Phase 3: Cluster Analysis

Group tracks by characteristics. Suggested clustering logic:

| Signal | Weight | Example |
|--------|--------|---------|
| Arabic title/artist | High | الدنيا، يا سلام |
| Keywords: Sheikh, Sufi, Inshad, ذكر | High | Sufi/Religious |
| Keywords: Remix, DJ, Beat, Bass | High | Electronic |
| Duration > 10min | Medium | Likely Sufi/Live |
| Duration < 3min | Medium | Likely Pop |
| Instrumental keywords | Medium | Oud, Piano, عود |

Output clusters as JSON:
```json
{
  "clusters": [
    {
      "name": "Arabic Vocal / Sufi",
      "track_count": 45,
      "characteristics": ["Arabic lyrics", "vocal-focused", "spiritual"],
      "sample_tracks": ["track1", "track2"],
      "recommended_eq": {}
    }
  ]
}
```

### Phase 4: Define EQ Presets

For each cluster, recommend eqMac preset settings (10-band EQ):

| Frequency | Sufi/Vocal | Electronic/Bass | Instrumental |
|-----------|------------|-----------------|--------------|
| 32 Hz     | -2 dB      | +6 dB           | 0 dB         |
| 64 Hz     | -1 dB      | +5 dB           | +1 dB        |
| 125 Hz    | 0 dB       | +3 dB           | +2 dB        |
| 250 Hz    | +1 dB      | 0 dB            | +1 dB        |
| 500 Hz    | +2 dB      | -1 dB           | 0 dB         |
| 1 kHz     | +3 dB      | 0 dB            | +1 dB        |
| 2 kHz     | +3 dB      | +1 dB           | +2 dB        |
| 4 kHz     | +2 dB      | +2 dB           | +3 dB        |
| 8 kHz     | +1 dB      | +1 dB           | +2 dB        |
| 16 kHz    | 0 dB       | 0 dB            | +1 dB        |

Adjust recommendations based on actual cluster characteristics discovered.

### Deliverables

1. `soundcloud_likes.json` - Full track list with metadata
2. `track_clusters.json` - Grouped tracks with cluster definitions
3. `eq_presets.json` - eqMac-compatible preset definitions per cluster
4. `cluster_summary.md` - Human-readable summary of findings

### Technical Notes

- Install: `npm install puppeteer` or `pip install playwright && playwright install`
- SoundCloud rate limits: Add 1-2 second delays between requests
- If blocked, try with stealth plugin or residential proxy
- Fallback: Use SoundCloud API v2 (undocumented but works): 
  `https://api-v2.soundcloud.com/users/USER_ID/likes?client_id=CLIENT_ID`

### Success Criteria

- Minimum 80% of liked tracks captured
- At least 3 distinct clusters identified
- EQ presets validated against audio engineering principles for each genre type
```