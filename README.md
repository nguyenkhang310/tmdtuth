# 🛍️ UTH Store — Flask E-Commerce Web App

> Ứng dụng thương mại điện tử thời trang hiện đại được xây dựng với Flask, SQLAlchemy và SQLite. Giao diện đẹp, responsive, hỗ trợ đầy đủ tính năng từ browsing sản phẩm, giỏ hàng, thanh toán đến quản trị admin.

---

## 📋 Mục lục

- [✨ Tính năng](#-tính-năng)
- [🗂️ Cấu trúc thư mục](#️-cấu-trúc-thư-mục)
- [🚀 Cài đặt & Chạy](#-cài-đặt--chạy)
- [⚙️ Cấu hình biến môi trường](#️-cấu-hình-biến-môi-trường)
- [🌱 Seed dữ liệu mẫu](#-seed-dữ-liệu-mẫu)
- [👤 Tài khoản mặc định](#-tài-khoản-mặc-định)
- [📄 Các trang & Route](#-các-trang--route)
- [🔐 Bảo mật](#-bảo-mật)
- [🗄️ Cơ sở dữ liệu](#️-cơ-sở-dữ-liệu)
- [💳 Thanh toán](#-thanh-toán)
- [🚢 Deploy lên Production](#-deploy-lên-production)

---

## ✨ Tính năng

### Khách hàng
| Tính năng | Mô tả |
|---|---|
| 🛒 Giỏ hàng | Thêm/xóa/cập nhật số lượng, hỗ trợ cả guest và user đã đăng nhập |
| ❤️ Wishlist | Lưu sản phẩm yêu thích |
| 🔍 Tìm kiếm & lọc | Tìm theo tên, lọc theo danh mục, giá, sale, sắp xếp |
| 🏷️ Mã giảm giá | Hỗ trợ coupon % / cố định / miễn phí ship |
| 📦 Theo dõi đơn hàng | Tra cứu đơn theo email + SĐT, hoặc xem trong tài khoản |
| ⭐ Đánh giá | Để lại review và rating cho sản phẩm |
| 👤 Tài khoản | Đăng ký, đăng nhập, đổi thông tin, đổi mật khẩu |
| 📱 Responsive | Giao diện đẹp trên mọi thiết bị (mobile, tablet, desktop) |

### Admin (`/admin`)
| Tính năng | Mô tả |
|---|---|
| 📊 Dashboard | Thống kê doanh thu, đơn hàng, sản phẩm, khách hàng |
| 📦 Quản lý sản phẩm | Thêm/sửa/xóa sản phẩm, upload ảnh, quản lý tồn kho |
| 📋 Quản lý đơn hàng | Xem tất cả đơn, cập nhật trạng thái |
| 👥 Quản lý người dùng | Xem danh sách, phân quyền |
| 🏷️ Quản lý coupon | Tạo và quản lý mã giảm giá |
| 📨 Hộp thư liên hệ | Xem tin nhắn từ khách |

---

## 🗂️ Cấu trúc thư mục

```
tmdtuth/
│
├── app.py              # Ứng dụng Flask chính — tất cả routes và logic
├── models.py           # SQLAlchemy models (User, Product, Order, v.v.)
├── extensions.py       # Khởi tạo db và login_manager
├── seed.py             # Script tạo dữ liệu mẫu (28 sản phẩm + 2 tài khoản)
├── requirements.txt    # Danh sách thư viện Python
├── .env                # Biến môi trường (không commit lên git!)
├── .gitignore
│
├── templates/          # HTML templates (Jinja2, kế thừa từ base.html)
│   ├── base.html           # Layout chung (navbar, footer, flash messages)
│   ├── index.html          # Trang chủ
│   ├── products.html       # Danh sách sản phẩm + bộ lọc
│   ├── product-detail.html # Chi tiết sản phẩm + đánh giá
│   ├── cart.html           # Giỏ hàng
│   ├── checkout.html       # Thanh toán
│   ├── order-detail.html   # Chi tiết đơn hàng
│   ├── order-lookup.html   # Tra cứu đơn hàng (không cần login)
│   ├── my-orders.html      # Đơn hàng của tôi (cần login)
│   ├── profile.html        # Thông tin tài khoản (cần login)
│   ├── wishlist.html       # Danh sách yêu thích
│   ├── login.html          # Đăng nhập / Đăng ký
│   ├── contact.html        # Liên hệ
│   ├── policy.html         # Chính sách đổi trả & vận chuyển
│   └── admin.html          # Bảng điều khiển admin
│
├── static/
│   ├── logo.png            # Logo cửa hàng
│   ├── js/
│   │   ├── main.js             # JS chung
│   │   ├── cart.js             # Logic giỏ hàng (AJAX update quantity)
│   │   ├── product-detail.js   # Logic trang chi tiết sản phẩm
│   │   ├── products-filter.js  # Bộ lọc sản phẩm
│   │   └── products.js         # Trang danh sách sản phẩm
│   └── uploads/            # Ảnh sản phẩm do admin upload
│
└── instance/
    └── ecommerce.db        # SQLite database (tự tạo khi chạy lần đầu)
```

---

## 🚀 Cài đặt & Chạy

### Yêu cầu
- **Python 3.10+**
- pip (đi kèm với Python)

### Bước 1 — Clone repo

```bash
git clone <repo-url>
cd tmdtuth
```

### Bước 2 — Tạo virtual environment (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3 — Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 4 — Tạo file `.env`

Tạo file `.env` ở thư mục gốc với nội dung sau:

```env
# BẮT BUỘC
SECRET_KEY=thay-bang-chuoi-bi-mat-it-nhat-32-ky-tu-cua-ban

# Chế độ development (bật debug, dùng RAM cho rate limiter)
FLASK_DEBUG=1
LIMITER_STORAGE_URI=memory://
```

> ⚠️ **Không bao giờ commit file `.env` lên git!** File này đã được thêm vào `.gitignore`.

### Bước 5 — Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt và truy cập: **http://127.0.0.1:5000**

---

## ⚙️ Cấu hình biến môi trường

| Biến | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Khóa bí mật Flask (≥ 32 ký tự) |
| `FLASK_DEBUG` | — | `0` | Bật debug mode (`1` = bật) |
| `LIMITER_STORAGE_URI` | ✅ production | `memory://` (debug) | URI Redis cho rate limiter |
| `REDIS_URL` | — | — | Alias cho `LIMITER_STORAGE_URI` |
| `PORT` | — | `5000` | Port chạy app |
| `COOKIE_SECURE` | — | `0` | Bật secure cookie khi dùng HTTPS (`1` = bật) |
| `SHOP_NAME` | — | `UTH Store` | Tên cửa hàng |
| `SHOP_EMAIL` | — | `contact@uthstore.vn` | Email hiển thị |
| `SHOP_PHONE` | — | `02838992862` | SĐT cửa hàng |
| `SHOP_ADDRESS` | — | địa chỉ mặc định | Địa chỉ cửa hàng |
| `BANK_TRANSFER_INFO` | — | nội dung mẫu | Thông tin chuyển khoản ngân hàng |
| `MOMO_PARTNER_CODE` | — | — | Mã đối tác MoMo |
| `MOMO_ACCESS_KEY` | — | — | Access key MoMo |
| `MOMO_SECRET_KEY` | — | — | Secret key MoMo |
| `VNPAY_TMN_CODE` | — | — | Mã merchant VNPay |
| `VNPAY_HASH_SECRET` | — | — | Hash secret VNPay |

---

## 🌱 Seed dữ liệu mẫu

Để tạo dữ liệu mẫu (28 sản phẩm, 4 danh mục, 2 tài khoản):

```bash
python seed.py
```

> Script chỉ thêm dữ liệu nếu chưa tồn tại — an toàn khi chạy nhiều lần.

---

## 👤 Tài khoản mặc định

Sau khi chạy `seed.py`:

| Vai trò | Username | Password | Email |
|---|---|---|---|
| 🔑 Admin | `admin` | `admin123` | `admin@uthstore.com` |
| 👤 User | `user` | `user123` | `user@uthstore.com` |

> 🔒 **Đổi mật khẩu ngay sau khi deploy lên production!**

---

## 📄 Các trang & Route

### Public (không cần đăng nhập)
| Route | Mô tả |
|---|---|
| `GET /` | Trang chủ |
| `GET /products` | Danh sách sản phẩm (hỗ trợ filter, search, sort, phân trang) |
| `GET /product/<id>` | Chi tiết sản phẩm |
| `GET /cart` | Giỏ hàng |
| `POST /cart/add/<id>` | Thêm vào giỏ |
| `POST /cart/remove/<id>` | Xóa khỏi giỏ |
| `POST /cart/coupon` | Áp dụng mã giảm giá |
| `GET/POST /checkout` | Thanh toán |
| `GET /order/lookup` | Tra cứu đơn hàng |
| `GET /contact` | Liên hệ |
| `GET /policy` | Chính sách |
| `GET /login` | Đăng nhập |
| `POST /login` | Xử lý đăng nhập |
| `GET /register` | Đăng ký |
| `POST /register` | Xử lý đăng ký |
| `GET /logout` | Đăng xuất |
| `GET /sitemap.xml` | Sitemap cho SEO |
| `GET /robots.txt` | Robots.txt cho SEO |

### User (cần đăng nhập)
| Route | Mô tả |
|---|---|
| `GET /my-orders` | Danh sách đơn hàng của tôi |
| `GET /order/<id>` | Chi tiết đơn hàng |
| `GET/POST /profile` | Xem & cập nhật thông tin tài khoản |
| `GET /wishlist` | Danh sách yêu thích |
| `POST /wishlist/toggle/<id>` | Thêm/xóa yêu thích |
| `POST /product/<id>/review` | Gửi đánh giá |

### Admin (cần role `admin`)
| Route | Mô tả |
|---|---|
| `GET /admin` | Dashboard quản trị |
| `POST /admin/product/add` | Thêm sản phẩm |
| `POST /admin/product/<id>/edit` | Sửa sản phẩm |
| `POST /admin/product/<id>/delete` | Xóa sản phẩm |
| `POST /admin/order/<id>/status` | Cập nhật trạng thái đơn |
| `POST /admin/coupon/add` | Thêm mã giảm giá |
| `POST /admin/coupon/<id>/delete` | Xóa mã giảm giá |

---

## 🔐 Bảo mật

- **CSRF Protection** — Flask-WTF bảo vệ tất cả POST request
- **Rate Limiting** — Flask-Limiter giới hạn 500 req/ngày, 200 req/giờ
- **Password Hashing** — Werkzeug `pbkdf2:sha256`
- **Session Cookie** — `HttpOnly`, `SameSite=Lax`; bật `COOKIE_SECURE=1` khi dùng HTTPS
- **Safe Redirect** — Kiểm tra URL redirect để tránh open redirect
- **Secret Key** — Bắt buộc phải set, tối thiểu 32 ký tự

---

## 🗄️ Cơ sở dữ liệu

SQLite được sử dụng trong development, lưu tại `instance/ecommerce.db`.

### Các bảng chính

```
User          — Tài khoản người dùng
Category      — Danh mục sản phẩm
Product       — Sản phẩm
Cart          — Giỏ hàng (DB, cho user đã đăng nhập)
CartItem      — Sản phẩm trong giỏ
Order         — Đơn hàng
OrderItem     — Sản phẩm trong đơn
Review        — Đánh giá sản phẩm
WishlistItem  — Danh sách yêu thích
Coupon        — Mã giảm giá
Contact       — Tin nhắn liên hệ
PaymentTransaction — Giao dịch thanh toán
```

---

## 💳 Thanh toán

App hỗ trợ 4 phương thức thanh toán:

| Phương thức | Trạng thái | Cấu hình |
|---|---|---|
| 💵 COD (Tiền mặt khi nhận) | ✅ Hoạt động | Không cần |
| 🏦 Chuyển khoản ngân hàng | ✅ Hoạt động | `BANK_TRANSFER_INFO` |
| 📱 MoMo | 🔧 Cần cấu hình | `MOMO_*` vars |
| 💳 VNPay | 🔧 Cần cấu hình | `VNPAY_*` vars |

---

## 🚢 Deploy lên Production

### Chuẩn bị `.env` cho production

```env
SECRET_KEY=<chuoi-bi-mat-manh-du-32-ky-tu>
FLASK_DEBUG=0
REDIS_URL=redis://localhost:6379/0
COOKIE_SECURE=1
SESSION_COOKIE_SAMESITE=Strict
```

### Chạy với Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Chạy với Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

### Với Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/tmdtuth/static/;
        expires 30d;
    }
}
```

> 💡 **Production**: Thay SQLite bằng PostgreSQL hoặc MySQL bằng cách đổi `SQLALCHEMY_DATABASE_URI` trong `app.py`.

---

## 📦 Thư viện sử dụng

| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM database |
| Flask-Login | 0.6.3 | Quản lý xác thực |
| Flask-WTF | 1.2.1 | CSRF protection |
| Flask-Limiter | 3.8.0 | Rate limiting |
| Flask-Migrate | 4.0.7 | Database migrations |
| SQLAlchemy | 2.0.31 | SQL toolkit |
| Werkzeug | 3.0.3 | Password hashing, utilities |
| python-dotenv | 1.0.1 | Load biến môi trường từ `.env` |
| requests | 2.32.3 | HTTP client (tích hợp payment) |
| redis | 7.4.0 | Client cho Redis (rate limiter prod) |

---

*Made with ❤️ — UTH Store © 2026*
