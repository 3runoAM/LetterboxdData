import os
import numpy as np
import pandas as pd
import plotly.express as px
from sqlalchemy import func

from app import data_base
from app.config import STOPWORDS_OVERVIEW
from wordcloud import WordCloud, STOPWORDS
from PIL import Image, ImageOps

from app.models import WatchLog, Movie


def plot_rewatch_rate():
    result = (data_base.session.query(
        WatchLog.is_rewatch.label("is_rewatch"),
        func.count(WatchLog.id).label("count")
    )
              .group_by(WatchLog.is_rewatch)
              .all())

    rewatches = []
    for rewatch in result:
        rewatch_type = "Rewatch" if rewatch.is_rewatch else "First time"
        rewatches.append({"Rewatch": rewatch_type, "Amount": rewatch.count})

    fig = px.pie(rewatches, values="Amount", names="Rewatch", color="Rewatch",
                 color_discrete_map={"Rewatch": "#f37b01", "First time": "#3eb7eb"}, hole=0.4)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
    )

    fig.update_traces(
        texttemplate="%{percent:.1%}",
    )

    return fig.to_html(full_html=False)


def plot_overview_wordcloud():
    try:
        result = (data_base.session.query(Movie.overview.label("overview"))
                  .all())

        overviews_joined = " ".join([overview.overview for overview in result])

        stopwords = set(STOPWORDS)
        stopwords.update(STOPWORDS_OVERVIEW)

        image = Image.open("app/static/masks/letterboxd_logo_mask.png").convert("L")
        mask = np.array(image)

        wordcloud = WordCloud(
            background_color=None,
            mode="RGBA",
            color_func=lambda *args, **kwargs: "#A9BBCC",
            stopwords=stopwords,
            max_font_size=100,
            min_font_size=20,
            mask=mask,
            font_path="app/static/fonts/Yantramanav-Regular.ttf"
        ).generate(overviews_joined.capitalize())

        wordcloud.to_file("app/static/images/overview_cloud.png")
    except Exception as e:
        print(f"ERRO AO GERAR WORD CLOUD: {e.with_traceback(e.__traceback__)}")


def plot_movie_map():
    result = data_base.session.query(
        Movie.country,
        func.count(Movie.id).label("count")
    ).filter(Movie.country.isnot(None)) \
        .group_by(Movie.country) \
        .all()

    country_counts = []
    for country, count in result:
        country_counts.append({"Country": country, "Count": count})

    fig = px.scatter_geo(country_counts, locations="Country", locationmode="country names", size="Count", color="Count",
                         hover_name="Country", size_max=40,
                         color_continuous_scale=[[0.0, "#fc7e00"], [0.5, "#3fbcf2"], [1.0, " #00d94f"]],
                         template="plotly_dark")

    fig.update_geos(showcoastlines=True, coastlinecolor="#edeff1", showland=True, landcolor="#A9BBCC", showocean=False,
                    showlakes=False, bgcolor="rgba(0,0,0,0)", projection_type="natural earth")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False)

    return fig.to_html(full_html=False)


def plot_time_lag_per_period(watched_movies, time_lag_averages):
    def plot_time_lag(movies, time_lag_average):
        data = [
            {
                "title": movie["name"],
                "release_year": movie["year"],
                "time_lag": movie["time_lag"]
            } for movie in movies
        ]

        if not data:
            return None

        fig = px.scatter(
            data,
            x="release_year",
            y="time_lag",
            hover_name="title",
            color="time_lag",
            color_continuous_scale=[[0.0, "#fc7e00"], [0.5, "#3fbcf2"], [1.0, "#00d94f"]],
            labels={'release_year': 'Movie Release Year', 'time_lag': 'Years Until Watched'}
        )

        fig.update_traces(
            marker=dict(
                size=14,
                opacity=0.85,
                line=dict(width=1.5, color='#A9BBCC')
            )
        )

        years = [movie.get("year") for movie in movies if movie.get("year")]
        min_year = min(years) if years else 1900
        current_year = 2026
        fig.add_shape(
            type="line",
            x0=min_year, y0=current_year - min_year,
            x1=current_year, y1=0,
            line=dict(color="#A9BBCC", width=1.5, dash="dash"),
            layer="below"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff"),
            coloraxis_showscale=False,
            xaxis=dict(
                title="Movie Release Year",
                showgrid=False,
                linecolor="#A9BBCC",
                autorange = "reversed"
            ),
            yaxis=dict(
                title="Years Until You Watched It",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(0,0,0,0)"
            ),
            margin={"r": 20, "t": 40, "l": 20, "b": 20}
        )

        fig.add_hline(
            y=time_lag_average,
            line_dash="dot",
            line_width=2,
            line_color="#de1643",
            annotation_text=f"Average: {time_lag_average:.1f} years",
            annotation_position="bottom left",
            annotation_font=dict(color="#fff", size=15)
        )

        return fig.to_html(full_html=False)

    time_lag_week = plot_time_lag(watched_movies.get("watched_this_week"), time_lag_averages[0])
    time_lag_month = plot_time_lag(watched_movies.get("watched_this_month"), time_lag_averages[1])
    time_lag_year = plot_time_lag(watched_movies.get("watched_this_year"), time_lag_averages[2])

    return {
        "time_lag_week": time_lag_week,
        "time_lag_month": time_lag_month,
        "time_lag_year": time_lag_year
    }


def plot_points_graph_per_period(genre_category_points_list):
    def plot_points_graph(df_points):
        if df_points is None or len(df_points) == 0:
            return None

        fig = px.line_polar(
            df_points,
            r="values",
            theta="categories",
            line_close=True,
            template="plotly_dark"
        )

        fig.update_traces(
            fill="toself",
            fillcolor="rgba(0,217,79, 0.5)",
            line=dict(color="#3fbcf2", width=2),
            mode="lines+markers",
            marker=dict(color="#fc7e00", size=6)
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff"),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    showline=False,
                    showticklabels=False,
                    ticks="",
                    gridcolor="rgba(0, 0, 0, 0)",
                    range=[0, 50]
                ),
                angularaxis=dict(
                    visible=True,
                    showline=False,
                    showgrid=True,
                    gridcolor="rgba(169, 187, 204, 0.15)",
                    gridwidth=1,
                    tickfont=dict(color="#A9BBCC", size=16, family="app/static/fonts/Yantramanav-Regular.ttf")
                )
            )
        )
        return fig.to_html(full_html=False)

    for genre_category_points in genre_category_points_list:
        print(genre_category_points)

    df_week = pd.DataFrame(genre_category_points_list[0]) if genre_category_points_list[0]["categories"] is not None else None
    df_month = pd.DataFrame(genre_category_points_list[1]) if genre_category_points_list[1]["categories"] is not None else None
    df_year = pd.DataFrame(genre_category_points_list[2]) if genre_category_points_list[2]["categories"] is not None else None

    points_graph_week = plot_points_graph(df_week)
    points_graph_month = plot_points_graph(df_month)
    points_graph_year = plot_points_graph(df_year)

    return {
        "points_graph_week": points_graph_week,
        "points_graph_month": points_graph_month,
        "points_graph_year": points_graph_year,
    }
