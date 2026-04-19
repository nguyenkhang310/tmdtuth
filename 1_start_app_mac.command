#!/bin/bash
cd "$(dirname "$0")" || exit 1

PORT=5011
PYTHON_EXE=""

if [ -x "venv/bin/python" ]; then
  PYTHON_EXE="venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_EXE="python3"
fi

if [ -z "$PYTHON_EXE" ]; then
  echo "[LOI] Khong tim thay Python. Hay cai Python hoac tao venv truoc."
  read -r -p "Nhan Enter de dong cua so..."
  exit 1
fi

echo "==============================================="
echo "Dang chay UTH Store tai http://127.0.0.1:${PORT}"
echo "Mo file 2_start_ngrok_mac.command o cua so khac neu can MoMo/VNPAY"
echo "==============================================="
echo

PORT="$PORT" "$PYTHON_EXE" app.py
read -r -p "Nhan Enter de dong cua so..."
