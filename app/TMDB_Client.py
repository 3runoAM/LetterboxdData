import requests
import concurrent.futures

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
            movie_id = data.get("id")

            details_url = f"{self.base_url}movie/{movie_id}"
            details_params = {"append_to_response": "credits"}

            details_response = requests.get(details_url, params=details_params, headers=self.headers, timeout=10)
            details_response.raise_for_status()

            details_data = details_response.json()

            crew_data = details_data.get("credits", {}).get("crew", [])
            director_list = [member.get("name") for member in crew_data if member.get("job") == "Director"]
            directors_csv = ",".join(director_list) if director_list else None

            production_countries = details_data.get("production_countries", [])
            main_country = production_countries[0].get("name") if production_countries else "Unknown"

            genres_data = details_data.get("genres", [])
            genre_list = [genre.get("name") for genre in genres_data]
            genres_csv = ",".join(genre_list) if genre_list else None

            original_language = details_data.get("original_language", "Unknown")
            overview = details_data.get("overview")
            poster_path = details_data.get("poster_path")
            poster_url = f"{self.image_url}w500{poster_path}" if poster_path else None

            return {
                "Name": movie["title"],
                "Year": movie["release_year"],
                "Genres": genres_csv,
                "Directors": directors_csv,
                "Country": main_country,
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