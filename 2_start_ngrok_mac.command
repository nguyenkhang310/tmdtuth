#!/bin/bash
cd "$(dirname "$0")" || exit 1

PORT=5011
NGROK_CMD=""

if [ -x "./ngrok" ]; then
  NGROK_CMD="./ngrok"
elif command -v ngrok >/dev/null 2>&1; then
  NGROK_CMD="ngrok"
fi

if [ -z "$NGROK_CMD" ]; then
  echo "[LOI] Khong tim thay file ngrok."
  echo "Cach de nhat: copy file ngrok vao cung thu muc voi project nay va dat ten la ngrok."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

echo "==============================================="
echo "Dang mo ngrok cho cong ${PORT}"
echo "Sau khi thay dong Forwarding, copy link https://...ngrok..."
echo "Roi chay file 3_cap_nhat_public_url_mac.command"
echo "==============================================="
echo

"$NGROK_CMD" http "$PORT"
read -r -p "Nhan Enter de dong cua so..."
