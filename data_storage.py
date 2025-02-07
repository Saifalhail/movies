import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DATA_DIR = 'data'
MOVIES_FILE = os.path.join(DATA_DIR, 'movies.json')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')
UPDATE_INTERVAL = timedelta(hours=24)  # Update daily

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")

def save_movies(movies):
    """Save movies to JSON file"""
    try:
        # Ensure data directory exists
        ensure_data_dir()
        
        # Create empty JSON file if it doesn't exist
        if not os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            logger.info(f"Created empty movies JSON file: {MOVIES_FILE}")
        
        # Save the movies data
        with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        metadata = {
            'last_update': datetime.now().isoformat(),
            'movie_count': len(movies)
        }
        
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved {len(movies)} movies to JSON")
        return True
    except Exception as e:
        logger.error(f"Error saving movies to JSON: {str(e)}")
        return False

def load_movies():
    """Load movies from JSON file"""
    try:
        # Create data directory and empty JSON if they don't exist
        ensure_data_dir()
        if not os.path.exists(MOVIES_FILE):
            save_movies([])  # Create empty movies file
            return []
            
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading movies from JSON: {str(e)}")
        return []

def needs_update():
    """Check if the data needs to be updated"""
    try:
        # Create metadata file if it doesn't exist
        if not os.path.exists(METADATA_FILE):
            metadata = {
                'last_update': datetime.min.isoformat(),
                'movie_count': 0
            }
            ensure_data_dir()
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            return True
            
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        last_update = datetime.fromisoformat(metadata['last_update'])
        return datetime.now() - last_update > UPDATE_INTERVAL
    except Exception as e:
        logger.error(f"Error checking update status: {str(e)}")
        return True  # If there's an error, assume update is needed 