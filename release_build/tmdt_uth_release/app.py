from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv(override=True)
import sqlite3
import smtplib
import uuid
import json
import hmac
import hashlib
import urllib.parse
from email.message import EmailMessage
from urllib.parse import urlparse, urljoin
import unicodedata
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func, or_
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from typing import Optional

from extensions import db, login_manager
from models import User, Category, Product, Cart, CartItem, Order, OrderItem, Review, Contact, PaymentTransaction, WishlistItem, Coupon

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)
_env_secret = (os.environ.get('SECRET_KEY') or '').strip()
_is_debug_mode = os.environ.get('FLASK_DEBUG', '').strip().lower() in ['1', 'true', 'yes']
_is_testing_mode = os.environ.get('TESTING', '').strip().lower() in ['1', 'true', 'yes']
if not _env_secret:
    if _is_debug_mode or _is_testing_mode:
        _env_secret = 'dev-secret-key-change-me-before-deploy'
    else:
        raise RuntimeError("SECRET_KEY must be set for all deployed environments.")
elif len(_env_secret) < 32:
    raise RuntimeError("SECRET_KEY must be at least 32 characters long.")

app.config['SECRET_KEY'] = _env_secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME', 'https' if os.environ.get('COOKIE_SECURE', '').strip().lower() in ['1', 'true', 'yes'] else 'http')

# Session / cookie hardening (set COOKIE_SECURE=1 when behind HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('COOKIE_SECURE', '').strip().lower() in ['1', 'true', 'yes']
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')
app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('COOKIE_SECURE', '').strip().lower() in ['1', 'true', 'yes']

# CSRF config for AJAX
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']

# Shared shop config
app.config['SHOP_INFO'] = {
    'name': os.environ.get('SHOP_NAME', 'UTH Store').strip() or 'UTH Store',
    'tagline': os.environ.get(
        'SHOP_TAGLINE',
        'Thời trang hiện đại, ưu đãi hấp dẫn, giao hàng nhanh.'
    ).strip(),
    'description': os.environ.get(
        'SHOP_DESCRIPTION',
        'Thương hiệu thời trang cao cấp dành cho thế hệ năng động, hiện đại và luôn muốn thể hiện phong cách riêng.'
    ).strip(),
    'address': os.environ.get(
        'SHOP_ADDRESS',
        '02 Võ Oanh, Phường 25, Thạnh Mỹ Tây, Hồ Chí Minh, Việt Nam'
    ).strip(),
    'phone': os.environ.get('SHOP_PHONE', '02838992862').strip(),
    'phone_display': os.environ.get('SHOP_PHONE_DISPLAY', '02838992862').strip() or os.environ.get('SHOP_PHONE', '02838992862').strip(),
    'email': os.environ.get('SHOP_EMAIL', 'contact@uthstore.vn').strip(),
    'support_email': os.environ.get('SHOP_SUPPORT_EMAIL', 'support@uthstore.vn').strip(),
    'hours': os.environ.get('SHOP_HOURS', 'Thứ 2 - Thứ 7: 8h - 22h | Chủ nhật: 9h - 20h').strip(),
    'map_embed_url': os.environ.get(
        'SHOP_MAP_EMBED_URL',
        'https://www.google.com/maps?q=02+V%C3%B5+Oanh%2C+Ph%C6%B0%E1%BB%9Dng+25%2C+Th%E1%BA%A1nh+M%E1%BB%B9+T%C3%A2y%2C+H%E1%BB%93+Ch%C3%AD+Minh%2C+Vi%E1%BB%87t+Nam&output=embed'
    ).strip(),
}

# Mail config (SMTP with console fallback for local demo)
app.config['MAIL_SERVER'] = (os.environ.get('MAIL_SERVER') or '').strip()
app.config['MAIL_PORT'] = int((os.environ.get('MAIL_PORT') or '587').strip() or '587')
app.config['MAIL_USE_TLS'] = (os.environ.get('MAIL_USE_TLS') or '1').strip().lower() in ['1', 'true', 'yes', 'on']
app.config['MAIL_USE_SSL'] = (os.environ.get('MAIL_USE_SSL') or '0').strip().lower() in ['1', 'true', 'yes', 'on']
app.config['MAIL_USERNAME'] = (os.environ.get('MAIL_USERNAME') or '').strip()
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or ''
app.config['MAIL_DEFAULT_SENDER'] = (
    os.environ.get('MAIL_DEFAULT_SENDER')
    or os.environ.get('MAIL_USERNAME')
    or ''
).strip()
app.config['MAIL_CONSOLE_FALLBACK'] = (
    os.environ.get('MAIL_CONSOLE_FALLBACK')
    or ('1' if (_is_debug_mode or _is_testing_mode) else '0')
).strip().lower() in ['1', 'true', 'yes', 'on']
app.config['PASSWORD_RESET_EXPIRES_MINUTES'] = max(
    5,
    int((os.environ.get('PASSWORD_RESET_EXPIRES_MINUTES') or '30').strip() or '30')
)

# Payment config (prefer env vars in production)
app.config['BANK_TRANSFER_INFO'] = os.environ.get('BANK_TRANSFER_INFO') or (
    "Ngân hàng: MB Bank\n"
    "Chủ TK: Đỗ Hữu Huân\n"
    "STK: 01237890\n"
    "Nội dung: UTH{{order_id}}"
)

app.config['MOMO_ENDPOINT'] = os.environ.get('MOMO_ENDPOINT') or 'https://test-payment.momo.vn/v2/gateway/api/create'
app.config['MOMO_PARTNER_CODE'] = os.environ.get('MOMO_PARTNER_CODE') or ''
app.config['MOMO_ACCESS_KEY'] = os.environ.get('MOMO_ACCESS_KEY') or ''
app.config['MOMO_SECRET_KEY'] = os.environ.get('MOMO_SECRET_KEY') or ''

app.config['VNPAY_TMN_CODE'] = os.environ.get('VNPAY_TMN_CODE') or ''
app.config['VNPAY_HASH_SECRET'] = os.environ.get('VNPAY_HASH_SECRET') or ''
app.config['VNPAY_URL'] = os.environ.get('VNPAY_URL') or 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
app.config['PAYMENT_ENV_VARS'] = {
    'MOMO': ['MOMO_ENDPOINT', 'MOMO_PARTNER_CODE', 'MOMO_ACCESS_KEY', 'MOMO_SECRET_KEY'],
    'VNPAY': ['VNPAY_TMN_CODE', 'VNPAY_HASH_SECRET', 'VNPAY_URL'],
    'BANK_TRANSFER': ['BANK_TRANSFER_INFO'],
}

app.config['COUPONS'] = {
    "WELCOME10": {"type": "percent", "value": 10, "min_subtotal": 200000},
    "FREESHIP": {"type": "shipping", "value": 30000, "min_subtotal": 300000},
    "SAVE50K": {"type": "fixed", "value": 50000, "min_subtotal": 600000},
}
app.config['ORDER_CANCEL_REASONS'] = [
    "Tôi muốn thay đổi địa chỉ nhận hàng",
    "Tôi muốn đổi sản phẩm hoặc phân loại",
    "Tôi đặt nhầm đơn hàng",
    "Tôi tìm thấy giá tốt hơn",
    "Thời gian giao hàng dự kiến quá lâu",
]

# Custom Jinja2 filters
@app.template_filter('enumerate')
def jinja_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)

@app.template_filter('fromjson')
def jinja_fromjson(value):
    return _safe_json_list(value)


def _safe_json_list(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


# Upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def ensure_db_schema():
    db_path = os.path.join(app.instance_path, 'ecommerce.db')
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(product);")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if 'stock' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN stock INTEGER DEFAULT 100")
    if 'created_at' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN created_at DATETIME")
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "UPDATE product SET created_at = ? WHERE created_at IS NULL",
            (timestamp,)
        )
    if 'extra_images' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN extra_images TEXT")
    if 'video_url' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN video_url VARCHAR(500)")
    if 'sizes' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN sizes TEXT")
    if 'subcategory' not in existing_columns:
        cursor.execute("ALTER TABLE product ADD COLUMN subcategory VARCHAR(100)")

    conn.commit()
    conn.close()

def ensure_order_schema():
    db_path = os.path.join(app.instance_path, 'ecommerce.db')
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info('order');")
    cols = {row[1] for row in cursor.fetchall()}

    if 'shipping_name' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN shipping_name VARCHAR(150)")
    if 'shipping_phone' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN shipping_phone VARCHAR(30)")
    if 'shipping_address' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN shipping_address VARCHAR(500)")
    if 'note' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN note VARCHAR(500)")
    if 'cancel_reason' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN cancel_reason VARCHAR(500)")
    if 'cancelled_at' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN cancelled_at DATETIME")
    if 'payment_method' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN payment_method VARCHAR(50) DEFAULT 'COD'")
        cursor.execute("UPDATE 'order' SET payment_method='COD' WHERE payment_method IS NULL")
    if 'payment_status' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN payment_status VARCHAR(50) DEFAULT 'unpaid'")
        cursor.execute("UPDATE 'order' SET payment_status='unpaid' WHERE payment_status IS NULL")
    if 'payment_ref' not in cols:
        cursor.execute("ALTER TABLE 'order' ADD COLUMN payment_ref VARCHAR(200)")

    conn.commit()
    conn.close()


def ensure_user_schema():
    """Thêm các cột hồ sơ người dùng nếu chưa có (schema migration đơn giản)."""
    db_path = os.path.join(app.instance_path, 'ecommerce.db')
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user);")
    cols = {row[1] for row in cursor.fetchall()}

    if 'first_name' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN first_name VARCHAR(100)")
    if 'last_name' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN last_name VARCHAR(100)")
    if 'phone' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN phone VARCHAR(30)")
    if 'address' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN address VARCHAR(500)")
    if 'birth_date' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN birth_date DATE")
    if 'policy_accepted_at' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN policy_accepted_at DATETIME")
    if 'reset_token' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)")
    if 'reset_token_expires' not in cols:
        cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expires DATETIME")

    conn.commit()
    conn.close()


