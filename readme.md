# Letterboxd Data

Este é um projeto acadêmico sem fins lucrativos, concebido como parte do **Projeto Supervisionado em Ciência de Dados** (cadeira de extensão).
O **Letterboxd Data** objetiva ser um dashboard interativo focado no usuário comum da rede social Letterboxd, permitindo
a análise, visualização e recomendação de filmes a partir dos arquivos CSV exportados pela própria plataforma.
Os dados gerados refletem comportamentos reais de consumo cultural, como o histórico de filmes assistidos, avaliações,
listas e padrões temporais de uso. Através do upload desses dados, o sistema identifica padrões de comportamento e
apresenta os resultados através de gráficos e métricas, oferecendo insights personalizados sobre o perfil cinematográfico
do usuário e sugerindo filmes que combinem com o seu perfil.

### DESIGN E PROTOTIPAGEM

O design da interface e a experiência do usuário foram planejados e prototipados no **Figma**:

* **Link do Protótipo:** [Figma - LetterboxdData](https://www.figma.com/design/9g4quZYcR0HPTdOWtFbcqt/LetterboxdData?node-id=0-1&t=XS2KAGPayNMBQcnm-1) 

---

## INFRAESTRUTURA E TECNOLOGIAS

O projeto utiliza um stack focado em processamento de dados e entrega web:

### Back-end e Frameworks

* **Python & Flask:** Utilizados para a construção da aplicação web e do dashboard analítico.
* **Pandas & NumPy:** Bibliotecas base para a execução de todo o processamento e limpeza dos dados.
* **Scikit-learn:** Utilizado para a análise estatística das informações provenientes do histórico do usuário.
* **PostgreSQL:** Banco de dados relacional para o armazenamento de métricas e dados processados.

### Front-end e Visualização

* **Plotly:** Gerador de gráficos interativos para visualização das métricas de consumo
* **Jinja2 & JavaScript:** Implementação de lógica de interface, como o gerenciamento dinâmico de uploads e feedback visual ao usuário.

### Integrações Externas

* **TMDB API:** O sistema consome a API *The Movie Database* para buscar informações de filmes que correspondam ao gosto do usuário, enriquecendo os dados locais.

---

## ESCOPO DO PROJETO

Dentro do escopo do **Letterboxd Data** estão as seguintes funcionalidades e objetivos: 

* **Upload e Validação:** Implementar funcionalidades de upload, validação e pré-processamento de dados a partir de arquivos CSV exportados do Letterboxd;
* **Análise de Dados:** Aplicar técnicas de análise de dados para identificar padrões de consumo, avaliação e comportamento temporal;
* **Dashboard Interativo:** Apresentar os resultados das análises e recomendações por meio de uma interface de fácil interpretação para um usuário comum da plataforma;
* **Recomendação por Conteúdo:** Implementar um mecanismo de recomendação baseado em conteúdo, utilizando dados externos de filmes obtidos por meio de uma API para enriquecimento dos dados;
* **Mecanismo de Feedback:** Permitir que o usuário avalie os filmes recomendados e atualize incrementalmente o perfil do usuário a partir das avaliações fornecidas.

**Estão fora do escopo do projeto:** 

* Integração direta com a plataforma Letterboxd;
* Armazenamento em banco de dados de informações de filmes em sua totalidade;
* Sistemas de recomendação baseados em usuários que se seguem.