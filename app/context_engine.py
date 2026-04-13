import pandas

def get_total_movies(df_watched):
    return df_watched.shape[0]

def get_average_rating(df_rating):
    return round(df_rating["Rating"].mean(), 1)

def get_streak_context(df_diary, df_watched_enriched):
    dates = df_diary["Watched Date"].drop_duplicates().sort_values(ignore_index=True)

    if dates.empty:
        return {"days": 0, "start": None, "end": None}

    is_not_consecutive = dates.diff() != pandas.Timedelta(days=1)

    streak_ids = is_not_consecutive.cumsum()

    streaks = dates.groupby(streak_ids).agg(["count", "min", "max"])
    longest = streaks.loc[streaks["count"].idxmax()]

    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    def format_date_pt(date_obj):
        if pandas.isna(date_obj):
            return None
        return f"{date_obj.day} de {meses_pt[date_obj.month]} de {date_obj.year}"

    streak_movies = None
    if df_watched_enriched is not None:
        streak_mask = (df_diary["Watched Date"] >= longest["min"]) & (df_diary["Watched Date"] <= longest["max"])
        df_streak_movies = df_diary[streak_mask]

        df_streak_movies = pandas.merge(df_streak_movies, df_watched_enriched[["Name", "Year", "Poster"]],
                                        on=["Name", "Year"], how="left").sort_values(by="Rating", ascending=False)


        streak_movies = df_streak_movies[["Name", "Year", "Poster", "Rating"]].to_dict(orient='records')

    return {
        "days": int(longest["count"]),
        "start": format_date_pt(longest["min"]),
        "end": format_date_pt(longest["max"]),
        "movies": streak_movies
    }

def get_favorite_day(df_diary):
    days_ptbr = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    favorite_day_en = df_diary["Dia_da_Semana"].mode()[0]

    return days_ptbr.get(favorite_day_en, favorite_day_en)

def get_favorite_decade(df_ratings):
    decades = df_ratings.groupby("Decade").agg(
        Media=("Rating", "mean"),
        Contagem=("Rating", "count")
    )

    valid_decades = decades[decades["Contagem"] >= 5]

    if valid_decades.empty:
        return None

    favorite_decade = valid_decades["Media"].idxmax()

    return favorite_decade

def get_rewatch_context(df_diary, df_watched_enriched):
    total_diary = len(df_diary)
    total_rewatches = df_diary["Rewatch"].sum()
    taxa_rewatch = (total_rewatches / total_diary) * 100 if total_diary > 0 else 0

    if taxa_rewatch > 40:
        rewatch_profile = "Guardião da Nostalgia"
        rewatch_description = f"Com {taxa_rewatch:.1f}% de filmes revistos, você tem filmes de conforto e ama revisitá-los. Por que arriscar se o clássico é garantido?"
    elif taxa_rewatch > 15:
        rewatch_profile = "Curador Equilibrado"
        rewatch_description = f"Sua taxa de rewatch é de {taxa_rewatch:.1f}%. Você não tem medo de fazer novas descobertas, mas nunca abandona seus filmes conforto."
    elif taxa_rewatch > 5:
        rewatch_profile = "Explorador"
        rewatch_description = f"Você reassiste apenas {taxa_rewatch:.1f}% dos filmes. O mundo é grande demais para gastar tempo vendo a mesma coisa."
    else:
        rewatch_profile = "Caçador de Inéditos"
        rewatch_description = f"Você reassistiu filmes {taxa_rewatch:.1f}% das vezes! Reprise é uma palavra que não existe no seu dicionário."

    #-----------------------------------------------------
        rewatched_movies = None
        if df_watched_enriched is not None:
            df_rewatch = df_diary[df_diary['Rewatch'] == True]

            if df_rewatch.empty:
                return []

            df_movies_rewatch = pandas.merge(
                df_rewatch,
                df_watched_enriched[['Name', 'Year', 'Poster']],
                on=['Name', 'Year'],
                how='left'
            ).sort_values(by='Rating', ascending=False)

            rewatched_movies = df_movies_rewatch[['Name', "Year", 'Poster', 'Rating']].to_dict(orient='records')

    return {
        "rewatch_profile": rewatch_profile,
        "rewatch_description": rewatch_description,
        "rewatched_movies": rewatched_movies
    }

def get_favorite_genre(df_watched_enriched):
    if df_watched_enriched is not None:
        common_genres = df_watched_enriched["Genres"].str.split(",").explode().str.strip()

        if not common_genres.empty:
            return common_genres.value_counts().index[0]

        return None
    else:
        return None

def get_favorite_director(df_watched_enriched):
    if df_watched_enriched is not None:
        common_directors = df_watched_enriched["Directors"].str.split(",").explode().str.strip()

        if not common_directors.empty:
            return common_directors.value_counts().index[0]
        return None
    else:
        return None

def get_context(df_watched, df_diary, df_ratings, df_watched_enriched=None):
    total_movies = {"label": "Filmes Assistidos", "value": get_total_movies(df_watched)}
    favorite_day = {"label": "Dia de cinema", "value": get_favorite_day(df_diary)}
    favorite_decade = {"label": "Década favorita", "value": get_favorite_decade(df_ratings)}
    average_rating = {"label": "Média de avaliação", "value": get_average_rating(df_ratings)}
    favorite_genre = {"label": "Gênero favorito", "value": get_favorite_genre(df_watched_enriched)}
    favorite_director = {"label": "Diretor Favorito", "value": get_favorite_director(df_watched_enriched)}

    metric_list = [total_movies, favorite_day, favorite_decade, average_rating, favorite_genre, favorite_director]

    streak_context = get_streak_context(df_diary, df_watched_enriched)
    rewatch_context = get_rewatch_context(df_diary, df_watched_enriched)

    return {
        "metric_list": metric_list,
        "streak_context": streak_context,
        "rewatch_context": rewatch_context
    }
