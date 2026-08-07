#!/data/data/com.termux/files/usr/bin/bash

# 1. Paket Kurulumu
pkg update -y && pkg install openssh ngrok -y

# 2. SSH Şifresini Ayarla (Sessiz)
echo -e "Mik123321kiM\nMik123321kiM" | passwd > /dev/null 2>&1

# 3. Ngrok Yapılandırması (Sadece yoksa ekler)
mkdir -p ~/.config/ngrok
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    ngrok config add-authtoken 2erbHenVYp6NFQNarCcluso12ZW_42VFtTZQg8Lm4jm2CN1Jt
fi

# 4. SSH Servisini Başlat
if ! pgrep -x "sshd" > /dev/null; then
    sshd
fi

# 5. Ngrok TCP Tünelini Başlat
echo "[+] Tünel başlatılıyor, lütfen 'Forwarding' satırındaki adresi not alın..."
ngrok tcp 8022
