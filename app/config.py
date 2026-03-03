import os

#-----------------------------------------------------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

#-----------------------------------------------------------------------------------------------------------------------

EXPECTED_DATA = {
    'diary.csv': ['Date', 'Name', 'Year', 'Letterboxd URI', 'Rating', 'Rewatch', 'Tags', 'Watched Date'],
    'ratings.csv': ['Date', 'Name', 'Year', 'Letterboxd URI', 'Rating'],
    'watched.csv': ['Date', 'Name', 'Year', 'Letterboxd URI']
}

#-----------------------------------------------------------------------------------------------------------------------

