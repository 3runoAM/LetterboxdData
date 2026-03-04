import plotly.express as px

def plot_volume_por_periodo(df_diary):
    volume = df_diary.groupby('Ano-Mes').size().reset_index(name='Filmes')

    fig = px.bar(volume, x='Ano-Mes', y='Filmes', title='Volume de Filmes por Mês',
                 color_discrete_sequence=['#00B020'])

    fig.update_layout(xaxis_tickangle=-45)
    return fig.to_html(full_html=False)

def plot_dia_semana(df_diary):
    ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    nomes_br = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    volume = df_diary['Dia_da_Semana'].value_counts().reindex(ordem_dias).reset_index()
    volume.columns = ['Dia', 'Quantidade']
    volume['Dia'] = nomes_br

    fig = px.bar(volume, x='Dia', y='Quantidade', title='Dia da Semana Favorito', color_discrete_sequence=['#00d94f'])
    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff')
    )
    return fig.to_html(full_html=False)


def plot_evolucao_gosto(df_diary):
    evolucao = df_diary.groupby('Ano_Assistido')['Rating'].mean().reset_index()
    fig = px.line(evolucao, x='Ano_Assistido', y='Rating', markers=True,
                  title='Evolução do Gosto (Média de Notas por Ano)')

    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )

    return fig.to_html(full_html=False)


def plot_taxa_rewatch(df_diary):
    rewatches = df_diary['Rewatch'].value_counts().reset_index()
    rewatches.columns = ['Rewatch', 'Quantidade']
    rewatches['Rewatch'] = rewatches['Rewatch'].map({True: 'Revistos', False: 'Inéditos'})

    fig = px.pie(rewatches, values='Quantidade', names='Rewatch', title='Taxa de Rewatch',
                 color='Rewatch', color_discrete_map={'Revistos': '#FF8000', 'Inéditos': '#2C3440'})

    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )

    return fig.to_html(full_html=False)


def plot_time_lag(df_diary):

    lag_valido = df_diary[df_diary['Time_Lag'] >= 0]

    fig = px.histogram(lag_valido, x='Time_Lag', nbins=50,
                       title='Time Lag (Anos entre o Lançamento e a Visualização)',
                       labels={'Time_Lag': 'Anos de Atraso'})

    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff'),
        # Remove as linhas de grade para um visual mais limpo (opcional)
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )

    return fig.to_html(full_html=False)

def get_max_streak(df_streaks):
    max_dias = df_streaks['Dias_Consecutivos'].max()
    return max_dias

def plot_distribuicao_notas(df_ratings):
    dist = df_ratings['Rating'].value_counts().sort_index().reset_index()
    dist.columns = ['Estrelas', 'Quantidade']

    fig = px.bar(dist, x='Estrelas', y='Quantidade', title='Curva de Notas (Distribuição Geral)',
                 color_discrete_sequence=['#00B020'])
    # Força o eixo X a mostrar de 0.5 em 0.5
    fig.update_xaxes(dtick=0.5)
    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff'),
        # Remove as linhas de grade para um visual mais limpo (opcional)
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    return fig.to_html(full_html=False)


def plot_decada_ouro(df_ratings):
    decadas = df_ratings.groupby('Decade')['Rating'].mean().reset_index()
    fig = px.bar(decadas, x='Decade', y='Rating', title='Década de Ouro (Média de Nota por Década)',
                 color='Rating', color_continuous_scale='Viridis')
    # Força o eixo Y a ir só de 0 a 5
    fig.update_yaxes(range=[0, 5])
    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff'),
        # Remove as linhas de grade para um visual mais limpo (opcional)
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    return fig.to_html(full_html=False)