#!/usr/bin/env bash
# CyberComp-Gov — Ubuntu 22.04/24.04 VPS'ga o‘rnatish
# Ishlatish (loyiha papkasida): sudo bash deploy/vps-setup.sh
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo ">> Docker o‘rnatilmoqda..."
  curl -fsSL https://get.docker.com | sh
fi

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$(openssl rand -hex 32)/" .env
  sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 16)/" .env
  IP=$(curl -fsS https://api.ipify.org || hostname -I | awk '{print $1}')
  sed -i "s#^PUBLIC_BASE_URL=.*#PUBLIC_BASE_URL=http://${IP}#" .env
  echo ">> .env yaratildi (JWT_SECRET va POSTGRES_PASSWORD tasodifiy)."
fi

if command -v ufw >/dev/null 2>&1; then
  ufw allow 22/tcp >/dev/null || true
  ufw allow 80/tcp >/dev/null || true
fi

docker compose up -d --build
docker compose ps
echo ">> Tayyor: $(grep ^PUBLIC_BASE_URL .env | cut -d= -f2)"
