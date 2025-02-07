# Qatar Cinema Showtimes

A modern web application that shows real-time movie showtimes from Novo Cinemas and VOX Cinemas in Qatar.

## Features
- Real-time movie data from Novo Cinemas and VOX Cinemas
- View movies by cinema location with expandable sections
- View showtimes by time period with customizable time ranges
- Filter movies by cinema location
- Mobile-friendly responsive interface
- Automatic data refresh
- Smart caching system for better performance
- Beautiful modern UI with smooth animations

## Requirements
- Python 3.8 or higher
- Google Chrome browser (for web scraping)
- Internet connection

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qatar-cinema-showtimes.git
   cd qatar-cinema-showtimes
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Features in Detail

### Movies View
- Expandable cinema sections
- Real-time movie information including:
  - Title, rating, and duration
  - Movie poster
  - Genre tags
  - Description
  - Available showtimes
- Filter by cinema location

### Times View
- Expandable time selection
- Quick time period filters (Morning, Afternoon, Evening, Night)
- Custom time range selection
- Movies grouped by showtime

### Data Refresh
- Automatic data refresh every 5 minutes
- Manual refresh button
- Smart caching to reduce server load

## Technologies Used
- Python/Flask for backend
- Selenium for web scraping
- BeautifulSoup4 for HTML parsing
- Bootstrap for responsive UI
- Custom CSS for animations and modern design

## Contributing
Feel free to open issues or submit pull requests for any improvements.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 