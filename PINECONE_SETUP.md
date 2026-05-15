# Configuração do Pinecone (Vector Database) 🌲

Para que a busca visual funcione, você precisa configurar um índice no Pinecone que seja compatível com os vetores gerados pelo modelo CLIP.

## 1. Criar Conta e API Key
1. Acesse [pinecone.io](https://www.pinecone.io/) e crie uma conta gratuita.
2. No painel, vá em **API Keys** e crie uma nova chave.
3. Copie essa chave e cole no seu arquivo `embedding-svc/.env` na variável `PINECONE_API_KEY`.

## 2. Criar o Índice (Manual ou via Console)
No painel do Pinecone, clique em **"Create Index"** e use as seguintes configurações:

- **Index Name:** `vectorai-index` (ou o nome que você definiu no seu `.env`)
- **Dimensions:** `512`  *(Obrigatório para o modelo ViT-B-32)*
- **Metric:** `Cosine`
- **Cloud Provider:** `AWS` (ou sua preferência)
- **Region:** `us-east-1` (ou a mais próxima disponível para o plano gratuito)
- **Capacity Mode:** `Serverless`

## 3. Estrutura dos Metadados
O sistema envia metadados para o Pinecone para facilitar a exibição no frontend. O índice aceita automaticamente estes campos:
- `name`: Nome do produto
- `url`: Link da imagem do produto
- `reference`: Código de referência
- `category`: Categoria do item

## 4. Verificação
Após criar o índice e configurar a API Key no `.env`, o backend se conectará automaticamente ao iniciar. Você verá o seguinte log no console:
`INFO - Conectado ao índice Pinecone: vectorai-index`

---

### 💡 Dica: Por que 512 dimensões?
O modelo **CLIP ViT-B-32** da OpenAI, que estamos utilizando no microserviço de IA, transforma qualquer imagem em uma lista de 512 números decimais (o "embedding"). Se o índice no Pinecone tiver um número diferente de dimensões, as buscas retornarão erro de compatibilidade.