def _normalize_phone(phone: str) -> str:
    return re.sub(r'\s+', '', (phone or '').strip())


def _parse_birth_date(value: str):
    value = (value or '').strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _split_shipping_name(full_name: str) -> tuple[str, str]:
    full_name = (full_name or '').strip()
    if not full_name:
        return '', ''
    parts = full_name.split()
    if len(parts) == 1:
        return '', parts[0]
    return ' '.join(parts[:-1]), parts[-1]


def _extract_momo_order_id(order_id_raw: str = '', extra_data_raw: str = '') -> Optional[int]:
    extra_data = urllib.parse.unquote(extra_data_raw or '').strip()
    if extra_data:
        try:
            parsed = json.loads(extra_data)
            order_id = int(parsed.get('order_id'))
            if order_id > 0:
                return order_id
        except Exception:
            pass

    match = re.search(r'UTH(\d+)', order_id_raw or '')
    if match:
        return int(match.group(1))
    return None


def _build_vnpay_txn_ref(order_id: int) -> str:
    return f"UTHVNP{order_id}-{uuid.uuid4().hex[:10]}"


def _extract_vnpay_order_id(txn_ref: str = '') -> Optional[int]:
    match = re.search(r'UTHVNP(\d+)', txn_ref or '')
    if match:
        return int(match.group(1))
    if str(txn_ref).isdigit():
        return int(txn_ref)
    return None


def _resolve_cancel_reason_from_form() -> tuple[Optional[str], Optional[str]]:
    choice = (request.form.get('cancel_reason_choice') or '').strip()
    note = (request.form.get('cancel_reason_note') or '').strip()
    allowed = app.config.get('ORDER_CANCEL_REASONS', [])

    if choice == '__other__':
        if len(note) < 5:
            return None, 'Vui lòng nhập lý do cụ thể cho lựa chọn "Khác".'
        return note, None

    if choice not in allowed:
        return None, 'Vui lòng chọn một lý do hủy đơn hàng.'

    return choice, None


def _build_checkout_profile(user: Optional[User]) -> dict[str, str]:
    if not user or not getattr(user, 'is_authenticated', False):
        return {
            'shipping_name': '',
            'shipping_phone': '',
            'shipping_address': '',
            'guest_email': '',
        }

    return {
        'shipping_name': user.full_name or user.username or '',
        'shipping_phone': user.phone or '',
        'shipping_address': user.address or '',
        'guest_email': user.email or '',
    }


def _can_cancel_order(order: Order) -> bool:
    return order.status not in ['shipped', 'delivered', 'cancelled']


def _restore_order_stock(order: Order) -> None:
    for item in order.items:
        product = item.product or Product.query.get(item.product_id)
        if not product or product.stock is None:
            continue
        product.stock = int(product.stock) + int(item.quantity or 0)


def _cancel_order(order: Order, reason: str, actor: str = 'user') -> None:
    if order.status == 'cancelled':
        return

    _restore_order_stock(order)
    order.status = 'cancelled'
    order.cancel_reason = (reason or '').strip()
    order.cancelled_at = datetime.utcnow()
    if order.payment_status != 'paid':
        order.payment_status = 'cancelled'
    if actor == 'admin' and not order.cancel_reason:
        order.cancel_reason = 'Đơn hàng được hủy bởi quản trị viên.'


def _hmac_sha256(secret: str, data: str) -> str:
    return hmac.new(secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()


def _vnpay_hmac_sha512(secret: str, data: str) -> str:
    return hmac.new(secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha512).hexdigest()


def _absolute_url(endpoint: str, **values) -> str:
    base_url = os.environ.get('PUBLIC_URL', '').strip()
    if base_url:
        # Nếu có PUBLIC_URL (ngrok), dùng urljoin với base_url
        return urljoin(base_url, url_for(endpoint, **values))
    return url_for(endpoint, _external=True, **values)


def _missing_payment_env_vars() -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for provider, env_keys in app.config.get('PAYMENT_ENV_VARS', {}).items():
        empty_keys = [key for key in env_keys if not str(app.config.get(key, '')).strip()]
        if empty_keys:
            missing[provider] = empty_keys
    return missing


def _mail_is_configured() -> bool:
    sender = app.config.get('MAIL_DEFAULT_SENDER', '').strip() or app.config.get('SHOP_INFO', {}).get('support_email', '').strip()
    server = app.config.get('MAIL_SERVER', '').strip()
    if not sender or not server:
        return False
    username = app.config.get('MAIL_USERNAME', '').strip()
    password = app.config.get('MAIL_PASSWORD', '')
    if username and not password:
        return False
    return True


def _send_email(subject: str, recipients: list[str], text_body: str) -> bool:
    recipients = [email.strip() for email in recipients if email and email.strip()]
    if not recipients:
        return False

    sender = app.config.get('MAIL_DEFAULT_SENDER', '').strip() or app.config.get('SHOP_INFO', {}).get('support_email', '').strip()

    if not _mail_is_configured():
        if app.config.get('MAIL_CONSOLE_FALLBACK'):
            app.logger.warning(
                "SMTP chưa cấu hình. Nội dung email được ghi ra log để demo.\nTo: %s\nSubject: %s\n\n%s",
                ", ".join(recipients),
                subject,
                text_body,
            )
            return True
        return False

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message.set_content(text_body)

    host = app.config.get('MAIL_SERVER')
    port = int(app.config.get('MAIL_PORT') or 587)
    username = app.config.get('MAIL_USERNAME', '').strip()
    password = app.config.get('MAIL_PASSWORD', '')
    use_tls = bool(app.config.get('MAIL_USE_TLS'))
    use_ssl = bool(app.config.get('MAIL_USE_SSL'))

    try:
        if use_ssl:
            smtp_client = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            smtp_client = smtplib.SMTP(host, port, timeout=20)
        with smtp_client as smtp:
            smtp.ehlo()
            if use_tls and not use_ssl:
                smtp.starttls()
                smtp.ehlo()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
        return True
    except Exception:
        app.logger.exception("Không gửi được email tới %s", ", ".join(recipients))
        if app.config.get('MAIL_CONSOLE_FALLBACK'):
            app.logger.warning(
                "Chuyển sang console fallback cho email reset password.\nTo: %s\nSubject: %s\n\n%s",
                ", ".join(recipients),
                subject,
                text_body,
            )
            return True
        return False


def _send_password_reset_email(user: User, reset_url: str) -> bool:
    expires_minutes = int(app.config.get('PASSWORD_RESET_EXPIRES_MINUTES') or 30)
    shop_name = app.config.get('SHOP_INFO', {}).get('name', 'UTH Store')
    subject = f"[{shop_name}] Liên kết đặt lại mật khẩu"
    greeting_name = user.display_name or user.email
    text_body = (
        f"Xin chào {greeting_name},\n\n"
        "Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.\n"
        f"Liên kết đặt lại mật khẩu: {reset_url}\n\n"
        f"Liên kết này sẽ hết hạn sau {expires_minutes} phút và chỉ dùng được một lần.\n"
        "Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.\n\n"
        f"Trân trọng,\n{shop_name}"
    )
    return _send_email(subject, [user.email], text_body)


def _payment_config_error(payment_method: str) -> Optional[str]:
    payment_method = (payment_method or '').strip().upper()
    if payment_method == 'MOMO':
        missing = [key for key in ['MOMO_ENDPOINT', 'MOMO_PARTNER_CODE', 'MOMO_ACCESS_KEY', 'MOMO_SECRET_KEY']
                   if not str(app.config.get(key, '')).strip()]
        if missing:
            return 'Chưa cấu hình MoMo merchant (MOMO_ENDPOINT/MOMO_PARTNER_CODE/MOMO_ACCESS_KEY/MOMO_SECRET_KEY).'
    elif payment_method == 'VNPAY':
        missing = [key for key in ['VNPAY_TMN_CODE', 'VNPAY_HASH_SECRET', 'VNPAY_URL']
                   if not str(app.config.get(key, '')).strip()]
        if missing:
            return 'Chưa cấu hình VNPAY merchant (VNPAY_TMN_CODE/VNPAY_HASH_SECRET/VNPAY_URL).'
    return None


def _prepare_momo_payment(order: Order) -> str:
    config_error = _payment_config_error('MOMO')
    if config_error:
        raise ValueError(config_error)

    partner_code = app.config.get('MOMO_PARTNER_CODE', '')
    access_key = app.config.get('MOMO_ACCESS_KEY', '')
    secret_key = app.config.get('MOMO_SECRET_KEY', '')
    endpoint = app.config.get('MOMO_ENDPOINT')

    request_id = f"{order.id}-{uuid.uuid4().hex}"
    momo_order_id = f"UTH{order.id}-{uuid.uuid4().hex[:10]}"
    amount = int(round(order.total_amount))
    order_info = f"Thanh toan don hang #{order.id}"
    redirect_url = _absolute_url('momo_return')
    ipn_url = _absolute_url('momo_ipn')
    request_type = "captureWallet"
    extra_data = urllib.parse.quote(
        json.dumps({"order_id": order.id}, ensure_ascii=False, separators=(',', ':'))
    )
    amount_str = str(int(amount))

    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={amount_str}"
        f"&extraData={extra_data}"
        f"&ipnUrl={ipn_url}"
        f"&orderId={momo_order_id}"
        f"&orderInfo={order_info}"
        f"&partnerCode={partner_code}"
        f"&redirectUrl={redirect_url}"
        f"&requestId={request_id}"
        f"&requestType={request_type}"
    )
    signature = _hmac_sha256(secret_key, raw_signature)

    payload = {
        "partnerCode": partner_code,
        "partnerName": app.config.get('SHOP_INFO', {}).get('name', 'UTH Store'),
        "storeId": "UTHStore",
        "requestId": request_id,
        "amount": amount_str,
        "orderId": momo_order_id,
        "orderInfo": order_info,
        "redirectUrl": redirect_url,
        "ipnUrl": ipn_url,
        "lang": "vi",
        "extraData": extra_data,
        "requestType": request_type,
        "signature": signature,
    }

    tx = PaymentTransaction(
        order_id=order.id,
        provider='MOMO',
        amount=float(amount),
        status='initiated',
        provider_ref=momo_order_id,
        raw_request=json.dumps(payload, ensure_ascii=False),
    )
    db.session.add(tx)
    order.payment_status = 'initiated'
    order.payment_ref = momo_order_id

    try:
        resp = requests.post(endpoint, json=payload, timeout=20)
        data = resp.json()
    except Exception as exc:
        order.payment_status = 'failed'
        tx.status = 'failed'
        raise ValueError('Không kết nối được MoMo. Vui lòng thử lại.') from exc

    tx.raw_response = json.dumps(data, ensure_ascii=False)
    pay_url = data.get('payUrl') or data.get('deeplink') or data.get('qrCodeUrl')
    if not pay_url or int(data.get('resultCode', -1)) != 0:
        order.payment_status = 'failed'
        tx.status = 'failed'
        raise ValueError('Tạo thanh toán MoMo thất bại. Vui lòng thử lại.')

    return pay_url


