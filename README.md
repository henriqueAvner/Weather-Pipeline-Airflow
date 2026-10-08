# Pipeline Weather

Projeto de estudo desenvolvido para adquirir conhecimentos em **Apache Airflow**, usando um pipeline ETL de dados meteorológicos como exercício prático.

## Sobre o projeto

- Coleta dados da API OpenWeather para a consulta `Minas Gerais,BR`.
- Trata os dados com Pandas: normaliza o JSON, renomeia colunas e converte datas para o fuso `America/Sao_Paulo`.
- Salva os dados tratados em Parquet e carrega os registros na tabela `mg_weather` do PostgreSQL.
- Usa Docker Compose para executar o ambiente do Airflow.
- Orquestra as etapas com a DAG `weather_pipeline`: `extract → transform → load`.
- Possui agendamento a cada hora, duas novas tentativas em caso de falha e intervalo de cinco minutos entre tentativas.

O foco é praticar criação de DAGs, dependências entre tasks, agendamento, acompanhamento de logs e tratamento de falhas. Este é um ambiente de estudo local.

## Tecnologias

- Python, Pandas, Requests e SQLAlchemy.
- PostgreSQL.
- Apache Airflow 3.1.7.
- Docker e Docker Compose.

## Estrutura

```text
dags/weather_dag.py      # DAG e definição das tasks
src/extract_data.py     # Extração da API
src/transform_data.py   # Transformação dos dados
src/load_data.py        # Carga no PostgreSQL
config/                # Configuração do Airflow e variáveis do pipeline
data/                  # JSON extraído e arquivo Parquet
docker-compose.yaml    # Serviços e volumes do ambiente
```

## Como executar

### 1. Pré-requisitos

- Docker Desktop instalado e em execução, com suporte a containers Linux.
- PostgreSQL instalado na máquina, com um banco disponível para receber os dados.
- Uma chave de API do OpenWeather.
- Execute os comandos abaixo na pasta raiz do projeto.

### 2. Configure as variáveis

Crie um arquivo `.env` na raiz para configurar os containers:

```dotenv
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
_PIP_ADDITIONAL_REQUIREMENTS="pandas requests python-dotenv sqlalchemy psycopg2-binary pyarrow"
```

Neste ambiente de estudo, as dependências são instaladas ao iniciar os containers. O `pyarrow` permite ler e gravar arquivos Parquet.

Crie também `config/.env`, substituindo os exemplos pelos seus valores:

```dotenv
API_KEY=sua_chave_openweather
user=seu_usuario_postgres
password=sua_senha_postgres
database=weather_data
```

Os arquivos `.env` estão no `.gitignore` e não devem ser publicados com credenciais reais.

### 3. Prepare o banco

No PostgreSQL local, crie o banco definido em `config/.env`, caso ainda não exista:

```sql
CREATE DATABASE weather_data;
```

O código usa `host.docker.internal:5432` para conectar os containers ao PostgreSQL da máquina. O banco deve aceitar essa conexão, e o usuário informado precisa ter permissão para criar a tabela e inserir registros.

O serviço `postgres` do Compose é usado pelo próprio Airflow para seus metadados. A carga meteorológica, na configuração atual, usa o PostgreSQL da máquina.

### 4. Inicie o Airflow

```bash
docker compose up airflow-init
docker compose up -d
```

Aguarde a inicialização dos serviços. Para conferir o estado:

```bash
docker compose ps
```

### 5. Execute a DAG

1. Acesse `http://localhost:8080`.
2. Entre com o usuário e a senha definidos no `.env` da raiz.
3. Localize a DAG `weather_pipeline` e ative-a.
4. Clique em **Acionar** para iniciar uma execução manual.
5. Acompanhe as tasks `extract`, `transform` e `load`, verificando os logs.

O agendamento passa a valer a partir da data inicial definida na DAG: **8 de outubro de 2026**. Para executar em uma data anterior, ajuste `start_date` em `dags/weather_dag.py`.

### 6. Confira os dados

Conecte-se ao banco configurado usando o pgAdmin ou o `psql` e execute:

```sql
SELECT COUNT(*) FROM mg_weather;
SELECT * FROM mg_weather LIMIT 10;
```

A tabela é criada na primeira carga, caso não exista. Cada execução acrescenta registros; repetir uma carga pode gerar dados duplicados.

## Problemas comuns

- **`Connection refused` usando `localhost`:** dentro do container, esse endereço aponta para o próprio container. Para o PostgreSQL no Windows, use `host.docker.internal`, conforme `src/load_data.py`.
- **Erro de diretório ao salvar o Parquet:** o caminho deve ser `/opt/airflow/data/...`, com a barra inicial. A pasta `data` está compartilhada pelo Compose.
- **Task com falha:** após corrigir o problema, selecione a task na interface e use **Limpar Instância de Tarefa** para reexecutá-la.
- **`psql` não reconhecido no Windows:** adicione a pasta `bin` do PostgreSQL ao PATH ou execute o programa pelo caminho completo.

As pastas `dags` e `src` são montadas como volumes. Alterações nesses arquivos normalmente não exigem reiniciar os containers. Se alterar o `.env` da raiz ou a configuração dos serviços, execute novamente `docker compose up -d` para aplicar as mudanças.

## Encerrar o ambiente

```bash
docker compose down
```

Esse comando encerra os serviços e mantém o volume do banco de metadados do Airflow.
