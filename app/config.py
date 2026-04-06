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

TMDB_GENRES = {
    28: "Ação",
    12: "Aventura",
    16: "Animação",
    35: "Comédia",
    80: "Crime",
    99: "Documentário",
    18: "Drama",
    10751: "Família",
    14: "Fantasia",
    36: "História",
    27: "Terror",
    10402: "Música",
    9648: "Mistério",
    10749: "Romance",
    878: "Ficção Científica",
    10770: "Cinema TV",
    53: "Suspense",
    10752: "Guerra",
    37: "Faroeste"
}