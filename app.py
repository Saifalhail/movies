from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import time

app = Flask(__name__)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_novo_cinemas():
    movies = []
    try:
        driver = setup_driver()
        driver.get("https://qa.novocinemas.com/")
        time.sleep(5)  # Wait for dynamic content to load
        
        # Extract movie information
        movie_elements = driver.find_elements(By.CLASS_NAME, "movie-item")
        for element in movie_elements:
            try:
                title = element.find_element(By.CLASS_NAME, "movie-title").text
                showtimes = element.find_elements(By.CLASS_NAME, "showtime")
                times = [time.text for time in showtimes]
                if title and times:
                    movies.append({
                        "title": title,
                        "cinema": "Novo Cinemas",
                        "showtimes": times
                    })
            except Exception as e:
                continue
                
        driver.quit()
    except Exception as e:
        print(f"Error scraping Novo Cinemas: {str(e)}")
    return movies

def scrape_vox_cinemas():
    movies = []
    try:
        driver = setup_driver()
        driver.get("https://qat.voxcinemas.com/")
        time.sleep(5)  # Wait for dynamic content to load
        
        # Extract movie information
        movie_elements = driver.find_elements(By.CLASS_NAME, "movie-card")
        for element in movie_elements:
            try:
                title = element.find_element(By.CLASS_NAME, "movie-title").text
                showtimes = element.find_elements(By.CLASS_NAME, "showtime")
                times = [time.text for time in showtimes]
                if title and times:
                    movies.append({
                        "title": title,
                        "cinema": "VOX Cinemas",
                        "showtimes": times
                    })
            except Exception as e:
                continue
                
        driver.quit()
    except Exception as e:
        print(f"Error scraping VOX Cinemas: {str(e)}")
    return movies

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_movies')
def get_movies():
    novo_movies = scrape_novo_cinemas()
    vox_movies = scrape_vox_cinemas()
    all_movies = novo_movies + vox_movies
    return jsonify(all_movies)

if __name__ == '__main__':
    app.run(debug=True) 