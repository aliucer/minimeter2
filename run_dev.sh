#!/bin/bash

# Renkler
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> MiniMeter2 Development Ortamı Hazırlanıyor...${NC}"

# 1. Virtual Environment Kontrolü
if [ ! -d "venv" ]; then
    echo ">>> Sanal ortam (venv) oluşturuluyor..."
    python3 -m venv venv
fi

# 2. Sanal ortamı aktif et
echo ">>> Sanal ortam aktif ediliyor..."
source venv/bin/activate

# 3. Paketleri yükle/güncelle
echo ">>> Gerekli paketler yükleniyor..."
pip install -r requirements.txt

# 4. Uygulamayı başlat
echo -e "${GREEN}>>> API Başlatılıyor... (Durdurmak için Ctrl+C)${NC}"
uvicorn api.main:app --reload
