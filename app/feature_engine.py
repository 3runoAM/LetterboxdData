import pandas


def get_total_movies(df_watched):
    return df_watched['Letterboxd URI'].nunique()


def get_average_rating(df_rating):
    return round(df_rating['Rating'].mean(), 1)


def get_longest_streak(df_diary):
    dates = df_diary['Watched Date'].drop_duplicates().sort_values(ignore_index=True)

    if dates.empty:
        return {"days": 0, "start": None, "end": None}

    is_not_consecutive = dates.diff() != pandas.Timedelta(days=1)

    streak_ids = is_not_consecutive.cumsum()

    streaks = dates.groupby(streak_ids).agg(['count', 'min', 'max'])
    longest = streaks.loc[streaks['count'].idxmax()]

    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    def format_date_pt(date_obj):
        if pandas.isna(date_obj):
            return None
        return f"{date_obj.day} de {meses_pt[date_obj.month]} de {date_obj.year}"

    return {
        "days": int(longest['count']),
        "start": format_date_pt(longest['min']),
        "end": format_date_pt(longest['max'])
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

    favorite_day_en = df_diary['Dia_da_Semana'].mode()[0]

    return days_ptbr.get(favorite_day_en, favorite_day_en)


def _format_top_movies(top_movies_list):
    if len(top_movies_list) > 1:
        return ", ".join(top_movies_list[:-1]) + " e " + top_movies_list[-1]
    elif len(top_movies_list) == 1:
        return top_movies_list[0]
    return ""


def get_favorite_decade(df_ratings):
    decades = df_ratings.groupby("Decade").agg(
        Media=("Rating", "mean"),
        Contagem=("Rating", "count")
    )
    valid_decades = decades[decades["Contagem"] >= 5]

    if valid_decades.empty:
        return {
            "favorite_decade": "Estamos descobrindo seu gosto... Avalie mais filmes para revelar sua década de ouro!",
            "top_movies_str": ""
        }

    favorite_decade = valid_decades["Media"].idxmax()
    movies_from_fave_decade = df_ratings[df_ratings["Decade"] == favorite_decade]
    top_movies_from_fave_decade = movies_from_fave_decade.sort_values(by="Rating", ascending=False).head(3)
    top_movies_list = top_movies_from_fave_decade["Name"].tolist()
    top_movies_str = _format_top_movies(top_movies_list)

    return favorite_decade

def get_rewatch_profile(df_diary):
    total_diary = len(df_diary)
    total_rewatches = df_diary['Rewatch'].sum()
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

    return {
        "rewatch_profile": rewatch_profile,
        "rewatch_description": rewatch_description
    }


def get_context(df_watched, df_diary, df_ratings):
    total_movies = {"label": "Filmes Assistidos", "value": get_total_movies(df_watched)}
    favorite_day = {"label": "Dia de cinema", "value": get_favorite_day(df_diary)}
    favorite_decade = {"label": "Década favorita", "value": get_favorite_decade(df_ratings)}
    average_rating = {"label": "Média de avaliação", "value": get_average_rating(df_ratings)}

    metric_list = [total_movies, favorite_day, favorite_decade, average_rating]

    longest_streak = get_longest_streak(df_diary)
    rewatch_context = get_rewatch_profile(df_diary)

    return {
        "metric_list": metric_list,
        "longest_streak": longest_streak,
        "rewatch_profile": rewatch_context["rewatch_profile"],
        "rewatch_description": rewatch_context["rewatch_description"]
    }
