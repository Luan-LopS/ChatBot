#!/bin/bash
set -e

domains=(SEU_DOMINIO_AQUI.com www.SEUDOMINIO_AQUI.com)
email="seu-email@dominio.com"
rsa_key_size=4096
data_path="./nginx/ssl"

command -v docker-compose >/dev/null 2>&1 || { echo >&2 "docker-compose não está instalado. Abortando."; exit 1; }

if [ -d "$data_path/live/${domains[0]}" ]; then
  echo "⚠️ Certificado já existe para ${domains[0]}"
  exit 0
fi

echo "### Criando pastas para certificado..."
mkdir -p "$data_path/www"
mkdir -p "$data_path/conf"

echo "### Baixando TLS configs recomendadas..."
curl -s https://raw.githubusercontent.com/certbot/certbot/main/certbot/certbot/ssl-dhparams.pem > "$data_path/ssl-dhparams.pem"
curl -s https://raw.githubusercontent.com/certbot/certbot/main/certbot/certbot/options-ssl-nginx.conf > "$data_path/options-ssl-nginx.conf"

echo "### Iniciando nginx para validação ACME..."
docker-compose up --force-recreate --no-deps -d nginx

echo "### Solicitando certificados com Certbot..."
docker run --rm \
  -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
  -v "$(pwd)/nginx/ssl/www:/var/www/certbot" \
  certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$email" \
    --agree-tos \
    --no-eff-email \
    --rsa-key-size $rsa_key_size \
    -d "${domains[@]}"

echo "### Reiniciando tudo com HTTPS ativo..."
docker-compose down
docker-compose up -d
