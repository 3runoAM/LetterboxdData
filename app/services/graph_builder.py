import os
import numpy as np
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
