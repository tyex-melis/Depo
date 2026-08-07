#!/bin/bash

# 1. Paket Güncelleme ve OpenSSH Kurulumu
echo "[+] Gerekli paketler kontrol ediliyor..."
pkg update -y && pkg upgrade -y
pkg install openssh -y

# 2. Şifreyi Otomatik Tanımlama
echo "[+] SSH şifresi ayarlanıyor..."
echo -e "Mik123321kiM\nMik123321kiM" | passwd > /dev/null 2>&1

# 3. SSH Servisini Başlat
if pgrep -x "sshd" > /dev/null; then
    echo "[+] SSH servisi zaten çalışıyor."
else
    sshd
    echo "[+] SSH servisi 8022 portunda başlatıldı."
fi

# 4. Bilgileri Göster ve Pinggy Tünelini Başlat
echo "=================================================="
echo "[+] SSH Kullanıcı Adı : icym"
echo "[+] SSH Şifresi       : Mik123321kiM"
echo "=================================================="
echo "[+] Pinggy Tüneli Başlatılıyor..."
echo "[!] Ekranda yeşil renkle çıkan 'tcp.pinggy.io:XXXXX' adresindeki XXXXX portunu not alın."
echo "=================================================="

ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8022 free@tcp.pinggy.io
