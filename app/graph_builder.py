import os
import numpy as np
import plotly.express as px

from app.config import STOPWORDS_OVERVIEW
from wordcloud import WordCloud, STOPWORDS
from PIL import Image, ImageOps


def plot_rewatch_rate(df_diary):
    rewatches = df_diary["Rewatch"].value_counts().reset_index()
    rewatches.columns = ["Rewatch", "Amount"]

    rewatches["Rewatch"] = rewatches["Rewatch"].map({True: "Rewatch", False: "First time"})

    fig = px.pie(rewatches, values="Amount", names="Rewatch", color="Rewatch",
                 color_discrete_map={"Revistos": "#f37b01", "Inéditos": "#3eb7eb"}, hole=0.4)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
    )

    fig.update_traces(
        texttemplate="%{percent:.1%}",
    )

    return fig.to_html(full_html=False)


def plot_overview_wordcloud(df_watched_enriched):
    try:
        overviews_joined = " ".join(df_watched_enriched["Overview"].dropna())

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


def plot_movie_map(df_watched_enriched):
    country_counts = df_watched_enriched["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]

    fig = px.scatter_geo(country_counts, locations="Country", locationmode="country names", size="Count", color="Count",
                         hover_name="Country", size_max=40,
                         color_continuous_scale=[[0.0, "#fc7e00"], [0.5, "#3fbcf2"], [1.0, " #00d94f"]],
                         template="plotly_dark")

    fig.update_geos(showcoastlines=True, coastlinecolor="#edeff1", showland=True, landcolor="#A9BBCC", showocean=False,
                    showlakes=False, bgcolor="rgba(0,0,0,0)", projection_type="natural earth")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False)

    return fig.to_html(full_html=False)
