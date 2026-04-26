# Huong dan chay MoMo va VNPAY bang ngrok

Tai lieu nay dung cho truong hop ban gui file `.zip` cho thanh vien trong nhom va muon moi nguoi co the tu chay thanh toan MoMo/VNPAY tren may cua ho.

## Vi sao phai can ngrok?

MoMo va VNPAY can mot dia chi `https` public de quay ve callback sau khi thanh toan. Project nay lay dia chi do tu bien `PUBLIC_URL` trong file `.env`.

Neu chi mo app bang `http://127.0.0.1:5011` ma khong co `PUBLIC_URL`, cac luong COD/chuyen khoan van dung, nhung MoMo/VNPAY se khong callback ve may dang chay app.

## Cach dong goi de gui cho nhom

Trong file zip, giu san cac file sau o thu muc goc project:

- `1_start_app_windows.bat`
- `2_start_ngrok_windows.bat`
- `3_cap_nhat_public_url_windows.bat`
- `1_start_app_mac.command`
- `2_start_ngrok_mac.command`
- `3_cap_nhat_public_url_mac.command`

Neu gui cho nguoi dung Windows, ban co the bo them `ngrok.exe` vao cung thu muc goc project.

Neu gui cho nguoi dung macOS, ban co the bo them file `ngrok` vao cung thu muc goc project.

## Quy trinh danh cho Windows

### Chuan bi lan dau

1. Giai nen file zip.
2. Dam bao may da co Python 3.
3. Mo `Command Prompt` trong thu muc project va cai thu vien neu day la lan dau:

```bat
py -3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py -3 seed.py
```

Neu may da co san moi truong `venv` dung duoc va database da duoc tao roi thi co the bo qua buoc nay.

4. Neu muon dung MoMo/VNPAY, copy `ngrok.exe` vao cung thu muc voi `app.py`.
5. Neu day la lan dau dung ngrok tren may do, mo Command Prompt va dang nhap authtoken cua ngrok:

```bat
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Neu ban chay `ngrok.exe` ngay trong thu muc project thi cung co the dung:

```bat
ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

### Cach chay moi lan

1. Double-click `1_start_app_windows.bat`.
2. Doi den khi thay app chay o `http://127.0.0.1:5011`.
3. Double-click `2_start_ngrok_windows.bat`.
4. Trong cua so ngrok, copy dong `Forwarding` co dang `https://xxxxx.ngrok-free.app`.
5. Double-click `3_cap_nhat_public_url_windows.bat`.
6. Paste link `https://...` vua copy vao va nhan `Enter`.
7. Mo trinh duyet vao `http://127.0.0.1:5011` va test thanh toan.

### Khi nao can chay lai buoc 3?

Can chay lai moi khi:

- Tat ngrok va mo lai.
- Nhan mot link ngrok moi.
- Chuyen sang may khac.

Khong can chay lai neu link ngrok van con song va ban chi reload app.

## Quy trinh danh cho macOS

### Chuan bi lan dau

1. Giai nen file zip.
2. Dam bao may da co Python 3.
3. Mo `Terminal`, di chuyen vao thu muc project va cai thu vien neu day la lan dau:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 seed.py
```

Neu may da co san moi truong `venv` dung duoc va database da duoc tao roi thi co the bo qua buoc nay.

4. Neu muon dung MoMo/VNPAY, copy file `ngrok` vao cung thu muc voi `app.py`.
5. Mo `Terminal`, di chuyen vao thu muc project va cap quyen chay cho cac file `.command` neu can:

```bash
chmod +x 1_start_app_mac.command 2_start_ngrok_mac.command 3_cap_nhat_public_url_mac.command
```

6. Neu day la lan dau dung ngrok tren may do, dang nhap authtoken:

```bash
./ngrok config add-authtoken YOUR_TOKEN_HERE
```

Neu ban cai ngrok bang Homebrew hoac PATH he thong, co the dung:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Cach chay moi lan

1. Double-click `1_start_app_mac.command`.
2. Doi den khi thay app chay o `http://127.0.0.1:5011`.
3. Double-click `2_start_ngrok_mac.command`.
4. Trong cua so ngrok, copy dong `Forwarding` co dang `https://xxxxx.ngrok-free.app`.
5. Double-click `3_cap_nhat_public_url_mac.command`.
6. Paste link `https://...` vua copy vao va nhan `Enter`.
7. Mo trinh duyet vao `http://127.0.0.1:5011` va test thanh toan.

### Neu macOS chan file `.command`

Neu double-click khong mo duoc, vao `System Settings` > `Privacy & Security`, tim muc canh bao va chon `Open Anyway`.

Ban cung co the mo bang Terminal:

```bash
./1_start_app_mac.command
./2_start_ngrok_mac.command
./3_cap_nhat_public_url_mac.command
```

## Meo de giai thich cho thanh vien trong nhom

Hay noi ngan gon nhu sau:

1. Mo file so `1` de chay web.
2. Mo file so `2` de tao link public.
3. Copy link `https` cua ngrok.
4. Mo file so `3` de dan link vao project.
5. Quay lai web va thanh toan.

## Loi thuong gap

### Bam thanh toan nhung khong quay ve web

Nguyen nhan thuong la `PUBLIC_URL` dang cu hoac ngrok da doi link. Chi can mo lai file so `2`, copy link moi, roi chay file so `3`.

### Script bao khong tim thay ngrok

Windows can `ngrok.exe` trong cung thu muc project hoac ngrok da co trong `PATH`.

macOS can file `ngrok` trong cung thu muc project hoac ngrok da co trong `PATH`.

### App khong mo duoc o cong 5011

Kiem tra xem cong `5011` co dang bi chiem boi chuong trinh khac hay khong. Neu can, tat chuong trinh do roi mo lai file so `1`.

## Ghi chu cho nguoi dong goi zip

- Khong nen ship mot `PUBLIC_URL` ngrok cu trong `.env`, vi link do se het han va lam nguoi khac bi loi callback.
- Co the ship san `ngrok.exe` cho Windows va file `ngrok` cho macOS, nhung moi may van can authtoken ngrok cua chinh may do trong lan dau.
- Neu ban muon ca nhom dung chung ma khong can ai cai ngrok, cach don gian nhat la chi mot may chay app + ngrok, roi gui link public cho ca nhom cung test.
