from flask import Flask, render_template, jsonify, request, send_from_directory
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re
from selenium.common.exceptions import TimeoutException, WebDriverException
import concurrent.futures
from functools import partial
from data_storage import load_movies, needs_update, save_movies, ensure_data_dir

app = Flask(__name__, static_folder='data', static_url_path='/data')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sample_movies():
    return [
        {
            "title": "Mufasa: The Lion King",
            "cinema": "Novo Cinemas - Mall of Qatar",
            "showtimes": ["12:30 PM", "3:00 PM", "5:30 PM", "8:00 PM"],
            "image": "https://lumiere-a.akamaihd.net/v1/images/p_mufasa_thelionking_796_0a8c0009.jpeg",
            "rating": "PG",
            "duration": "120 min",
            "description": "Simba, having become king of the Pride Lands, is determined for his cub to follow in his paw prints while the origins of his late father Mufasa are explored.",
            "genres": ["Animation", "Adventure", "Family"]
        },
        {
            "title": "Dog Man",
            "cinema": "Novo Cinemas - Mall of Qatar",
            "showtimes": ["1:00 PM", "3:30 PM", "6:00 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BZTYyZGY0NTktOWQxZi00NjgwLWEzOWYtODhjZDYzYmVlOGE1XkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_.jpg",
            "rating": "PG",
            "duration": "95 min",
            "description": "A new animated adventure about a part-dog, part-man police officer who loves to fight crime and dance to funk music.",
            "genres": ["Animation", "Comedy", "Family"]
        },
        {
            "title": "Paddington in Peru",
            "cinema": "Novo Cinemas - The Pearl",
            "showtimes": ["2:00 PM", "4:30 PM", "7:00 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BYTUxYjczMWUtYzlkZC00NTcwLWE3ODQtN2I2YTIxOTU0ZTljXkEyXkFqcGdeQXVyMTI2ODM1ODUw._V1_.jpg",
            "rating": "PG",
            "duration": "110 min",
            "description": "Paddington embarks on an epic adventure through the jungles of Peru with the Brown family to find his beloved Aunt Lucy.",
            "genres": ["Adventure", "Comedy", "Family"]
        },
        {
            "title": "Godzilla x Kong",
            "cinema": "Novo Cinemas - Msheireb",
            "showtimes": ["1:30 PM", "4:00 PM", "6:30 PM", "9:00 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BNzE1MDJhMGYtOTA3ZC00MjUyLWI1NjktNzViNjJiZGFkYjc0XkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_.jpg",
            "rating": "PG-13",
            "duration": "115 min",
            "description": "Two ancient titans, Godzilla and Kong, clash in an epic battle as humans unravel their intertwined origins and connection to Skull Island's mysteries.",
            "genres": ["Action", "Adventure", "Sci-Fi"]
        },
        {
            "title": "Kung Fu Panda 4",
            "cinema": "Novo Cinemas - North Gate",
            "showtimes": ["11:00 AM", "1:30 PM", "4:00 PM", "6:30 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BYzE4MTllZTktMTIyZS00Yzg1LTg1YzAtNWNkZjlhMTc0NjZiXkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_.jpg",
            "rating": "PG",
            "duration": "94 min",
            "description": "Po must train a new warrior when he's chosen to become the spiritual leader of the Valley of Peace.",
            "genres": ["Animation", "Action", "Adventure"]
        },
        {
            "title": "Sonic The Hedgehog 3",
            "cinema": "VOX Cinemas - Festival City",
            "showtimes": ["1:30 PM", "4:00 PM", "6:30 PM", "9:00 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BMWM2ZmU5YzgtNzY4NC00YTQ5LTkyMzktNzY1ZmY0MzM5YzY4XkEyXkFqcGdeQXVyMTI0NTE1Njg4._V1_.jpg",
            "rating": "PG",
            "duration": "115 min",
            "description": "Sonic teams up with Tails and Knuckles to face off against a mysterious new adversary, Shadow the Hedgehog.",
            "genres": ["Action", "Adventure", "Family"]
        },
        {
            "title": "Flight Risk",
            "cinema": "VOX Cinemas - Festival City",
            "showtimes": ["2:30 PM", "5:00 PM", "7:30 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BZmQ5YjZkOWYtYjZiZi00ZDZiLWJiYjMtZGVhOGUyZjBmNzk1XkEyXkFqcGdeQXVyMTY3ODkyNDkz._V1_.jpg",
            "rating": "15+",
            "duration": "105 min",
            "description": "A pilot transports an Air Marshal accompanying a fugitive to trial across the Alaskan wilderness.",
            "genres": ["Thriller", "Action", "Drama"]
        },
        {
            "title": "The Bayou",
            "cinema": "VOX Cinemas - Festival City",
            "showtimes": ["3:00 PM", "5:30 PM", "8:00 PM"],
            "image": "https://m.media-amazon.com/images/M/MV5BZjE1ZjQ5NTQtZGQ4Yi00ZDY5LTk2MDAtN2FlODM0OGM5NDc4XkEyXkFqcGdeQXVyMTY3ODkyNDkz._V1_.jpg",
            "rating": "18+",
            "duration": "98 min",
            "description": "A vacation turns into a nightmare when friends survive a plane crash in the Louisiana everglades.",
            "genres": ["Horror", "Thriller", "Mystery"]
        }
    ]

def get_vox_movies():
    movies = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        logger.info("Initializing Chrome driver for VOX Cinemas...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(60)
        
        url = "https://qat.voxcinemas.com/movies/whatson?o=az"
        logger.info(f"Fetching movies from {url}")
        driver.get(url)
        
        # Wait for movies container to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "now-showing"))
        )
        
        # Get all movie elements
        movie_elements = driver.find_elements(By.CLASS_NAME, "movie-summary")
        logger.info(f"Found {len(movie_elements)} movie elements")
        
        # Process each movie
        for movie_element in movie_elements:
            try:
                # Extract basic movie info from the list view
                title = movie_element.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
                logger.info(f"Processing movie: {title}")
                
                # Get movie URL and image
                movie_url = movie_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                image_url = movie_element.find_element(By.CSS_SELECTOR, "img.poster").get_attribute("src")
                
                # Extract rating and language
                rating = movie_element.find_element(By.CSS_SELECTOR, "span.classification").text.strip()
                language = movie_element.find_element(By.CSS_SELECTOR, "p.language").text.replace("Language:", "").strip()
                
                # Open movie details in a new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(movie_url)
                
                try:
                    # Wait for movie details to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "showtimes"))
                    )
                    
                    # Get movie description
                    description = ""
                    try:
                        description = driver.find_element(By.CSS_SELECTOR, ".movie-synopsis").text.strip()
                    except:
                        description = "Description not available"
                    
                    # Get duration
                    duration = ""
                    try:
                        duration = driver.find_element(By.CSS_SELECTOR, ".movie-duration").text.strip()
                    except:
                        duration = "Duration not available"
                    
                    # Get genres
                    genres = []
                    try:
                        genre_elements = driver.find_elements(By.CSS_SELECTOR, ".movie-genre span")
                        genres = [genre.text.strip() for genre in genre_elements]
                    except:
                        genres = []
                    
                    # Get available dates
                    dates = []
                    try:
                        date_elements = driver.find_elements(By.CSS_SELECTOR, ".date-filter .viewport ol li")
                        for date_element in date_elements:
                            date_text = date_element.text.strip()
                            if date_text:
                                dates.append(date_text)
                    except Exception as e:
                        logger.error(f"Error getting dates for {title}: {str(e)}")
                    
                    # Get showtimes for each cinema
                    showtimes_by_cinema = {}
                    try:
                        cinema_sections = driver.find_elements(By.CSS_SELECTOR, ".dates h3.highlight")
                        for section in cinema_sections:
                            cinema_name = section.text.strip()
                            cinema_showtimes = []
                            
                            # Find the next sibling element containing showtimes
                            showtimes_section = section.find_element(By.XPATH, "following-sibling::ol[contains(@class, 'showtimes')]")
                            
                            # Get all showtime elements
                            showtime_elements = showtimes_section.find_elements(By.CSS_SELECTOR, ".action.showtime")
                            for showtime in showtime_elements:
                                time_text = showtime.text.strip()
                                experience = showtime.find_element(By.XPATH, "ancestor::li/parent::ol/parent::li/strong").text.strip()
                                cinema_showtimes.append({
                                    "time": time_text,
                                    "experience": experience
                                })
                            
                            showtimes_by_cinema[cinema_name] = cinema_showtimes
                    except Exception as e:
                        logger.error(f"Error getting showtimes for {title}: {str(e)}")
                    
                    # Create movie object with enhanced data
                    movie = {
                        "title": title,
                        "url": movie_url,
                        "image": image_url,
                        "rating": rating,
                        "language": language,
                        "description": description,
                        "duration": duration,
                        "genres": genres,
                        "dates": dates,
                        "showtimes_by_cinema": showtimes_by_cinema,
                        "source": "VOX"
                    }
                    
                    movies.append(movie)
                    logger.info(f"Successfully processed movie details for {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing movie details for {title}: {str(e)}")
                    # Add basic movie info even if details page fails
                    movie = {
                        "title": title,
                        "url": movie_url,
                        "image": image_url,
                        "rating": rating,
                        "language": language,
                        "description": "Details temporarily unavailable",
                        "duration": "N/A",
                        "genres": [],
                        "dates": [],
                        "showtimes_by_cinema": {},
                        "source": "VOX"
                    }
                    movies.append(movie)
                
                # Close the movie details tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                logger.error(f"Error processing movie {title if 'title' in locals() else 'unknown'}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(movies)} movies from VOX Cinemas")
        return movies
        
    except Exception as e:
        logger.error(f"Error processing VOX Cinemas: {str(e)}")
        return []
        
    finally:
        try:
            driver.quit()
        except:
            pass

def get_novo_movies():
    movies = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        logger.info("Initializing Chrome driver for Novo Cinemas...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(60)
        
        url = "https://qa.novocinemas.com/"
        logger.info(f"Fetching movies from {url}")
        driver.get(url)
        
        # Wait for movies container to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "n-poster-block"))
        )
        
        # Wait for the "now showing" tab to be active
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nowshowing-movie-block.active"))
        )
        
        # Get all movie elements
        movie_elements = driver.find_elements(By.CSS_SELECTOR, "#nowshowing-movie-block .n-movie-poster")
        logger.info(f"Found {len(movie_elements)} movie elements")
        
        # Process each movie
        for movie_element in movie_elements:
            try:
                # Extract basic movie info
                title = movie_element.find_element(By.CSS_SELECTOR, ".movie-title").text.strip()
                logger.info(f"Processing movie: {title}")
                
                # Get movie URL and image
                movie_url = movie_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                image_url = movie_element.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                
                # Extract rating and language
                rating = movie_element.find_element(By.CSS_SELECTOR, ".n-movie-grade").text.strip()
                language = movie_element.find_element(By.CSS_SELECTOR, ".n-movie-desc p").text.strip()
                
                # Open movie details in a new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(movie_url)
                
                try:
                    # Wait for movie details to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "n-movie-date-block"))
                    )
                    
                    # Get movie description
                    description = ""
                    try:
                        description = driver.find_element(By.CSS_SELECTOR, ".n-movie-desc").text.strip()
                    except:
                        description = "Description not available"
                    
                    # Get duration
                    duration = ""
                    try:
                        duration = driver.find_element(By.CSS_SELECTOR, ".n-movie-duration").text.strip()
                    except:
                        duration = "Duration not available"
                    
                    # Get genres
                    genres = []
                    try:
                        genre_elements = driver.find_elements(By.CSS_SELECTOR, ".n-movie-genre span")
                        genres = [genre.text.strip() for genre in genre_elements]
                    except:
                        genres = []
                    
                    # Get available dates
                    dates = []
                    try:
                        date_elements = driver.find_elements(By.CSS_SELECTOR, ".n-date-section .dateselected")
                        for date_element in date_elements:
                            date_text = date_element.find_element(By.CSS_SELECTOR, "a").text.strip()
                            if date_text:
                                dates.append(date_text)
                    except Exception as e:
                        logger.error(f"Error getting dates for {title}: {str(e)}")
                    
                    # Get showtimes for each cinema
                    showtimes_by_cinema = {}
                    try:
                        cinema_sections = driver.find_elements(By.CSS_SELECTOR, ".n-cinema-desc")
                        for section in cinema_sections:
                            cinema_name = section.find_element(By.CSS_SELECTOR, ".n-cinema").text.strip()
                            cinema_showtimes = []
                            
                            # Get language and showtimes
                            showtime_sections = section.find_elements(By.CSS_SELECTOR, ".n-movie-timings")
                            for showtime_section in showtime_sections:
                                language = showtime_section.find_element(By.CSS_SELECTOR, ".n-language").text.strip()
                                
                                # Get all showtime elements
                                showtime_elements = showtime_section.find_elements(By.CSS_SELECTOR, ".n-time a")
                                for showtime in showtime_elements:
                                    time_text = showtime.text.strip()
                                    experience = showtime.find_element(By.XPATH, "following-sibling::span[@class='n-info-experience']").text.strip()
                                    cinema_showtimes.append({
                                        "time": time_text,
                                        "experience": experience,
                                        "language": language
                                    })
                            
                            showtimes_by_cinema[cinema_name] = cinema_showtimes
                    except Exception as e:
                        logger.error(f"Error getting showtimes for {title}: {str(e)}")
                    
                    # Create movie object with enhanced data
                    movie = {
                        "title": title,
                        "url": movie_url,
                        "image": image_url,
                        "rating": rating,
                        "language": language,
                        "description": description,
                        "duration": duration,
                        "genres": genres,
                        "dates": dates,
                        "showtimes_by_cinema": showtimes_by_cinema,
                        "source": "Novo"
                    }
                    
                    movies.append(movie)
                    logger.info(f"Successfully processed movie details for {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing movie details for {title}: {str(e)}")
                    # Add basic movie info even if details page fails
                    movie = {
                        "title": title,
                        "url": movie_url,
                        "image": image_url,
                        "rating": rating,
                        "language": language,
                        "description": "Details temporarily unavailable",
                        "duration": "N/A",
                        "genres": [],
                        "dates": [],
                        "showtimes_by_cinema": {},
                        "source": "Novo"
                    }
                    movies.append(movie)
                
                # Close the movie details tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                logger.error(f"Error processing movie {title if 'title' in locals() else 'unknown'}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(movies)} movies from Novo Cinemas")
        return movies
        
    except Exception as e:
        logger.error(f"Error processing Novo Cinemas: {str(e)}")
        return []
        
    finally:
        try:
            driver.quit()
        except:
            pass

def get_real_movies():
    try:
        # Use ThreadPoolExecutor to run both scrapers in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Check individual cinema caches first
            vox_movies = get_vox_movies()
            novo_movies = get_novo_movies()
            
            futures = []
            if vox_movies is None:
                futures.append((executor.submit(get_vox_movies), 'vox'))
            if novo_movies is None:
                futures.append((executor.submit(get_novo_movies), 'novo'))
            
            all_movies = []
            if vox_movies:
                all_movies.extend(vox_movies)
            if novo_movies:
                all_movies.extend(novo_movies)
            
            for future, cinema in futures:
                try:
                    movies = future.result()
                    all_movies.extend(movies)
                    logger.info(f"Successfully fetched {len(movies)} movies from {cinema.upper()} Cinemas")
                except Exception as e:
                    logger.error(f"Error fetching movies from {cinema.upper()} Cinemas: {str(e)}")
        
        # Sort movies by title
        all_movies.sort(key=lambda x: x['title'])
        
        logger.info(f"Successfully fetched {len(all_movies)} movies in total")
        return all_movies
        
    except Exception as e:
        logger.error(f"Error fetching movies: {str(e)}")
        return get_sample_movies()  # Fallback to sample data

@app.route('/')
def index():
    """Serve the main page with cached data"""
    try:
        # Ensure data directory exists
        ensure_data_dir()
        
        # Load movies from JSON file
        movies = load_movies()
        if not movies:
            logger.warning("No cached movies found in JSON, using sample data")
            movies = get_sample_movies()
            save_movies(movies)  # Save sample data for future use
        
        return render_template('index.html', movies=movies, is_loading=False)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html', movies=get_sample_movies(), is_loading=True)

@app.route('/get_movies')
def get_movies():
    """Get movies from JSON file"""
    try:
        # Check if data needs to be updated
        update_needed = needs_update()
        
        # Load current data from JSON
        movies = load_movies()
        
        if not movies:
            logger.warning("No movies found in JSON file")
            return jsonify({
                'status': 'error',
                'movies': get_sample_movies(),
                'is_loading': False,
                'message': 'No movie data available'
            })
        
        return jsonify({
            'status': 'success',
            'movies': movies,
            'is_loading': update_needed,  # Indicate if an update is needed
            'needs_update': update_needed
        })
            
    except Exception as e:
        logger.error(f"Error fetching movies from JSON: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error loading movies',
            'movies': get_sample_movies(),
            'is_loading': False
        })

@app.route('/get_movies_by_time')
def get_movies_by_time():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    try:
        # Load movies from JSON
        movies = load_movies()
        if not movies:
            logger.warning("No movies found in JSON for time filtering")
            movies = get_sample_movies()
        
        # Filter movies by time if time range is provided
        if start_time and end_time:
            filtered_movies = []
            for movie in movies:
                valid_showtimes = []
                for showtime in movie['showtimes']:
                    time_obj = datetime.strptime(showtime, '%I:%M %p').time()
                    start = datetime.strptime(start_time, '%I:%M %p').time()
                    end = datetime.strptime(end_time, '%I:%M %p').time()
                    
                    if start <= time_obj <= end:
                        valid_showtimes.append(showtime)
            
                if valid_showtimes:
                    movie_copy = movie.copy()
                    movie_copy['showtimes'] = valid_showtimes
                    filtered_movies.append(movie_copy)
            
            movies = filtered_movies
        
        return jsonify({
            'status': 'success', 
            'movies': movies, 
            'is_loading': False,
            'needs_update': needs_update()
        })
    except Exception as e:
        logger.error(f"Error in get_movies_by_time: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error filtering movies by time',
            'movies': get_sample_movies(),
            'is_loading': False
        })

@app.route('/get_available_times')
def get_available_times():
    try:
        # Load movies from JSON
        movies = load_movies()
        if not movies:
            logger.warning("No movies found in JSON for available times")
            movies = get_sample_movies()
        
        all_times = set()
        for movie in movies:
            all_times.update(showtime for showtime in movie['showtimes'])
        
        return jsonify({
            'status': 'success',
            'times': sorted(list(all_times)),
            'needs_update': needs_update()
        })
    except Exception as e:
        logger.error(f"Error in get_available_times: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch available times',
            'times': []
        }), 500

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

if __name__ == '__main__':
    # Ensure data directory exists
    ensure_data_dir()
    
    # Start the Flask app
    app.run(debug=True) 