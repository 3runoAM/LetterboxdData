# INTRODUÇÃO E DEFINIÇÃO DO PROJETO

O Letterboxd é uma rede social global voltada à discussão e à descoberta de filmes a partir de sua comunidade de
usuários que permite a avaliação de filmes com uma nota entre 0,5 e 5 estrelas. Os dados gerados por esta plataforma
refletem comportamentos reais de consumo cultural dos milhões de usuários ativos (17 milhões em 2024), como o histórico
de filmes assistidos, avaliações, listas e padrões temporais de uso.

Tendo isso em mente, o presente projeto objetiva criar um dashboard analítico-exploratório chamado LetterboxdData, que,
diferente de um dashboard operacional, busca identificar tendências de consumo e apresentá-las por meio de uma narrativa
de dados voltada ao usuário final.

O LetterboxData poderia funcionar como um módulo de análise e exibição de dados integrada a própria plataforma do
Letterboxd, com mínimas mudanças, tendo acesso aos dados em tempo real dos usuários e dos metadados dos filmes que a
plataforma gere; como isso não é possível, a ingestão dos dados é simulada pelo envio de arquivos csv, exportados
diretamente da rede social para o LetterboxdData, que são processados, armazenados em um banco de dados relacional e,
por fim, analisados e exibidos por meio de uma interface interativa, voltada ao Data Storytelling.

# FRAMEWORK E TECNOLOGIAS

O Letterboxd Data utiliza o ecossistema Python/Flask para construir uma aplicação web, monolítica, com as bibliotecas
Pandas, NumPy e Collections para limpeza e processamento dos dados; assim como dependências externas, a exemplo do
Plotly, para criação de gráficos interativos; WordCloud e Pillow, para geração de nuvem de palavras em formato
específico; SQLAlchemy, que abstrai todas as interações com o banco de dados; e Jinja2 para exibição no front-end.

Outras ferramentas externas utilizadas foram: PostgreSQL, como banco de dados relacional que armazena os dados após o
processamento (em entidades como Movie, WatchLog, Genre e Director); API da The Movie DataBase para coleta de metadados
dos filmes (como pôsteres, diretores e gêneros); Tenacity, para controle de tentativas automáticas em requisições à API;
e ThreadPoolExecutor para paralelizar buscas e otimizar o desempenho.

# TÉCNICAS DE NARRATIVA, ANÁLISE E VISUALIZAÇÃO DE DADOS

O dashboard é dividido em três rotas, cada uma trazendo um âmbito diferente do espectro de gostos do usuário, e
aplicando sobre a totalidade, ou um parcela, dos dados técnicas de análise e a narrativa de dados como agrupamento de
intervalos, cálculo de moda/frequência, média aritmética, análise geoespacial, gamificação, frases dinâmicas, e um
design focado na clareza das informações, na redução da carga cognitiva do usuário, espelhando o design do Letterboxd.

## ROTA PROFILE

A rota Profile, visa responder a pergunta “Quem é o usuário em relação ao seu gosto por filmes?” e leva em consideração
os dados como um todo, da primeira à última avaliação.

## ROTA CURRENT VIBE

A rota Current Vibe, visa responder a pergunta “O que o usuário tem consumido ultimamente?” e leva em consideração um
recorte de tempo mais recente: a semana atual, o mês atual e o ano atual, aplicando basicamente as mesmas técnicas de
análise, visualização e narrativa de dados.

## ROTA BADGES

A rota Badges, foi construída pensando inteiramente no aspecto da gamificação utilizando as personas definidas pelas
diversas características dos dados como um todo, sem recorte temporal. Algumas personas já foram detalhadas nas rotas
descritas anteriormente neste relatório, tendo isso em vista, nesta seção serão descritas apenas as personas exclusivas
desta rota, que acompanham uma imagem de um filme relacionado ao tipo da persona.
