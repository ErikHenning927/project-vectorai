# Embedding Microservice (VectorAI)

Este microserviço é responsável por gerenciar o processamento de embeddings de produtos e armazenamento em banco de dados vetorial, seguindo os princípios de **Clean Architecture**.

## 🚀 Tecnologias

- **Python 3.12**
- **FastAPI** (Framework web)
- **PostgreSQL** (Banco de dados relacional)
- **SQLAlchemy** (ORM)
- **Alembic** (Migrações de banco de dados)
- **OpenAI CLIP** (Modelo de Embedding)
- **Pinecone** (Banco de dados vetorial)
- **Docker & Docker Compose** (Containerização)

## 📁 Estrutura do Projeto

O projeto segue a Clean Architecture para manter a separação de interesses:

```text
embedding-svc/
├── app/
│   ├── api/             # Camada de Entrada (Controllers, Routes, Middlewares)
│   ├── application/     # Casos de Uso e DTOs
│   ├── domain/          # Entidades e Interfaces (Core do negócio)
│   └── infrastructure/  # Implementações externas (Database, External APIs)
│       └── database/
│           ├── migrations/ # Arquivos do Alembic
│           └── models.py   # Modelos SQLAlchemy
├── alembic.ini          # Configuração do Alembic
├── docker-compose.yml   # Orquestração de containers
└── Dockerfile           # Definição da imagem Docker
```

## 🛠️ Como Iniciar

### Pré-requisitos
- Docker e Docker Compose instalados.

### Rodando com Docker (Recomendado)

1. Clone o repositório e navegue até a pasta `embedding-svc`.
2. Configure o arquivo `.env` (use o `.env.example` como base).
3. Execute o comando:
   ```bash
   docker compose up --build
   ```
O serviço estará disponível em `http://localhost:8000`.

### Rodando Localmente (Desenvolvimento)

1. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor:
   ```bash
   uvicorn app.api.server:app --reload --port 8000
   ```

---

## 🗄️ Migrations (Alembic)

O projeto utiliza o Alembic para gerenciar o esquema do banco de dados de forma versionada, similar ao TypeORM.

### Comandos Comuns

#### Gerar uma nova migration automaticamente
Sempre que você alterar um modelo em `app/infrastructure/database/models.py`, gere uma nova migration:
```bash
# Dentro do container
docker exec -it embedding-svc alembic revision --autogenerate -m "descricao_da_mudanca"

# Ou localmente (com venv ativa)
alembic revision --autogenerate -m "descricao_da_mudanca"
```

#### Aplicar migrações
As migrações são aplicadas automaticamente no startup do container (via Dockerfile). Para aplicar manualmente:
```bash
# Dentro do container
docker exec -it embedding-svc alembic upgrade head

# Ou localmente
alembic upgrade head
```

#### Reverter migrações
```bash
# Reverter para a versão anterior
alembic downgrade -1
```

### Seeding (Dados Iniciais)

Para popular o banco de dados com dados de teste:

```bash
# Dentro do container
docker exec -it embedding-svc python scripts/seed.py

# Ou localmente
python scripts/seed.py
```

---

## ⚙️ Variáveis de Ambiente

As principais variáveis configuráveis no `.env`:

### Banco de Dados (PostgreSQL)
| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `DB_USER` | Usuário do Postgres | `postgres` |
| `DB_PASSWORD` | Senha do Postgres | `postgres` |
| `DB_HOST` | Host do banco (use `postgres` no docker) | `localhost` |
| `DB_PORT` | Porta do banco | `5432` |
| `DB_NAME` | Nome do banco | `vectorai` |

### Embedding & Vector Store
| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `EMBEDDING_MODEL` | Modelo CLIP a ser utilizado | `ViT-B-32` |
| `BATCH_SIZE` | Tamanho do batch para processamento | `32` |
| `PINECONE_API_KEY` | Chave de API do Pinecone | `-` |
| `PINECONE_INDEX_NAME` | Nome do índice no Pinecone | `vectorai-index` |

### API
| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `API_PORT` | Porta da API | `8000` |

---

## 🔗 Endpoints Principais (Swagger)

A documentação interativa da API está disponível em:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
