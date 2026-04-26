#!/bin/bash
cd "$(dirname "$0")" || exit 1

PORT=5011
NGROK_CMD=""
NGROK_CONFIG="$(pwd)/ngrok.local.yml"
WINDOWS_NGROK_FOUND=0

if [ -x "./ngrok" ]; then
  NGROK_CMD="./ngrok"
elif [ -f "./ngrok.exe" ]; then
  WINDOWS_NGROK_FOUND=1
elif [ -x "/opt/homebrew/bin/ngrok" ]; then
  NGROK_CMD="/opt/homebrew/bin/ngrok"
elif [ -x "/usr/local/bin/ngrok" ]; then
  NGROK_CMD="/usr/local/bin/ngrok"
elif command -v ngrok >/dev/null 2>&1; then
  NGROK_CMD="ngrok"
fi

if [ -z "$NGROK_CMD" ]; then
  echo "[LOI] Khong tim thay file ngrok."
  if [ "$WINDOWS_NGROK_FOUND" -eq 1 ]; then
    echo "Phat hien ngrok.exe trong project, nhung day la ban Windows nen macOS khong chay duoc."
  fi
  echo "Hay cai ngrok cho macOS bang Homebrew hoac copy dung file ngrok ban macOS vao cung thu muc voi project nay."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

if [ ! -f "$NGROK_CONFIG" ]; then
  echo "==============================================="
  echo "Chua co file cau hinh ngrok rieng cho project nay."
  echo "Nhap authtoken de tao file $NGROK_CONFIG"
  echo "Lay authtoken tai: https://dashboard.ngrok.com/get-started/your-authtoken"
  echo "==============================================="
  read -r -p "Authtoken: " NGROK_TOKEN
  if [ -z "$NGROK_TOKEN" ]; then
    echo "[LOI] Ban chua nhap authtoken."
    read -r -p "Nhan Enter de dong cua so..."
    exit 1
  fi
  "$NGROK_CMD" config add-authtoken "$NGROK_TOKEN" --config "$NGROK_CONFIG"
  if [ $? -ne 0 ]; then
    echo "[LOI] Khong tao duoc file cau hinh ngrok rieng cho project."
    read -r -p "Nhan Enter de dong cua so..."
    exit 1
  fi
  echo
  echo "Da luu authtoken vao $NGROK_CONFIG"
  echo
fi

if ! "$NGROK_CMD" config check --config "$NGROK_CONFIG" >/dev/null 2>&1; then
  echo "[LOI] File cau hinh ngrok cua project dang loi: $NGROK_CONFIG"
  echo "Hay xoa file do roi chay lai script nay de nhap authtoken moi."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

echo "==============================================="
echo "Dang mo ngrok cho cong ${PORT}"
echo "Sau khi thay dong Forwarding, copy link https://...ngrok..."
echo "Roi chay file 3_cap_nhat_public_url_mac.command"
echo "==============================================="
echo

"$NGROK_CMD" http "$PORT" --config "$NGROK_CONFIG"
read -r -p "Nhan Enter de dong cua so..."
