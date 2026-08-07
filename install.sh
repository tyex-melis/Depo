#!/bin/bash

# 1. Paket Güncellemeleri ve Kurulumlar
echo "[+] Paketler güncelleniyor ve OpenSSH kuruluyor..."
pkg update -y && pkg upgrade -y
pkg install openssh -y

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

# 4. Bilgileri Göster ve Serveo Tünelini Başlat
echo "=================================================="
echo "[+] SSH Kullanıcı Adı : icym"
echo "[+] SSH Şifresi       : Mik123321kiM"
echo "[+] Yerel Port        : 8022"
echo "=================================================="
echo "[+] Serveo TCP Tüneli Bağlanıyor..."
echo "[!] Ekrana gelen port numarasını (Örn: serveo.net:12345) not alın."
echo "=================================================="

ssh -o StrictHostKeyChecking=no -R 0:localhost:8022 serveo.net
