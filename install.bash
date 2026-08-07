#!/bin/bash

# 1. Paket Güncellemeleri ve Kurulumlar
echo "[+] Paketler güncelleniyor ve gerekli araçlar (SSH, Bore) kuruluyor..."
pkg update -y && pkg upgrade -y
pkg install openssh bore -y

# 2. Şifreyi Otomatik Tanımlama
echo "[+] SSH şifresi otomatik ayarlanıyor..."
echo -e "Mik123321kiM\nMik123321kiM" | passwd > /dev/null 2>&1

# 3. SSH Servisini Başlat
if pgrep -x "sshd" > /dev/null; then
    echo "[+] SSH servisi zaten aktif."
else
    sshd
    echo "[+] SSH servisi 8022 portunda başlatıldı."
fi

# 4. Bilgileri Göster ve Bore Tünelini Başlat
echo "=================================================="
echo "[+] SSH Kullanıcı Adı : icym"
echo "[+] SSH Şifresi       : Mik123321kiM"
echo "[+] Yerel Port        : 8022"
echo "=================================================="
echo "[+] Bore TCP Tüneli 'bore.pub' sunucusuna bağlanıyor..."
echo "[!] Ekrana gelen 'listening at bore.pub:XXXXX' satırındaki XXXXX port numarasını not alın."
echo "=================================================="

bore local 8022 --to bore.pub
