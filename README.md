# VectorAI - Busca Visual Inteligente 🚀

Sistema completo de busca visual de produtos utilizando Inteligência Artificial (CLIP), Vector Search (Pinecone) e uma interface moderna com Glassmorphism.

## 🏗️ Arquitetura do Sistema

O projeto é composto por três serviços principais containerizados com Docker:

1.  **Frontend (React + Vite):** Interface responsiva otimizada para dispositivos móveis, permitindo captura de fotos e comparação visual.
2.  **Backend (FastAPI):** Microserviço de IA que gera embeddings de imagens usando o modelo CLIP e realiza análise de avarias (Damage Detection).
3.  **Database (PostgreSQL):** Persistência de metadados e logs de operação.

---

## 🔄 Proxy Reverso e Gateway (Nginx)

Um dos destaques desta arquitetura é o uso do **Nginx como Proxy Reverso** dentro do container do frontend. 

### Por que usamos isso?
Originalmente, o Frontend e o Backend rodavam em portas diferentes (80 e 8000). Para acessar externamente via **ngrok** (que no plano gratuito permite apenas 1 túnel), teríamos um problema de conectividade.

### Como funciona:
Configuramos o Nginx para escutar na porta **80** e agir como um roteador:
-   **`/`**: Entrega os arquivos estáticos do aplicativo React.
-   **`/api/`**: Intercepta as chamadas e as repassa internamente para o container do backend (`http://embedding-svc:8000/`).

**Benefício:** Você só precisa abrir um túnel ngrok para a porta 80 (`ngrok http 80`) e tanto o site quanto a API funcionarão através da mesma URL, eliminando erros de CORS e Mixed Content no celular.

---

## 🚀 Como Rodar

### Pré-requisitos
- Docker e Docker Compose instalados.
- Chave de API do Pinecone configurada no arquivo `./embedding-svc/.env`.

### Iniciar o Projeto
Na raiz do projeto, execute:
```bash
docker compose up --build
```

### Acesso Externo (Celular/WiFi)
Para acessar do celular usando ngrok:
1.  No seu PC, rode: `ngrok http 80`
2.  Acesse a URL gerada (ex: `https://abcd-123.ngrok-free.app`) no navegador do seu celular.

---

## 🛠️ Tecnologias Utilizadas
- **IA:** OpenAI CLIP (ViT-B-32) para Similaridade e Zero-shot Classification.
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic.
- **Frontend:** React, TypeScript, TailwindCSS, Framer Motion, Lucide.
- **Infra:** Docker, Nginx, PostgreSQL, Pinecone.

---

## 📸 Funcionalidades
- **Busca por Similaridade:** Encontra o produto mais parecido na base de dados a partir de uma foto.
- **Detecção de Avaria:** Analisa se o item na foto possui danos físicos (quebras, riscos, etc).
- **Fluxo de Decisão:** Interface para decidir entre Devolução ou Salvado com base na análise de IA.
- **Comparação Visual:** Visualização lado a lado (Foto capturada vs Foto do banco) no modal de detalhes.
