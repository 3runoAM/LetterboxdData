def get_total_movies(df_watched):
    return df_watched['Letterboxd URI'].nunique()


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


def get_favorite_decade_context(df_ratings):
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

    return {
        "favorite_decade": favorite_decade,
        "top_movies_str": top_movies_str
    }


def get_rewatch_profile(df_diary):
    total_diary = len(df_diary)
    total_rewatches = df_diary['Rewatch'].sum()
    taxa_rewatch = (total_rewatches / total_diary) * 100 if total_diary > 0 else 0

    if taxa_rewatch > 40:
        rewatch_profile = "Guardião da Nostalgia"
        hero_title = f"Com {taxa_rewatch:.1f}% de filmes revistos, você tem filmes de conforto e ama revisitá-los. Por que arriscar se o clássico é garantido?"
    elif taxa_rewatch > 15:
        rewatch_profile = "Curador Equilibrado"
        hero_title = f"Sua taxa de rewatch é de {taxa_rewatch:.1f}%. Você desbrava o novo, mas nunca abandona as obras que marcaram sua vida."
    elif taxa_rewatch > 5:
        rewatch_profile = "Explorador"
        hero_title = f"Apenas {taxa_rewatch:.1f}% dos seus filmes são repetições. O mundo é grande demais para gastar tempo vendo a mesma coisa."
    else:
        rewatch_profile = "Caçador de Inéditos"
        hero_title = f"Você reassistiu filmes {taxa_rewatch:.1f}% das vezes! Você tem sede por novidade, reprise é uma palavra que não existe no seu dicionário"

    return {
        "rewatch_profile": rewatch_profile,
        "hero_title": hero_title
    }


def get_context(df_watched, df_diary, df_ratings):
    total_movies = get_total_movies(df_watched)
    favorite_day = get_favorite_day(df_diary)
    decade_context = get_favorite_decade_context(df_ratings)
    rewatch_context = get_rewatch_profile(df_diary)

    return {
        "total_movies": total_movies,
        "favorite_day": favorite_day,
        "favorite_decade": decade_context["favorite_decade"],
        "top_movies_str": decade_context["top_movies_str"],
        "rewatch_profile": rewatch_context["rewatch_profile"],
        "hero_title": rewatch_context["hero_title"]
    }