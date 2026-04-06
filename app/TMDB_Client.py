import requests
import concurrent.futures
from flask import request_started

from app.config import TMDB_GENRES

class TMDBClient:
    def __init__(self, token):
        self.api_key = token
        self.base_url = "https://api.themoviedb.org/3/"
        self.image_url = "https://image.tmdb.org/t/p/"
        self.search_url = f"{self.base_url}search/movie"

        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }


    def fetch_movie_details(self, movie):
        try:
            params = {
                "query": movie["title"],
                "year": movie["release_year"],
                "language": "en-US",
            }

            response = requests.get(self.search_url, params=params, headers=self.headers, timeout=10)

            response.raise_for_status()

            results = response.json().get("results")
            if not results or not results[0]:
                return None

            data = results[0]
            genres_ids = data.get("genre_ids", [])
            genre_list = []

            for genre_id in genres_ids:
                genre_name = TMDB_GENRES.get(genre_id)
                if genre_name:
                    genre_list.append(genre_name)

            genres_csv = ",".join(genre_list) if genre_list else None

            #-------------------------------------------------------
            movie_id = data.get("id")
            credits_url = f"{self.base_url}movie/{movie_id}/credits"

            cred_resp = requests.get(credits_url, headers=self.headers, timeout=5)
            cred_resp.raise_for_status()

            crew_data = cred_resp.json().get("crew", [])
            director_list = []

            if crew_data:
                for crew_member in crew_data:
                    if crew_member.get("job") == "Director":
                        director_list.append(crew_member.get("name"))

            directors_csv = ",".join(director_list) if director_list else None

            poster_path = data.get("poster_path", "https://placehold.co/500x750?text=No+Image")
            poster_url = f"{self.image_url}w500{poster_path}" if poster_path else None
            overview = data.get("overview", None)
            original_language = data.get("original_language", None)

            return {
                "Name": movie["title"],
                "Year": movie["release_year"],
                "Genres": genres_csv,
                "Directors": directors_csv,
                "Original Language": original_language,
                "Poster": poster_url,
                "Overview": overview
            }

        except requests.exceptions.HTTPError as err:
            print(f"ERRO EM REQUISIÇÃO: {err}")
        except Exception as err:
            print(f"ERRO: {err}")


    def fetch_movies_parallel(self, movie_list):
        results = []

        completed_tasks = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for movie in movie_list:
                task = executor.submit(self.fetch_movie_details, movie)
                completed_tasks[task] = movie

            for task in concurrent.futures.as_completed(completed_tasks):
                try:
                    movie_details = task.result()

                    if movie_details:
                        results.append(movie_details)

                except Exception as err:
                    print(f"ERRO: {err}")

        return results