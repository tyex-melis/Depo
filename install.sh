#!/data/data/com.termux/files/usr/bin/bash

# 1. Gerekli Tüm Paketleri Kur (SSH, Ngrok, Stunnel, OpenSSL)
pkg update -y && pkg install openssh ngrok stunnel openssl -y

# 2. SSH Şifresini Ayarla
echo -e "Mik123321kiM\nMik123321kiM" | passwd > /dev/null 2>&1

# 3. SSL/TLS Çözücü (Stunnel) Yapılandırması
mkdir -p $PREFIX/etc/stunnel
if [ ! -f $PREFIX/etc/stunnel/stunnel.pem ]; then
    openssl req -new -x509 -days 365 -nodes -out $PREFIX/etc/stunnel/stunnel.pem -keyout $PREFIX/etc/stunnel/stunnel.pem -subj "/CN=whatsapp.com" > /dev/null 2>&1
fi

cat << 'EOF' > $PREFIX/etc/stunnel/stunnel.conf
pid =
cert = /data/data/com.termux/files/usr/etc/stunnel/stunnel.pem
[openssh]
accept = 8443
connect = 127.0.0.1:8022
EOF

# 4. Ngrok Token Ayarla
mkdir -p ~/.config/ngrok
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    ngrok config add-authtoken 2erbHenVYp6NFQNarCcluso12ZW_42VFtTZQg8Lm4jm2CN1Jt
fi

# 5. Servisleri Çalıştır (SSH + Stunnel)
if ! pgrep -x "sshd" > /dev/null; then
    sshd
fi

pkill stunnel > /dev/null 2>&1
stunnel $PREFIX/etc/stunnel/stunnel.conf

# 6. Ngrok Tünelini Stunnel Portuna (8443) Yönlendir
echo "[+] SSL/TLS Tüneli Başlatılıyor..."
ngrok tcp 8443
