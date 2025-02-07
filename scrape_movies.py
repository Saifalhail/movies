import logging
from app import get_real_movies
from data_storage import save_movies, ensure_data_dir

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the scraper"""
    try:
        # Ensure data directory exists
        ensure_data_dir()
        
        # Scrape movies
        logger.info("Starting movie scraping process...")
        movies = get_real_movies()
        
        if movies:
            # Save movies to JSON
            if save_movies(movies):
                logger.info(f"Successfully scraped and saved {len(movies)} movies")
            else:
                logger.error("Failed to save movies to JSON")
        else:
            logger.error("No movies were scraped")
            
    except Exception as e:
        logger.error(f"Error in scraping process: {str(e)}")

if __name__ == "__main__":
    main() 