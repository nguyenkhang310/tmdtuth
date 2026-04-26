#!/bin/bash
cd "$(dirname "$0")" || exit 1

if [ ! -f ".env" ]; then
  echo "[LOI] Khong tim thay file .env trong thu muc project."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

read -r -p "Dan link https cua ngrok vao day roi nhan Enter: " PUBLIC_URL

if [ -z "$PUBLIC_URL" ]; then
  echo "[LOI] Ban chua nhap PUBLIC_URL."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

PUBLIC_URL_INPUT="$PUBLIC_URL" perl -0pi.bak -e 's/^PUBLIC_URL=.*$/PUBLIC_URL=$ENV{PUBLIC_URL_INPUT}/m' .env

if ! grep -q '^PUBLIC_URL=' .env; then
  printf '\nPUBLIC_URL=%s\n' "$PUBLIC_URL" >> .env
fi

rm -f .env.bak

echo
echo "Da cap nhat PUBLIC_URL=${PUBLIC_URL}"
echo "Bay gio quay lai web va thanh toan MoMo/VNPAY nhu binh thuong."
read -r -p "Nhan Enter de dong cua so..."
