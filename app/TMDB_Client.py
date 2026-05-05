import requests
import concurrent.futures
import json
import os
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


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

        self.cache_file = os.path.join("data", "tmdb_cache.json")
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((requests.exceptions.RequestException, Exception))
    )
    def _make_request(self, url, params):
        response = requests.get(url, params=params, headers=self.headers, timeout=10)

        # Se batermos no rate limit do TMDB, forçamos o erro para o tenacity tentar de novo
        if response.status_code == 429:
            raise Exception("Rate limit do TMDB atingido (Erro 429). Tentando novamente...")

        response.raise_for_status()
        return response.json()

    def fetch_movie_details(self, movie):
        cache_key = f"{movie["title"]}_{movie["release_year"]}_{movie["Letterboxd URI"]}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            params = {
                "query": movie["title"],
                "year": movie["release_year"],
                "language": "en-US",
            }
            search_data = self._make_request(self.search_url, params)

            results = search_data.get("results")
            if not results or not results[0]:
                return None

            movie_id = results[0].get("id")

            details_url = f"{self.base_url}movie/{movie_id}"
            details_params = {"append_to_response": "credits"}

            details_data = self._make_request(details_url, details_params)

            genres = details_data.get("genres", [])
            genres_csv = ", ".join([genre["name"] for genre in genres])

            credits = details_data.get("credits", {})
            crew = credits.get("crew", [])
            directors_csv = ", ".join([member["name"] for member in crew if member.get("job") == "Director"])

            production_countries = details_data.get("production_countries", [])
            main_country = production_countries[0]["name"] if production_countries else "Unknown"

            original_language = details_data.get("original_language", "Unknown")
            overview = details_data.get("overview")
            poster_path = details_data.get("poster_path")
            poster_url = f"{self.image_url}w500{poster_path}" if poster_path else None

            movie_info = {
                "Name": movie["title"],
                "Year": movie["release_year"],
                "Genres": genres_csv,
                "Directors": directors_csv,
                "Country": main_country,
                "Original Language": original_language,
                "Poster": poster_url,
                "Overview": overview
            }

            self.cache[cache_key] = movie_info
            return movie_info

        except Exception as err:
            print(f"ERRO Desistindo de buscar \"{movie['title']}\" após várias tentativas: {err}")
            return None

    def fetch_movies_parallel(self, movie_list):
        results = []
        completed_tasks = {}

        # MANTENDO OS SEUS 10 WORKERS
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
                    print(f"Erro no processamento de uma thread paralela: {err}")

        # 4. SALVA O CACHE NO DISCO ASSIM QUE TODOS OS FILMES TERMINAREM
        self._save_cache()
        return results