def _prepare_vnpay_payment(order: Order) -> str:
    config_error = _payment_config_error('VNPAY')
    if config_error:
        raise ValueError(config_error)

    tmn_code = app.config.get('VNPAY_TMN_CODE', '')
    hash_secret = app.config.get('VNPAY_HASH_SECRET', '')
    vnp_url = app.config.get('VNPAY_URL', '')
    txn_ref = _build_vnpay_txn_ref(order.id)
    amount = int(round(order.total_amount)) * 100
    create_date = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y%m%d%H%M%S")
    expire_date = (datetime.utcnow() + timedelta(hours=7, minutes=15)).strftime("%Y%m%d%H%M%S")

    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": str(amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Thanh toan don hang #{order.id}",
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": _absolute_url('vnpay_return'),
        "vnp_IpAddr": request.headers.get('X-Forwarded-For', request.remote_addr) or "127.0.0.1",
        "vnp_CreateDate": create_date,
        "vnp_ExpireDate": expire_date,
    }
    sorted_items = sorted(vnp_params.items())
    hashdata = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_items])
    secure_hash = _vnpay_hmac_sha512(hash_secret, hashdata)
    query = urllib.parse.urlencode(sorted_items, quote_via=urllib.parse.quote_plus)
    pay_url = f"{vnp_url}?{query}&vnp_SecureHash={secure_hash}"

    tx = PaymentTransaction(
        order_id=order.id,
        provider='VNPAY',
        amount=float(int(round(order.total_amount))),
        status='initiated',
        provider_ref=txn_ref,
        raw_request=json.dumps(vnp_params, ensure_ascii=False),
    )
    db.session.add(tx)
    order.payment_status = 'initiated'
    order.payment_ref = txn_ref
    return pay_url


def _create_order_from_items(
    *,
    user_id: int,
    items,
    shipping_name: str,
    shipping_phone: str,
    shipping_address: str,
    note: str,
    payment_method: str,
    totals: dict,
    db_coupon: Optional[Coupon],
) -> tuple[Order, list]:
    materialized_items = list(items)
    order = Order(
        user_id=user_id,
        total_amount=float(totals['grand_total']),
        status='pending',
        shipping_name=shipping_name,
        shipping_phone=shipping_phone,
        shipping_address=shipping_address,
        note=note,
        payment_method=payment_method,
        payment_status='initiated' if payment_method in ['MOMO', 'VNPAY'] else 'unpaid'
    )
    db.session.add(order)
    db.session.flush()

    for item in materialized_items:
        product, quantity = _extract_cart_line(item)
        if not product or quantity < 1:
            continue
        product_id = int(item.product_id) if hasattr(item, 'product_id') else int(product.id)
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            price=product.price,
        ))
        if product.stock is not None:
            product.stock = max(0, int(product.stock) - int(quantity))

    if db_coupon and totals.get("applied_coupon"):
        db_coupon.used_count = int(db_coupon.used_count or 0) + 1

    return order, materialized_items


def _is_safe_redirect_url(target: str) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _coupon_to_dict(c: Coupon) -> dict:
    return {
        "type": c.coupon_type,
        "value": float(c.value),
        "min_subtotal": float(c.min_subtotal or 0),
    }


def _coupon_is_available(c: Coupon) -> bool:
    if not c or not c.is_active:
        return False
    if c.expires_at and c.expires_at < datetime.utcnow():
        return False
    if c.max_uses is not None and int(c.used_count or 0) >= int(c.max_uses):
        return False
    return True


def _resolve_coupon_by_code(code: str | None) -> tuple[str | None, dict | None, Coupon | None]:
    if not code:
        return None, None, None
    normalized = code.strip().upper()
    if not normalized:
        return None, None, None
    db_coupon = Coupon.query.filter_by(code=normalized).first()
    if db_coupon and _coupon_is_available(db_coupon):
        return normalized, _coupon_to_dict(db_coupon), db_coupon
    static_coupon = app.config.get('COUPONS', {}).get(normalized)
    if static_coupon:
        return normalized, static_coupon, None
    return normalized, None, None


db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)
_redis_url = (os.environ.get('REDIS_URL') or os.environ.get('LIMITER_STORAGE_URI') or '').strip()
_limiter_storage_uri = _redis_url
if not _limiter_storage_uri:
    if _is_debug_mode or _is_testing_mode:
        _limiter_storage_uri = 'memory://'
    else:
        raise RuntimeError("Production rate limiting requires REDIS_URL or LIMITER_STORAGE_URI.")
app.config['RATELIMIT_STORAGE_URI'] = _limiter_storage_uri
app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["500 per day", "200 per hour"],
    storage_uri=_limiter_storage_uri,
)

with app.app_context():
    db.create_all()
    ensure_db_schema()
    ensure_order_schema()
    ensure_user_schema()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _session_cart_get() -> dict:
    cart = session.get('cart')
    if isinstance(cart, dict):
        return cart
    cart = {}
    session['cart'] = cart
    return cart


def _session_cart_set(cart: dict) -> None:
    session['cart'] = cart
    session.modified = True


def _build_guest_cart_view(cart_dict: dict):
    """
    Build a lightweight cart-like object for templates:
    - .items: list of { id, product, quantity }
    """
    items = []
    for pid_str, qty in cart_dict.items():
        try:
            pid = int(pid_str)
            qty_int = int(qty)
        except Exception:
            continue
        if qty_int < 1:
            continue
        product = Product.query.get(pid)
        if not product:
            continue
        items.append({'id': pid, 'product': product, 'quantity': qty_int})

    class _CartView:
        def __init__(self, items):
            self.items = items

    return _CartView(items)


def _get_or_create_user_cart(user_id: int) -> Cart:
    active_cart = Cart.query.filter_by(user_id=user_id).first()
    if not active_cart:
        active_cart = Cart(user_id=user_id)
        db.session.add(active_cart)
        db.session.commit()
    return active_cart


def _merge_session_cart_into_user_cart(user: User) -> None:
    cart_dict = _session_cart_get()
    if not cart_dict:
        return
    active_cart = _get_or_create_user_cart(user.id)
    for pid_str, qty in cart_dict.items():
        try:
            pid = int(pid_str)
            qty_int = int(qty)
        except Exception:
            continue
        if qty_int < 1:
            continue
        product = Product.query.get(pid)
        if not product:
            continue
        existing = CartItem.query.filter_by(cart_id=active_cart.id, product_id=pid).first()
        if existing:
            existing.quantity = min(int(existing.quantity) + qty_int, int(product.stock or 10**9))
        else:
            db.session.add(CartItem(cart_id=active_cart.id, product_id=pid, quantity=qty_int))
    _session_cart_set({})
    db.session.commit()


def _normalize_text(value: str) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("đ", "d").replace("Đ", "D")
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _extract_cart_line(item):
    if hasattr(item, "product"):
        return item.product, int(item.quantity)
    return item.get("product"), int(item.get("quantity", 0))


def _compute_totals_from_items(items, coupon_code: str | None = None):
    subtotal = 0.0
    item_count = 0
    for item in items:
        product, qty = _extract_cart_line(item)
        if not product or qty < 1:
            continue
        subtotal += float(product.price) * qty
        item_count += qty

    shipping_fee = 0 if subtotal >= 500000 else 30000
    discount = 0
    applied_coupon = None
    coupon = None
    normalized_code = None
    if coupon_code:
        normalized_code, coupon, _ = _resolve_coupon_by_code(coupon_code)
    if coupon and subtotal >= float(coupon.get("min_subtotal", 0)):
        ctype = coupon.get("type")
        cval = float(coupon.get("value", 0))
        if ctype == "percent":
            discount = int(subtotal * cval / 100)
        elif ctype == "fixed":
            discount = int(cval)
        elif ctype == "shipping":
            discount = min(int(cval), int(shipping_fee))
        applied_coupon = normalized_code

    discount = max(0, min(int(discount), int(subtotal + shipping_fee)))
    grand_total = max(0, int(subtotal + shipping_fee - discount))
    return {
        "subtotal": int(subtotal),
        "shipping_fee": int(shipping_fee),
        "discount": int(discount),
        "grand_total": int(grand_total),
        "item_count": int(item_count),
        "applied_coupon": applied_coupon,
    }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_user_counters():
    wishlist_count = 0
    if current_user.is_authenticated:
        wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    return {
        "wishlist_count": wishlist_count,
        "shop": app.config.get('SHOP_INFO', {}),
        "order_cancel_reasons": app.config.get('ORDER_CANCEL_REASONS', []),
    }

# --- ROUTES ---

