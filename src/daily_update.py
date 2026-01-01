#!/usr/bin/env python3
"""
AutoEQ Daily Update Pipeline
Runs once per day to refresh SoundCloud data and regenerate clusters/presets
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/daily_update.log' if os.path.exists('/app') else 'logs/daily_update.log')
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_likes import fetch_all_likes
from groq_cluster import dynamic_cluster_tracks


def run_daily_update():
    """Execute the complete daily update pipeline"""

    start_time = datetime.now()
    logger.info("="*60)
    logger.info("AUTOEQ DAILY UPDATE STARTED")
    logger.info(f"Timestamp: {start_time.isoformat()}")
    logger.info("="*60)

    # Determine paths
    if os.path.exists('/app/data'):
        data_dir = '/app/data'
        logs_dir = '/app/logs'
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        logs_dir = os.path.join(base_dir, 'logs')

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    status = {
        "started_at": start_time.isoformat(),
        "stages": {},
        "success": False
    }

    try:
        # Stage 1: Fetch SoundCloud Likes
        logger.info("\n[STAGE 1/3] Fetching SoundCloud likes...")
        stage1_start = datetime.now()

        likes_data = fetch_all_likes(
            username="amr-farouk-10",
            max_tracks=10000,
            output_dir=data_dir
        )

        track_count = likes_data.get("track_count", 0)
        status["stages"]["fetch"] = {
            "success": track_count > 0,
            "tracks_fetched": track_count,
            "duration_seconds": (datetime.now() - stage1_start).total_seconds()
        }
        logger.info(f"  Fetched {track_count} tracks")

        if track_count == 0:
            raise Exception("No tracks fetched from SoundCloud")

        # Stage 2: Dynamic AI Clustering
        logger.info("\n[STAGE 2/3] Running AI-powered clustering...")
        stage2_start = datetime.now()

        tracks = likes_data.get("tracks", [])
        cluster_result = dynamic_cluster_tracks(tracks, data_dir)

        cluster_count = cluster_result.get("cluster_count", 0)
        status["stages"]["clustering"] = {
            "success": cluster_count > 0,
            "clusters_generated": cluster_count,
            "duration_seconds": (datetime.now() - stage2_start).total_seconds()
        }
        logger.info(f"  Generated {cluster_count} clusters")

        # Stage 3: Validate outputs
        logger.info("\n[STAGE 3/3] Validating outputs...")
        stage3_start = datetime.now()

        required_files = [
            "soundcloud_likes.json",
            "track_clusters.json",
            "eq_presets.json",
            "eq_presets_detailed.json"
        ]

        validation_results = {}
        for fname in required_files:
            fpath = os.path.join(data_dir, fname)
            exists = os.path.exists(fpath)
            size = os.path.getsize(fpath) if exists else 0
            valid = exists and size > 100
            validation_results[fname] = {"exists": exists, "size": size, "valid": valid}
            logger.info(f"  {fname}: {'OK' if valid else 'MISSING'} ({size} bytes)")

        all_valid = all(v["valid"] for v in validation_results.values())
        status["stages"]["validation"] = {
            "success": all_valid,
            "files": validation_results,
            "duration_seconds": (datetime.now() - stage3_start).total_seconds()
        }

        if not all_valid:
            raise Exception("Output validation failed")

        # Success
        status["success"] = True
        status["completed_at"] = datetime.now().isoformat()
        status["total_duration_seconds"] = (datetime.now() - start_time).total_seconds()

        logger.info("\n" + "="*60)
        logger.info("DAILY UPDATE COMPLETED SUCCESSFULLY")
        logger.info(f"Total duration: {status['total_duration_seconds']:.1f} seconds")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"\nDAILY UPDATE FAILED: {e}")
        status["error"] = str(e)
        status["failed_at"] = datetime.now().isoformat()

    finally:
        # Save status
        status_path = os.path.join(data_dir, "last_update_status.json")
        with open(status_path, "w") as f:
            json.dump(status, f, indent=2)
        logger.info(f"\nStatus saved to {status_path}")

    return status["success"]


if __name__ == "__main__":
    success = run_daily_update()
    sys.exit(0 if success else 1)
