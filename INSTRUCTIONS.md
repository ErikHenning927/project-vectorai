# Guia de Instalação e Execução Geral 🚀

Siga este passo a passo para colocar o VectorAI rodando do zero no seu ambiente.

## 1. Organização do Git
Se você acabou de clonar e quer padronizar sua branch principal:
```bash
git checkout master
git branch -m master main
git merge homolog  # Trazer as funcionalidades prontas
```

## 2. Configuração do Banco Vetorial (Pinecone)
O sistema precisa de um lugar para guardar as "impressões digitais" (embeddings) das imagens.
1. Crie um índice no [Pinecone](https://app.pinecone.io).
2. **IMPORTANTE:** Configure com **512 dimensões** e métrica **Cosine**.
3. Copie sua API Key.

## 3. Variáveis de Ambiente
Crie o arquivo `./embedding-svc/.env` (use o `.env.example` como guia) e preencha:
- `PINECONE_API_KEY=sua_chave_aqui`
- `PINECONE_INDEX_NAME=vectorai-index`

## 4. Executando o Projeto (Docker)
Na raiz do projeto, suba todos os containers:
```bash
docker compose up --build
```
*O primeiro build pode demorar alguns minutos pois o Docker baixará o modelo CLIP da OpenAI (aprox. 350MB).*

## 5. Populando os Dados (Seed)
Com o sistema rodando, insira os produtos iniciais no banco:
```bash
docker exec -it vectorai-backend python scripts/seed.py
```

## 6. Acesso pelo Celular (Testes Reais)
Para testar a câmera e a responsividade no seu celular:
1. Certifique-se que o Docker está rodando na porta 80.
2. No seu PC, inicie o ngrok:
   ```bash
   ngrok http 80
   ```
3. Abra a URL `https://...` gerada no navegador do seu celular.

---

### 🛡️ Troubleshooting (Solução de Problemas)
- **Erro de Memória:** Se o backend travar, certifique-se que o Docker tem pelo menos 4GB de RAM disponíveis (modelos de IA são pesados).
- **Câmera não abre:** O acesso à câmera em celulares exige **HTTPS**. Use sempre o link seguro do ngrok para testar.
- **Porta 80 ocupada:** Se você já tiver outro servidor (Apache/IIS) rodando na porta 80, mude o mapeamento no `docker-compose.yml`.