@app.route('/')
def index():
    new_products = Product.query.filter_by(is_new=True).limit(8).all()
    sale_products = Product.query.filter_by(is_on_sale=True).limit(8).all()
    return render_template('index.html', new_products=new_products, sale_products=sale_products)


@app.route('/robots.txt')
def robots_txt():
    body = "\n".join([
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {_absolute_url('sitemap_xml')}",
        "",
    ])
    resp = make_response(body)
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    return resp


@app.route('/sitemap.xml')
def sitemap_xml():
    pages = []
    pages.append((_absolute_url('index'), datetime.utcnow()))
    pages.append((_absolute_url('products'), datetime.utcnow()))
    pages.append((_absolute_url('policy'), datetime.utcnow()))
    pages.append((_absolute_url('contact'), datetime.utcnow()))

    for p in Product.query.with_entities(Product.id, Product.created_at).order_by(Product.id.desc()).all():
        pid, created_at = p
        pages.append((_absolute_url('product_detail', product_id=pid), created_at or datetime.utcnow()))

    def _fmt(dt: datetime) -> str:
        try:
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return datetime.utcnow().strftime("%Y-%m-%d")

    urlset = []
    urlset.append('<?xml version="1.0" encoding="UTF-8"?>')
    urlset.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, lastmod in pages:
        urlset.append("  <url>")
        urlset.append(f"    <loc>{loc}</loc>")
        urlset.append(f"    <lastmod>{_fmt(lastmod)}</lastmod>")
        urlset.append("  </url>")
    urlset.append("</urlset>")

    resp = make_response("\n".join(urlset))
    resp.headers["Content-Type"] = "application/xml; charset=utf-8"
    return resp

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    q_lower = q.lower()
    q_cap = q.capitalize()
    q_upper = q.upper()
    
    products = Product.query.filter(
        or_(
            Product.name.contains(q_lower),
            Product.name.contains(q_cap),
            Product.name.contains(q_upper)
        )
    ).order_by(Product.id.desc()).limit(6).all()
    
    results = []
    for p in products:
        results.append({
            'name': p.name,
            'price': "{:,.0f}đ".format(p.price),
            'image_url': p.image_url,
            'url': url_for('product_detail', product_id=p.id)
        })
    return jsonify(results)

@app.route('/products')
def products():
    query = Product.query

    category_slug = request.args.get('category')
    sale = request.args.get('sale')
    search_q = (request.args.get('q') or '').strip()
    sub = (request.args.get('sub') or '').strip()  # subcategory filter
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    if category_slug:
        category = Category.query.filter(Category.name.ilike(f'%{category_slug}%')).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if sale == 'true':
        query = query.filter_by(is_on_sale=True)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.desc())

    page = max(1, request.args.get('page', 1, type=int))
    per_page = 12

    if search_q:
        q_lower = search_q.lower()
        q_cap = search_q.capitalize()
        q_upper = search_q.upper()
        
        query = query.filter(
            or_(
                Product.name.contains(q_lower),
                Product.name.contains(q_cap),
                Product.name.contains(q_upper)
            )
        )

    if sub:
        sub_lower = sub.lower()
        sub_cap = sub.capitalize()
        sub_upper = sub.upper()
        query = query.filter(
            or_(
                Product.subcategory == sub,
                Product.name.contains(sub_lower),
                Product.name.contains(sub_cap),
                Product.name.contains(sub_upper)
            )
        )

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return render_template('products.html', products=pagination.items, pagination=pagination)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    is_in_wishlist = False
    can_review = False
    if current_user.is_authenticated:
        is_in_wishlist = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
        if current_user.role != 'admin':
            can_review = OrderItem.query.join(Order).filter(
                Order.user_id == current_user.id,
                Order.status == 'delivered',
                OrderItem.product_id == product_id
            ).first() is not None

    extra_images_list = _safe_json_list(product.extra_images)
    return render_template('product-detail.html', product=product, reviews=reviews, is_in_wishlist=is_in_wishlist, can_review=can_review, extra_images_list=extra_images_list)


@app.route('/wishlist')
@login_required
def wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.created_at.desc()).all()
    return render_template('wishlist.html', items=items)


