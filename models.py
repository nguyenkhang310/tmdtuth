from __future__ import annotations

from extensions import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import hashlib
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='user') # 'admin' or 'user'
    policy_accepted_at = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    @property
    def full_name(self) -> str:
        parts = [part.strip() for part in [self.last_name or '', self.first_name or ''] if part and part.strip()]
        return ' '.join(parts).strip()

    @property
    def display_name(self) -> str:
        return self.full_name or self.username

    @staticmethod
    def hash_reset_token(token: str) -> str:
        return hashlib.sha256((token or '').encode('utf-8')).hexdigest()

    def generate_reset_token(self, expires_minutes: int = 30) -> str:
        """Tạo token reset mật khẩu có thời hạn, lưu hash vào model."""
        token = secrets.token_urlsafe(48)
        self.reset_token = self.hash_reset_token(token)
        self.reset_token_expires = datetime.utcnow() + timedelta(minutes=expires_minutes)
        return token

    def clear_reset_token(self):
        """Xóa token sau khi đã dùng."""
        self.reset_token = None
        self.reset_token_expires = None

    def is_reset_token_valid(self, token: str | None = None) -> bool:
        """Kiểm tra token còn hạn và khớp hash hay không."""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if token and self.reset_token != self.hash_reset_token(token):
            return False
        return datetime.utcnow() < self.reset_token_expires
    
    carts = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    extra_images = db.Column(db.Text, nullable=True) # JSON list of URLs
    video_url = db.Column(db.String(500), nullable=True)
    stock = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory = db.Column(db.String(100), nullable=True)
    
    is_new = db.Column(db.Boolean, default=False)
    is_on_sale = db.Column(db.Boolean, default=False)
    sizes = db.Column(db.Text, nullable=True)  # JSON list of size strings, e.g. ["S","M","L","XL"] or ["One Size"]
    
    reviews = db.relationship('Review', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product_ref', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    product = db.relationship('Product')


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uq_wishlist_user_product'),
    )

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    # Order lifecycle status (fulfillment)
    status = db.Column(db.String(50), default='pending') # pending, paid, shipped, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Shipping/customer info (captured at checkout)
    shipping_name = db.Column(db.String(150), nullable=True)
    shipping_phone = db.Column(db.String(30), nullable=True)
    shipping_address = db.Column(db.String(500), nullable=True)
    note = db.Column(db.String(500), nullable=True)
    cancel_reason = db.Column(db.String(500), nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    # Payment info
    payment_method = db.Column(db.String(50), default='COD')  # COD, BANK_TRANSFER, MOMO, VNPAY
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, initiated, paid, failed, cancelled
    payment_ref = db.Column(db.String(200), nullable=True)  # gateway transaction ref
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False)  # MOMO, VNPAY
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='initiated')  # initiated, paid, failed, cancelled
    provider_ref = db.Column(db.String(200), nullable=True)  # transactionId / vnp_TxnRef
    raw_request = db.Column(db.Text, nullable=True)
    raw_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref=db.backref('transactions', lazy=True, cascade='all, delete-orphan'))


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    coupon_type = db.Column(db.String(20), nullable=False, default='percent')  # percent, fixed, shipping
    value = db.Column(db.Float, nullable=False, default=0)
    min_subtotal = db.Column(db.Float, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # price at the time of purchase
    
    product = db.relationship('Product', overlaps='order_items,product_ref')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
