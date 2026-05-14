# Estágio de Build
FROM node:20-slim AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Estágio de Produção (Nginx)
FROM nginx:alpine

# Copiar build do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Configuração do Nginx com Proxy Reverso e Limite de Upload aumentado
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    
    # Aumentar limite de upload para 50MB (fotos de celular)
    client_max_body_size 50M;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy para o Backend
    location /api/ {
        proxy_pass http://embedding-svc:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Ajustes de timeout para processamento de IA
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