@app.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def wishlist_toggle(product_id):
    if current_user.role == 'admin':
        flash('Tài khoản quản trị không thể dùng danh sách yêu thích.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    product = Product.query.get_or_404(product_id)
    item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Đã bỏ sản phẩm khỏi danh sách yêu thích.', 'info')
    else:
        db.session.add(WishlistItem(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        flash('Đã thêm sản phẩm vào danh sách yêu thích.', 'success')
    return redirect(request.referrer or url_for('product_detail', product_id=product.id))

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    # Admin không được phép viết đánh giá sản phẩm
    if current_user.role == 'admin':
        flash('Tài khoản quản trị không thể viết đánh giá sản phẩm.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
        
    has_bought = OrderItem.query.join(Order).filter(
        Order.user_id == current_user.id,
        Order.status == 'delivered',
        OrderItem.product_id == product_id
    ).first()
    
    if not has_bought:
        flash('Bạn cần mua và nhận hàng thành công mới được phép đánh giá.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    rating = int(request.form.get('rating', 5))
    rating = max(1, min(5, rating))
    comment = (request.form.get('comment') or '').strip()
    if not comment:
        flash('Vui lòng nhập nội dung đánh giá.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    existed = Review.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if existed:
        existed.rating = rating
        existed.comment = comment
        db.session.commit()
        flash('Đã cập nhật đánh giá của bạn.', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    flash('Cảm ơn bạn đã đánh giá sản phẩm!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    product_id = review.product_id
    # Admin được xóa bất kỳ đánh giá nào; user chỉ xóa được đánh giá của mình
    if current_user.role != 'admin' and review.user_id != current_user.id:
        flash('Bạn không có quyền xóa đánh giá này.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    db.session.delete(review)
    db.session.commit()
    flash('Đã xóa đánh giá thành công.', 'success')
    # Nếu admin đang ở trang admin thì quay lại referrer
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/cart')
def cart():
    if current_user.is_authenticated and current_user.role == 'admin':
        flash('Tài khoản quản trị không thể mua sắm. Vui lòng dùng tài khoản thường.', 'error')
        return redirect(url_for('admin_dashboard'))
    if current_user.is_authenticated:
        active_cart = _get_or_create_user_cart(current_user.id)
        active_coupon_code = session.get('coupon_code')
        totals = _compute_totals_from_items(active_cart.items, active_coupon_code)
        _, _, db_coupon = _resolve_coupon_by_code(active_coupon_code)
        return render_template('cart.html', cart=active_cart, is_guest=False, totals=totals)
    guest_cart = _build_guest_cart_view(_session_cart_get())
    totals = _compute_totals_from_items(guest_cart.items, session.get('coupon_code'))
    return render_template('cart.html', cart=guest_cart, is_guest=True, totals=totals)


@app.route('/cart/coupon', methods=['POST'])
def apply_coupon():
    code = (request.form.get('coupon_code') or '').strip().upper()
    if not code:
        session.pop('coupon_code', None)
        flash('Đã bỏ mã giảm giá.', 'info')
        return redirect(url_for('cart'))

    cart_obj = _get_or_create_user_cart(current_user.id) if current_user.is_authenticated else _build_guest_cart_view(_session_cart_get())
    totals = _compute_totals_from_items(cart_obj.items, code)
    if not totals.get("applied_coupon"):
        flash('Mã giảm giá không hợp lệ hoặc chưa đạt giá trị tối thiểu.', 'error')
        return redirect(url_for('cart'))

    session['coupon_code'] = totals["applied_coupon"]
    session.modified = True
    flash(f'Áp dụng mã {totals["applied_coupon"]} thành công.', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if current_user.is_authenticated and current_user.role == 'admin':
        flash('Tài khoản quản trị không thể mua sắm.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    product = Product.query.get_or_404(product_id)
    if product.stock is not None and quantity > product.stock:
        flash(f'Sản phẩm "{product.name}" không đủ tồn kho (còn {product.stock}).', 'error')
        return redirect(url_for('product_detail', product_id=product_id))

    if current_user.is_authenticated:
        active_cart = _get_or_create_user_cart(current_user.id)
        existing = CartItem.query.filter_by(cart_id=active_cart.id, product_id=product_id).first()
        if existing:
            new_qty = int(existing.quantity) + quantity
            if product.stock is not None and new_qty > product.stock:
                new_qty = product.stock
                flash(f'Giỏ hàng đã được cập nhật tới tối đa tồn kho ({product.stock}).', 'info')
            existing.quantity = new_qty
        else:
            db.session.add(CartItem(cart_id=active_cart.id, product_id=product_id, quantity=quantity))
        db.session.commit()
    else:
        cart_dict = _session_cart_get()
        current_qty = int(cart_dict.get(str(product_id), 0) or 0)
        new_qty = current_qty + quantity
        if product.stock is not None and new_qty > product.stock:
            new_qty = int(product.stock)
            flash(f'Giỏ hàng đã được cập nhật tới tối đa tồn kho ({product.stock}).', 'info')
        cart_dict[str(product_id)] = int(new_qty)
        _session_cart_set(cart_dict)

    flash('Đã thêm sản phẩm vào giỏ hàng!', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/item/<int:item_id>/quantity', methods=['POST'])
def update_cart_item_quantity(item_id):
    qty = None
    if request.is_json:
        qty = request.json.get('quantity')
    else:
        qty = request.form.get('quantity')
    try:
        qty = int(qty)
    except Exception:
        return jsonify({'ok': False, 'error': 'invalid_quantity'}), 400

    if qty < 1:
        qty = 1
    if current_user.is_authenticated:
        item = CartItem.query.get_or_404(item_id)
        if item.cart.user_id != current_user.id:
            return jsonify({'ok': False, 'error': 'forbidden'}), 403
        if item.product.stock is not None and qty > item.product.stock:
            qty = item.product.stock
        item.quantity = qty
        db.session.commit()
        return jsonify({'ok': True, 'quantity': item.quantity})
    # Guest mode: item_id is product_id
    product = Product.query.get_or_404(item_id)
    if product.stock is not None and qty > product.stock:
        qty = int(product.stock)
    cart_dict = _session_cart_get()
    cart_dict[str(product.id)] = int(qty)
    _session_cart_set(cart_dict)
    return jsonify({'ok': True, 'quantity': int(qty)})

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if current_user.is_authenticated:
        item = CartItem.query.get_or_404(item_id)
        if item.cart.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
        return redirect(url_for('cart'))
    # Guest mode: item_id is product_id
    cart_dict = _session_cart_get()
    cart_dict.pop(str(item_id), None)
    _session_cart_set(cart_dict)
    flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if current_user.is_authenticated and current_user.role == 'admin':
        flash('Tài khoản quản trị không thể mua sắm. Vui lòng dùng tài khoản thường.', 'error')
        return redirect(url_for('admin_dashboard'))
    if current_user.is_authenticated:
        active_cart = _get_or_create_user_cart(current_user.id)
        is_guest = False
    else:
        active_cart = _build_guest_cart_view(_session_cart_get())
        is_guest = True
    if not active_cart or len(list(active_cart.items)) == 0:
        flash('Giỏ hàng của bạn đang trống.', 'error')
        return redirect(url_for('cart'))
    coupon_code = session.get('coupon_code')
    totals_preview = _compute_totals_from_items(active_cart.items, coupon_code)
    checkout_profile = _build_checkout_profile(current_user if current_user.is_authenticated else None)
    if request.method == 'POST':
        shipping_name = request.form.get('shipping_name', '').strip()
        shipping_phone = _normalize_phone(request.form.get('shipping_phone', ''))
        shipping_address = request.form.get('shipping_address', '').strip()
        guest_email = request.form.get('guest_email', '').strip().lower()
        note = request.form.get('note', '').strip()
        payment_method = (request.form.get('payment_method') or 'COD').strip().upper()
        if payment_method not in ['COD', 'BANK_TRANSFER', 'MOMO', 'VNPAY']:
            payment_method = 'COD'
        config_error = _payment_config_error(payment_method)
        if config_error:
            flash(config_error, 'error')
            return redirect(url_for('checkout'))

        if current_user.is_authenticated:
            shipping_name = shipping_name or current_user.full_name or current_user.username or ''
            shipping_phone = shipping_phone or _normalize_phone(current_user.phone or '')
            shipping_address = shipping_address or (current_user.address or '').strip()
        else:
            guest_email = guest_email or checkout_profile.get('guest_email', '')

        # Basic validation
        if not shipping_name or not shipping_phone or not shipping_address:
            flash('Vui lòng nhập đầy đủ Họ tên, SĐT và Địa chỉ nhận hàng.', 'error')
            return redirect(url_for('checkout'))
        if not re.fullmatch(r'(0|\+84)\d{9,10}', shipping_phone):
            flash('Số điện thoại không hợp lệ.', 'error')
            return redirect(url_for('checkout'))
        if is_guest and not guest_email:
            flash('Vui lòng nhập Email để nhận thông tin đơn hàng.', 'error')
            return redirect(url_for('checkout'))
        if is_guest and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', guest_email):
            flash('Email không hợp lệ.', 'error')
            return redirect(url_for('checkout'))

        # Stock check
        for item in active_cart.items:
            qty_item = int(item.quantity) if hasattr(item, 'quantity') else int(item.get('quantity', 0))
            product = item.product if hasattr(item, 'product') else item.get('product')
            if qty_item < 1:
                flash('Số lượng sản phẩm không hợp lệ.', 'error')
                return redirect(url_for('cart'))
            if product.stock is not None and qty_item > product.stock:
                flash(f'Sản phẩm "{product.name}" không đủ tồn kho (còn {product.stock}).', 'error')
                return redirect(url_for('cart'))
        totals = _compute_totals_from_items(active_cart.items, session.get('coupon_code'))
        _, _, db_coupon = _resolve_coupon_by_code(session.get('coupon_code'))
        checkout_user = current_user if current_user.is_authenticated else None
        created_guest_user = None
        pay_url = None

        try:
            if is_guest:
                existing_user = User.query.filter(func.lower(User.email) == guest_email.lower()).first()
                if existing_user:
                    flash('Email này đã có tài khoản. Vui lòng đăng nhập — giỏ hàng của bạn sẽ được giữ nguyên!', 'error')
                    return redirect(url_for('login', next=url_for('checkout')))

                uname = f"guest_{uuid.uuid4().hex[:8]}"
                rand_pw = uuid.uuid4().hex + uuid.uuid4().hex
                guest_last_name, guest_first_name = _split_shipping_name(shipping_name)
                created_guest_user = User(
                    username=uname,
                    first_name=guest_first_name or None,
                    last_name=guest_last_name or None,
                    email=guest_email,
                    phone=shipping_phone,
                    address=shipping_address,
                    password_hash=generate_password_hash(rand_pw),
                    policy_accepted_at=datetime.utcnow(),
                )
                db.session.add(created_guest_user)
                db.session.flush()
                checkout_user = created_guest_user
            else:
                profile_changed = False
                parsed_last_name, parsed_first_name = _split_shipping_name(shipping_name)
                if shipping_phone != _normalize_phone(current_user.phone or ''):
                    current_user.phone = shipping_phone
                    profile_changed = True
                if shipping_address != (current_user.address or '').strip():
                    current_user.address = shipping_address
                    profile_changed = True
                if parsed_first_name and not (current_user.first_name or '').strip():
                    current_user.first_name = parsed_first_name
                    profile_changed = True
                if parsed_last_name and not (current_user.last_name or '').strip():
                    current_user.last_name = parsed_last_name
                    profile_changed = True
                if profile_changed:
                    db.session.flush()

            order, materialized_items = _create_order_from_items(
                user_id=checkout_user.id,
                items=active_cart.items,
                shipping_name=shipping_name,
                shipping_phone=shipping_phone,
                shipping_address=shipping_address,
                note=note,
                payment_method=payment_method,
                totals=totals,
                db_coupon=db_coupon,
            )

            if not is_guest:
                for item in materialized_items:
                    db.session.delete(item)

            if payment_method == 'MOMO':
                pay_url = _prepare_momo_payment(order)
            elif payment_method == 'VNPAY':
                pay_url = _prepare_vnpay_payment(order)

            db.session.commit()
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
            return redirect(url_for('checkout'))
        except Exception:
            db.session.rollback()
            app.logger.exception("Checkout failed for payment_method=%s", payment_method)
            flash('Không thể tạo đơn hàng lúc này. Vui lòng thử lại.', 'error')
            return redirect(url_for('checkout'))

        session.pop('coupon_code', None)
        if is_guest:
            _session_cart_set({})
            login_user(created_guest_user)
        session.modified = True

        flash('Đã tạo đơn hàng thành công!', 'success')
        if pay_url:
            return redirect(pay_url)
        return redirect(url_for('order_detail', order_id=order.id))
    
    response = make_response(
        render_template(
            'checkout.html',
            cart=active_cart,
            is_guest=is_guest,
            totals=totals_preview,
            coupon_code=coupon_code,
            checkout_profile=checkout_profile,
        )
    )
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền xem đơn hàng này.', 'error')
        return redirect(url_for('index'))
    bank_info = app.config.get('BANK_TRANSFER_INFO', '')
    return render_template('order-detail.html', order=order, bank_info=bank_info)


@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền hủy đơn hàng này.', 'error')
        return redirect(url_for('index'))

    cancel_reason, cancel_reason_error = _resolve_cancel_reason_from_form()
    if cancel_reason_error:
        flash(cancel_reason_error, 'error')
        return redirect(url_for('order_detail', order_id=order.id))

    if not _can_cancel_order(order):
        flash('Đơn hàng đã chuyển sang trạng thái đang giao hoặc hoàn tất nên không thể hủy.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))

    _cancel_order(order, cancel_reason or '', actor='user')
    db.session.commit()
    flash('Đã hủy đơn hàng thành công.', 'success')
    return redirect(url_for('order_detail', order_id=order.id))


@app.route('/order/lookup', methods=['GET', 'POST'])
def order_lookup():
    found_order = None
    status_steps = []
    lookup_email = (request.form.get('email') or '').strip().lower()
    if request.method == 'POST':
        order_id = request.form.get('order_id', type=int)
        if current_user.is_authenticated and not lookup_email:
            lookup_email = (current_user.email or '').strip().lower()

        if not order_id or not lookup_email:
            flash('Vui lòng nhập mã đơn hàng và email đã dùng khi đặt hàng.', 'error')
            return render_template('order-lookup.html', found_order=None, status_steps=[], lookup_email=lookup_email)
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', lookup_email):
            flash('Email tra cứu không hợp lệ.', 'error')
            return render_template('order-lookup.html', found_order=None, status_steps=[], lookup_email=lookup_email)

        found_order = Order.query.join(User).filter(
            Order.id == order_id,
            func.lower(User.email) == lookup_email
        ).first()
        if not found_order:
            flash('Không tìm thấy đơn hàng phù hợp với thông tin đã nhập.', 'error')
        else:
            flash('Đã tìm thấy đơn hàng.', 'success')
            steps = ['pending', 'paid', 'shipped', 'delivered']
            reached = found_order.status
            if reached == 'cancelled':
                status_steps = [{'id': 'cancelled', 'label': 'Đã huỷ', 'done': True}]
            else:
                for step in steps:
                    status_steps.append({
                        'id': step,
                        'label': {
                            'pending': 'Chờ xử lý',
                            'paid': 'Đã xác nhận',
                            'shipped': 'Đang giao',
                            'delivered': 'Hoàn tất',
                        }[step],
                        'done': steps.index(step) <= steps.index(reached) if reached in steps else False
                    })
    return render_template('order-lookup.html', found_order=found_order, status_steps=status_steps, lookup_email=lookup_email)


def _mark_order_paid(order: Order, payment_ref: Optional[str] = None):
    order.payment_status = 'paid'
    order.status = 'paid'
    if payment_ref:
        order.payment_ref = payment_ref
    db.session.commit()


@app.route('/payment/momo/create/<int:order_id>')
@login_required
@limiter.limit("30 per minute")
def momo_create(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền thanh toán đơn hàng này.', 'error')
        return redirect(url_for('index'))
    if order.status == 'cancelled':
        flash('Đơn hàng đã bị hủy nên không thể tạo thanh toán MoMo.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    if order.payment_status == 'paid':
        return redirect(url_for('order_detail', order_id=order.id))
    if order.payment_method != 'MOMO':
        flash('Đơn hàng này không chọn MoMo.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    try:
        pay_url = _prepare_momo_payment(order)
        db.session.commit()
    except ValueError as exc:
        db.session.commit()
        flash(str(exc), 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    except Exception:
        db.session.rollback()
        app.logger.exception("Không thể tạo thanh toán MoMo cho order_id=%s", order.id)
        flash('Không thể tạo thanh toán MoMo lúc này. Vui lòng thử lại.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    return redirect(pay_url)


@app.route('/payment/momo/return')
@login_required
def momo_return():
    # This is browser return URL. Final confirmation should rely on IPN.
    order_id = _extract_momo_order_id(
        request.args.get('orderId', ''),
        request.args.get('extraData', '')
    )
    if order_id:
        result_code = request.args.get('resultCode', type=int)
        if result_code and result_code != 0:
            order = Order.query.get(order_id)
            if order and order.payment_status != 'paid':
                order.payment_status = 'failed'
                db.session.commit()
        return redirect(url_for('order_detail', order_id=order_id))
    flash('Không xác định được đơn hàng từ MoMo.', 'error')
    return redirect(url_for('index'))


@app.route('/payment/momo/ipn', methods=['POST'])
@csrf.exempt
@limiter.exempt
def momo_ipn():
    data = request.get_json(silent=True) or {}
    signature = data.get('signature', '')

    partner_code = app.config.get('MOMO_PARTNER_CODE', '')
    access_key = app.config.get('MOMO_ACCESS_KEY', '')
    secret_key = app.config.get('MOMO_SECRET_KEY', '')
    if not partner_code or not access_key or not secret_key:
        return jsonify({"message": "not_configured"}), 500

    # Build signature string according to MoMo IPN docs
    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={data.get('amount','')}"
        f"&extraData={data.get('extraData','')}"
        f"&message={data.get('message','')}"
        f"&orderId={data.get('orderId','')}"
        f"&orderInfo={data.get('orderInfo','')}"
        f"&orderType={data.get('orderType','')}"
        f"&partnerCode={data.get('partnerCode','')}"
        f"&payType={data.get('payType','')}"
        f"&requestId={data.get('requestId','')}"
        f"&responseTime={data.get('responseTime','')}"
        f"&resultCode={data.get('resultCode','')}"
        f"&transId={data.get('transId','')}"
    )
    expected = _hmac_sha256(secret_key, raw_signature)
    if signature != expected:
        return jsonify({"message": "invalid_signature"}), 400

    order_id = _extract_momo_order_id(data.get('orderId', ''), data.get('extraData', ''))
    if not order_id:
        return jsonify({"message": "invalid_order"}), 400
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "order_not_found"}), 404

    # Persist tx log
    tx = PaymentTransaction(
        order_id=order.id,
        provider='MOMO',
        amount=float(data.get('amount') or 0),
        status='paid' if int(data.get('resultCode', -1)) == 0 else 'failed',
        provider_ref=str(data.get('transId') or data.get('orderId') or ''),
        raw_response=json.dumps(data, ensure_ascii=False),
    )
    db.session.add(tx)

    if int(data.get('resultCode', -1)) == 0:
        # amount check
        try:
            paid_amount = int(data.get('amount', 0))
        except Exception:
            paid_amount = 0
        if int(round(order.total_amount)) == paid_amount:
            _mark_order_paid(order, payment_ref=str(data.get('transId') or ''))
            tx.status = 'paid'
        else:
            order.payment_status = 'failed'
            tx.status = 'failed'
            db.session.commit()
            return jsonify({"message": "amount_mismatch"}), 400

    db.session.commit()
    return jsonify({"message": "received"}), 200


@app.route('/payment/vnpay/create/<int:order_id>')
@login_required
@limiter.limit("30 per minute")
def vnpay_create(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền thanh toán đơn hàng này.', 'error')
        return redirect(url_for('index'))
    if order.status == 'cancelled':
        flash('Đơn hàng đã bị hủy nên không thể tạo thanh toán VNPAY.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    if order.payment_status == 'paid':
        return redirect(url_for('order_detail', order_id=order.id))
    if order.payment_method != 'VNPAY':
        flash('Đơn hàng này không chọn VNPAY.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    try:
        pay_url = _prepare_vnpay_payment(order)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    except Exception:
        db.session.rollback()
        app.logger.exception("Không thể tạo thanh toán VNPAY cho order_id=%s", order.id)
        flash('Không thể tạo thanh toán VNPAY lúc này. Vui lòng thử lại.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    return redirect(pay_url)


@app.route('/payment/vnpay/return')
@login_required
def vnpay_return():
    args = dict(request.args)
    secure_hash = args.pop('vnp_SecureHash', '')
    args.pop('vnp_SecureHashType', None)

    hash_secret = app.config.get('VNPAY_HASH_SECRET', '')
    if not hash_secret:
        flash('Chưa cấu hình VNPAY.', 'error')
        return redirect(url_for('index'))

    sorted_items = sorted(args.items())
    hashdata = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_items])
    expected = _vnpay_hmac_sha512(hash_secret, hashdata)
    if secure_hash != expected:
        flash('Chữ ký VNPAY không hợp lệ.', 'error')
        return redirect(url_for('index'))

    txn_ref = args.get('vnp_TxnRef', '')
    order_id = _extract_vnpay_order_id(txn_ref)
    if order_id:
        resp_code = args.get('vnp_ResponseCode')
        if resp_code and resp_code != '00':
            order = Order.query.get(order_id)
            if order and order.payment_status != 'paid':
                order.payment_status = 'failed'
                db.session.commit()
        return redirect(url_for('order_detail', order_id=order_id))
    flash('Không xác định được đơn hàng từ VNPAY.', 'error')
    return redirect(url_for('index'))


@app.route('/payment/vnpay/ipn', methods=['GET'])
@csrf.exempt
@limiter.exempt
def vnpay_ipn():
    # VNPAY calls IPN via GET
    args = dict(request.args)
    secure_hash = args.pop('vnp_SecureHash', '')
    args.pop('vnp_SecureHashType', None)

    hash_secret = app.config.get('VNPAY_HASH_SECRET', '')
    if not hash_secret:
        return "not_configured", 500

    sorted_items = sorted(args.items())
    hashdata = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_items])
    expected = _vnpay_hmac_sha512(hash_secret, hashdata)
    if secure_hash != expected:
        return "invalid_signature", 400

    txn_ref = args.get('vnp_TxnRef')
    resp_code = args.get('vnp_ResponseCode')
    amount = args.get('vnp_Amount')
    trans_no = args.get('vnp_TransactionNo')
    order_id = _extract_vnpay_order_id(txn_ref or '')
    if not order_id:
        return "invalid_order", 400
    order = Order.query.get(order_id)
    if not order:
        return "order_not_found", 404

    tx = PaymentTransaction(
        order_id=order.id,
        provider='VNPAY',
        amount=float(int(amount or 0) / 100),
        status='paid' if resp_code == '00' else 'failed',
        provider_ref=str(trans_no or txn_ref),
        raw_response=json.dumps(args, ensure_ascii=False),
    )
    db.session.add(tx)

    if resp_code == '00':
        try:
            paid = int(amount or 0) // 100
        except Exception:
            paid = 0
        if int(round(order.total_amount)) == int(paid):
            _mark_order_paid(order, payment_ref=str(trans_no or ''))
            tx.status = 'paid'
        else:
            order.payment_status = 'failed'
            db.session.commit()
            return "amount_mismatch", 400
    else:
        order.payment_status = 'failed'

    db.session.commit()
    return "ok", 200

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login_id = (request.form.get('login_id') or '').strip()
        password = request.form.get('password')
        
        # Tìm user theo email hoặc username không phân biệt chữ hoa, chữ thường
        # Đảm bảo người dùng gõ sai hoa/thường vẫn tìm ra tài khoản (chuẩn UX/Security chống trùng lặp)
        user = User.query.filter(
            (func.lower(User.username) == login_id.lower()) | 
            (func.lower(User.email) == login_id.lower())
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            remember_me = bool(request.form.get('remember'))
            login_user(user, remember=remember_me)
            _merge_session_cart_into_user_cart(user)
            next_page = request.args.get('next')
            if next_page and _is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Email/Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    first_name = (request.form.get('first_name') or '').strip()
    last_name = (request.form.get('last_name') or '').strip()
    username = (request.form.get('username') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    confirm_password = request.form.get('confirm_password') or ''
    agreed_policy = bool(request.form.get('agree_policy'))

    if not first_name or not last_name or not username or not email or not password:
        flash('Vui lòng điền đầy đủ Họ, Tên, Tên đăng nhập, Email và Mật khẩu.', 'error')
        return redirect(url_for('login') + '#register')

    if not agreed_policy:
        flash('Bạn cần đồng ý với chính sách và điều khoản trước khi đăng ký.', 'error')
        return redirect(url_for('login') + '#register')

    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        flash('Email không hợp lệ.', 'error')
        return redirect(url_for('login') + '#register')

    if not re.fullmatch(r'^[A-Za-z0-9_.-]{4,30}$', username):
        flash('Tên đăng nhập chỉ gồm chữ cái, số, dấu chấm, gạch dưới hoặc gạch ngang và dài 4-30 ký tự.', 'error')
        return redirect(url_for('login') + '#register')

    pw_pattern = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')
    if not pw_pattern.match(password):
        flash('Mật khẩu phải có ít nhất 8 ký tự, gồm chữ HOA, chữ thường và số.', 'error')
        return redirect(url_for('login') + '#register')

    if password != confirm_password:
        flash('Xác nhận mật khẩu không khớp.', 'error')
        return redirect(url_for('login') + '#register')

    # Kiểm tra trùng lập không phân biệt hoa thường để tránh tạo ra 2 tài khoản "Hana" và "hana"
    if User.query.filter(func.lower(User.email) == email.lower()).first():
        flash('Email này đã được sử dụng. Vui lòng dùng email khác.', 'error')
        return redirect(url_for('login') + '#register')
        
    if User.query.filter(func.lower(User.username) == username.lower()).first():
        flash('Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.', 'error')
        return redirect(url_for('login') + '#register')

    new_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
        policy_accepted_at=datetime.utcnow(),
    )
    db.session.add(new_user)
    db.session.commit()
    flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('index'))


@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def forgot_password():
    """Tạo token reset mật khẩu và gửi qua email hoặc console log an toàn."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    entered_email = (request.form.get('email') or request.args.get('email') or '').strip()
    if request.method == 'POST':
        email = entered_email.lower()
        if not email:
            flash('Vui lòng nhập địa chỉ email.', 'error')
        elif not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            flash('Địa chỉ email không hợp lệ.', 'error')
        else:
            delivery_failed = False
            user = User.query.filter(func.lower(User.email) == email).first()
            if user:
                token = user.generate_reset_token(expires_minutes=int(app.config.get('PASSWORD_RESET_EXPIRES_MINUTES') or 30))
                # Use the current request host for password reset links so local demos
                # are not blocked by stale PUBLIC_URL/ngrok values.
                reset_url = url_for('reset_password', token=token, _external=True)
                if _send_password_reset_email(user, reset_url):
                    db.session.commit()
                else:
                    db.session.rollback()
                    delivery_failed = True
            flash('Nếu email tồn tại trong hệ thống, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu.', 'info')
            if delivery_failed:
                flash('Dịch vụ email đang tạm thời gián đoạn. Vui lòng thử lại sau hoặc liên hệ quản trị viên.', 'error')

    return render_template('forgot-password.html', entered_email=entered_email)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def reset_password(token):
    """Xác thực token và cho phép đặt lại mật khẩu."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    token_hash = User.hash_reset_token(token)
    user = User.query.filter(
        or_(User.reset_token == token_hash, User.reset_token == token)
    ).first()
    token_matches = bool(user and user.reset_token in {token_hash, token})

    if not user or not token_matches or not user.is_reset_token_valid():
        flash('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_pw = request.form.get('password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if len(new_pw) < 8:
            flash('Mật khẩu phải có ít nhất 8 ký tự.', 'error')
            return render_template('reset-password.html', token=token)

        pw_pattern = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')
        if not pw_pattern.match(new_pw):
            flash('Mật khẩu cần có ít nhất 1 chữ HOA, 1 chữ thường và 1 chữ số.', 'error')
            return render_template('reset-password.html', token=token)

        if new_pw != confirm_pw:
            flash('Xác nhận mật khẩu không khớp.', 'error')
            return render_template('reset-password.html', token=token)

        user.password_hash = generate_password_hash(new_pw, method='pbkdf2:sha256')
        user.clear_reset_token()
        db.session.commit()
        flash('Đặt lại mật khẩu thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('reset-password.html', token=token)


@app.route('/contact', methods=['GET', 'POST'])
@limiter.limit("30 per hour")
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', '')
        message = request.form.get('message')
        contact_entry = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(contact_entry)
        db.session.commit()
        flash('Cảm ơn bạn! Chúng tôi sẽ phản hồi sớm nhất.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

# --- ADMIN ROUTES ---

def get_analytics_data():
    """Tổng hợp dữ liệu analytics cho admin dashboard"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Orders stats
    orders_count = Order.query.count()
    orders_today = Order.query.filter(Order.created_at >= today_start).count()
    orders_month = Order.query.filter(Order.created_at >= month_start).count()

    # Revenue
    total_revenue_row = db.session.query(func.sum(Order.total_amount)).scalar()
    total_revenue = total_revenue_row or 0

    revenue_month_row = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= month_start
    ).scalar()
    revenue_month = revenue_month_row or 0

    revenue_today_row = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= today_start
    ).scalar()
    revenue_today = revenue_today_row or 0

    # Doanh thu 7 ngày gần nhất
    revenue_7days = []
    labels_7days = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        rev = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= day_start,
            Order.created_at < day_end
        ).scalar() or 0
        revenue_7days.append(float(rev))
        labels_7days.append(day.strftime('%d/%m'))

    # Đơn hàng 30 ngày
    orders_30days = []
    labels_30days = []
    for i in range(29, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        cnt = Order.query.filter(
            Order.created_at >= day_start,
            Order.created_at < day_end
        ).count()
        orders_30days.append(cnt)
        labels_30days.append(day.strftime('%d/%m'))

    # Top sản phẩm bán chạy
    top_products_raw = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * OrderItem.price).label('revenue')
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .group_by(Product.id)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(5).all()

    top_products = [{'name': r[0], 'sold': int(r[1] or 0), 'revenue': float(r[2] or 0)} for r in top_products_raw]

    # Phân bổ doanh thu theo danh mục
    category_revenue_raw = db.session.query(
        Category.name,
        func.sum(OrderItem.quantity * OrderItem.price).label('revenue')
    ).join(Product, Category.id == Product.category_id)\
     .join(OrderItem, Product.id == OrderItem.product_id)\
     .group_by(Category.id)\
     .order_by(func.sum(OrderItem.quantity * OrderItem.price).desc())\
     .all()
    category_labels = [r[0] for r in category_revenue_raw]
    category_data = [float(r[1] or 0) for r in category_revenue_raw]

    # Đơn hàng gần đây
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    recent_cancelled_orders = Order.query.filter_by(status='cancelled')\
        .order_by(Order.cancelled_at.desc(), Order.created_at.desc())\
        .limit(5).all()

    # Order status breakdown
    status_counts = {
        'pending': Order.query.filter_by(status='pending').count(),
        'paid': Order.query.filter_by(status='paid').count(),
        'shipped': Order.query.filter_by(status='shipped').count(),
        'delivered': Order.query.filter_by(status='delivered').count(),
        'cancelled': Order.query.filter_by(status='cancelled').count(),
    }

    return {
        'orders_count': orders_count,
        'orders_today': orders_today,
        'orders_month': orders_month,
        'total_revenue': total_revenue,
        'revenue_month': revenue_month,
        'revenue_today': revenue_today,
        'revenue_7days': revenue_7days,
        'labels_7days': labels_7days,
        'orders_30days': orders_30days,
        'labels_30days': labels_30days,
        'top_products': top_products,
        'category_labels': category_labels,
        'category_data': category_data,
        'recent_orders': recent_orders,
        'recent_cancelled_orders': recent_cancelled_orders,
        'status_counts': status_counts,
    }


@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này.', 'error')
        return redirect(url_for('index'))
    products_count = Product.query.count()
    users_count = User.query.count()
    all_products = Product.query.order_by(Product.id.desc()).all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    categories = Category.query.all()
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    payment_transactions = PaymentTransaction.query.order_by(PaymentTransaction.created_at.desc()).limit(30).all()
    analytics = get_analytics_data()

    return render_template('admin.html',
                           products_count=products_count,
                           users_count=users_count,
                           products=all_products,
                           contacts=contacts,
                           categories=categories,
                           coupons=coupons,
                           payment_transactions=payment_transactions,
                           now=datetime.now(),
                           analytics=analytics)


@app.route('/admin/product/add', methods=['POST'])
@login_required
def admin_add_product():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    name = request.form.get('name')
    price = float(request.form.get('price', 0))
    old_price_str = request.form.get('old_price', '')
    old_price = float(old_price_str) if old_price_str else None
    description = request.form.get('description', '')
    
    category_action = request.form.get('category_action', '1|')
    cat_parts = category_action.split('|')
    category_id = int(cat_parts[0])
    subcategory = cat_parts[1] if len(cat_parts) > 1 and cat_parts[1] else None

    is_new = bool(request.form.get('is_new'))
    is_on_sale = bool(request.form.get('is_on_sale'))
    stock = int(request.form.get('stock', 100))

    # Xử lý sizes tùy chỉnh
    sizes_raw = request.form.get('sizes_input', '').strip()
    sizes_list = []
    if sizes_raw:
        sizes_list = [s.strip() for s in sizes_raw.replace('\n', ',').split(',') if s.strip()]
    sizes_json = json.dumps(sizes_list, ensure_ascii=False) if sizes_list else None

    # Xử lý upload ảnh (tối đa 5 ảnh)
    image_url = request.form.get('image_url', '')
    files = request.files.getlist('image_files')
    extra_urls = []
    
    # Process multiple image files
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            url = url_for('static', filename=f'uploads/{filename}')
            if not image_url:
                image_url = url
            else:
                extra_urls.append(url)
                
    # Xử lý upload video
    video_url = request.form.get('video_url', '')
    video_file = request.files.get('video_file')
    if video_file and video_file.filename and allowed_file(video_file.filename):
        ext = video_file.filename.rsplit('.', 1)[1].lower()
        filename = f"vid_{uuid.uuid4().hex}.{ext}"
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        video_url = url_for('static', filename=f'uploads/{filename}')

    # Giới hạn mảng ảnh phụ (tối đa 8 ảnh phụ + 1 ảnh chính = 9)
    extra_urls = extra_urls[:8]
    extra_images_json = json.dumps(extra_urls) if extra_urls else None

    product = Product(
        name=name, price=price, old_price=old_price,
        image_url=image_url, extra_images=extra_images_json, video_url=video_url,
        description=description, sizes=sizes_json,
        category_id=category_id, subcategory=subcategory, is_new=is_new, is_on_sale=is_on_sale, stock=stock
    )
    db.session.add(product)
    db.session.commit()
    flash(f'Đã thêm sản phẩm "{name}" thành công!', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=products')


@app.route('/admin/product/edit/<int:product_id>', methods=['POST'])
@login_required
def admin_edit_product(product_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    product = Product.query.get_or_404(product_id)

    product.name = request.form.get('name', product.name).strip()
    product.price = float(request.form.get('price', product.price) or 0)
    old_price_str = request.form.get('old_price', '').strip()
    product.old_price = float(old_price_str) if old_price_str else None
    product.description = request.form.get('description', '').strip()
    
    category_action = request.form.get('category_action', f"{product.category_id}|{product.subcategory or ''}")
    cat_parts = category_action.split('|')
    product.category_id = int(cat_parts[0])
    product.subcategory = cat_parts[1] if len(cat_parts) > 1 and cat_parts[1] else None
    
    product.stock = int(request.form.get('stock', product.stock or 100))
    product.is_new = bool(request.form.get('is_new'))
    product.is_on_sale = bool(request.form.get('is_on_sale'))

    # Update image if new ones uploaded
    files = request.files.getlist('image_files')
    extra_urls = []
    has_new_images = False
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            url = url_for('static', filename=f'uploads/{filename}')
            if not has_new_images:
                product.image_url = url
                has_new_images = True
            else:
                extra_urls.append(url)
    
    if extra_urls:
        product.extra_images = json.dumps(extra_urls)

    # Allow setting a direct URL if provided
    direct_image_url = request.form.get('direct_image_url', '').strip()
    if direct_image_url:
        product.image_url = direct_image_url

    # Sizes
    sizes_raw = request.form.get('sizes_input', '').strip()
    if sizes_raw:
        sizes_list = [s.strip() for s in sizes_raw.replace('\n', ',').split(',') if s.strip()]
        product.sizes = json.dumps(sizes_list, ensure_ascii=False) if sizes_list else None
    else:
        product.sizes = None

    db.session.commit()
    flash(f'Đã cập nhật sản phẩm "{product.name}" thành công!', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=products')


@app.route('/admin/coupon/add', methods=['POST'])
@login_required
def admin_add_coupon():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    code = (request.form.get('code') or '').strip().upper()
    coupon_type = (request.form.get('coupon_type') or 'percent').strip().lower()
    value = float(request.form.get('value') or 0)
    min_subtotal = float(request.form.get('min_subtotal') or 0)
    max_uses_raw = (request.form.get('max_uses') or '').strip()
    expires_raw = (request.form.get('expires_at') or '').strip()

    if not code:
        flash('Mã coupon không được để trống.', 'error')
        return redirect(url_for('admin_dashboard') + '?tab=marketing')
    if coupon_type not in ['percent', 'fixed', 'shipping']:
        coupon_type = 'percent'
    if value <= 0:
        flash('Giá trị coupon phải lớn hơn 0.', 'error')
        return redirect(url_for('admin_dashboard') + '?tab=marketing')
    if Coupon.query.filter_by(code=code).first():
        flash('Mã coupon đã tồn tại trong hệ thống.', 'error')
        return redirect(url_for('admin_dashboard') + '?tab=marketing')
    if code in app.config.get('COUPONS', {}):
        flash('Mã coupon này là mã mặc định của hệ thống, không thể tạo trùng.', 'error')
        return redirect(url_for('admin_dashboard') + '?tab=marketing')


    max_uses = int(max_uses_raw) if max_uses_raw.isdigit() else None
    expires_at = None
    if expires_raw:
        try:
            expires_at = datetime.strptime(expires_raw, '%Y-%m-%dT%H:%M')
        except Exception:
            flash('Định dạng ngày hết hạn không hợp lệ.', 'error')
            return redirect(url_for('admin_dashboard') + '?tab=marketing')

    coupon = Coupon(
        code=code,
        coupon_type=coupon_type,
        value=value,
        min_subtotal=min_subtotal,
        max_uses=max_uses,
        expires_at=expires_at,
        is_active=True,
    )
    db.session.add(coupon)
    db.session.commit()
    flash(f'Đã tạo coupon {code}.', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=marketing')


@app.route('/admin/coupon/delete/<int:coupon_id>', methods=['POST'])
@login_required
def admin_delete_coupon(coupon_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Đã xóa coupon.', 'info')
    return redirect(url_for('admin_dashboard') + '?tab=marketing')


@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    product = Product.query.get_or_404(product_id)
    # Xóa ảnh upload nếu có
    if product.image_url and '/static/uploads/' in product.image_url:
        filename = product.image_url.split('/static/uploads/')[-1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
    # Ngăn rác dữ liệu/crash trang web của người dùng bằng cách xoá sản phẩm khỏi giỏ hàng/wishlist
    CartItem.query.filter_by(product_id=product.id).delete()
    WishlistItem.query.filter_by(product_id=product.id).delete()
    Review.query.filter_by(product_id=product.id).delete()
    
    db.session.delete(product)
    db.session.commit()
    flash('Đã xóa sản phẩm và cập nhật giỏ hàng khách hàng.', 'info')
    return redirect(url_for('admin_dashboard') + '?tab=products')


@app.route('/admin/order/<int:order_id>/status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        if order.status == 'cancelled' and new_status != 'cancelled':
            flash(f'Đơn hàng #{order_id} đã bị hủy và không thể chuyển lại trạng thái khác.', 'error')
            return redirect(url_for('admin_dashboard') + '?tab=orders')
        if new_status in ['shipped', 'delivered'] and order.payment_method in ['MOMO', 'VNPAY'] and order.payment_status != 'paid':
            flash(f'Không thể chuyển đơn #{order_id} sang trạng thái giao hàng khi thanh toán online chưa hoàn tất.', 'error')
            return redirect(url_for('admin_dashboard') + '?tab=orders')
        if new_status == 'cancelled':
            if order.status != 'cancelled':
                _cancel_order(order, request.form.get('cancel_reason') or '', actor='admin')
                db.session.commit()
            flash(f'Đã hủy đơn hàng #{order_id}.', 'success')
        else:
            order.status = new_status
            if new_status == 'paid':
                order.payment_status = 'paid'
            elif new_status == 'delivered' and order.payment_method == 'COD' and order.payment_status != 'paid':
                order.payment_status = 'paid'
            db.session.commit()
            flash(f'Đã cập nhật trạng thái đơn hàng #{order_id}.', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=orders')


# ── MY ORDERS ──────────────────────────────────────────────────────────────────
@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template('my-orders.html', orders=orders)


# ── PROFILE ─────────────────────────────────────────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'update_info':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = _normalize_phone(request.form.get('phone', ''))
            address = request.form.get('address', '').strip()
            birth_date_raw = request.form.get('birth_date', '').strip()
            birth_date = _parse_birth_date(birth_date_raw)

            if not first_name or not last_name or not username or not email:
                flash('Vui lòng điền đầy đủ Họ, Tên, Tên đăng nhập và Email.', 'error')
                return redirect(url_for('profile'))
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
                flash('Email không hợp lệ.', 'error')
                return redirect(url_for('profile'))
            if not re.fullmatch(r'^[A-Za-z0-9_.-]{4,30}$', username):
                flash('Tên đăng nhập chỉ gồm chữ cái, số, dấu chấm, gạch dưới hoặc gạch ngang và dài 4-30 ký tự.', 'error')
                return redirect(url_for('profile'))
            if phone and not re.fullmatch(r'(0|\+84)\d{9,10}', phone):
                flash('Số điện thoại không hợp lệ.', 'error')
                return redirect(url_for('profile'))
            if birth_date_raw and not birth_date:
                flash('Ngày sinh không hợp lệ.', 'error')
                return redirect(url_for('profile'))
            if User.query.filter(func.lower(User.username) == username.lower(), User.id != current_user.id).first():
                flash('Tên đăng nhập đã được sử dụng bởi tài khoản khác.', 'error')
                return redirect(url_for('profile'))
            if User.query.filter(func.lower(User.email) == email.lower(), User.id != current_user.id).first():
                flash('Email đã được sử dụng bởi tài khoản khác.', 'error')
                return redirect(url_for('profile'))
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.username = username
            current_user.email = email
            current_user.phone = phone or None
            current_user.address = address or None
            current_user.birth_date = birth_date
            db.session.commit()
            flash('Cập nhật thông tin thành công!', 'success')

        elif action == 'change_password':
            current_pw  = request.form.get('current_password', '')
            new_pw      = request.form.get('new_password', '')
            confirm_pw  = request.form.get('confirm_password', '')
            if not check_password_hash(current_user.password_hash, current_pw):
                flash('Mật khẩu hiện tại không đúng.', 'error')
                return redirect(url_for('profile'))
            if len(new_pw) < 8:
                flash('Mật khẩu mới phải có ít nhất 8 ký tự.', 'error')
                return redirect(url_for('profile'))
            pw_pattern = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')
            if not pw_pattern.match(new_pw):
                flash('Mật khẩu mới cần có ít nhất 1 chữ HOA, 1 chữ thường và 1 chữ số.', 'error')
                return redirect(url_for('profile'))
            if new_pw != confirm_pw:
                flash('Xác nhận mật khẩu không khớp.', 'error')
                return redirect(url_for('profile'))
            current_user.password_hash = generate_password_hash(new_pw)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')

        return redirect(url_for('profile'))

    order_count = Order.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', order_count=order_count)


if __name__ == '__main__':
    missing_payment_env = _missing_payment_env_vars()
    if missing_payment_env and not _is_debug_mode:
        raise RuntimeError(f"Missing payment environment variables: {missing_payment_env}")
    debug = os.environ.get('FLASK_DEBUG', '').strip() in ['1', 'true', 'True']
    port = int(os.environ.get('PORT', '5011'))
    app.run(debug=debug, port=port)
