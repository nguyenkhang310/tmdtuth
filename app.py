import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func

from extensions import db, login_manager
from models import User, Category, Product, Cart, CartItem, Order, OrderItem, Review, Contact

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)
app.config['SECRET_KEY'] = 'dev_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Custom Jinja2 filters
@app.template_filter('enumerate')
def jinja_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)


# Upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

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

    conn.commit()
    conn.close()


db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def index():
    new_products = Product.query.filter_by(is_new=True).limit(8).all()
    sale_products = Product.query.filter_by(is_on_sale=True).limit(8).all()
    return render_template('index.html', new_products=new_products, sale_products=sale_products)

@app.route('/products')
def products():
    query = Product.query

    category_slug = request.args.get('category')
    sale = request.args.get('sale')
    search_q = request.args.get('q')
    sort = request.args.get('sort', 'newest')

    if category_slug:
        category = Category.query.filter(Category.name.ilike(f'%{category_slug}%')).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if sale == 'true':
        query = query.filter_by(is_on_sale=True)

    if search_q:
        query = query.filter(Product.name.ilike(f'%{search_q}%'))

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.desc())

    all_products = query.all()
    return render_template('products.html', products=all_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    return render_template('product-detail.html', product=product, reviews=reviews)

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
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

@app.route('/cart')
@login_required
def cart():
    active_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not active_cart:
        active_cart = Cart(user_id=current_user.id)
        db.session.add(active_cart)
        db.session.commit()
    return render_template('cart.html', cart=active_cart)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    active_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not active_cart:
        active_cart = Cart(user_id=current_user.id)
        db.session.add(active_cart)
        db.session.commit()

    existing = CartItem.query.filter_by(cart_id=active_cart.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(cart_id=active_cart.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    flash('Đã thêm sản phẩm vào giỏ hàng!', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    active_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not active_cart or not active_cart.items:
        flash('Giỏ hàng của bạn đang trống.', 'error')
        return redirect(url_for('cart'))
    if request.method == 'POST':
        total = sum(item.product.price * item.quantity for item in active_cart.items)
        order = Order(user_id=current_user.id, total_amount=total, status='pending')
        db.session.add(order)
        db.session.flush()
        for item in active_cart.items:
            oi = OrderItem(order_id=order.id, product_id=item.product_id,
                           quantity=item.quantity, price=item.product.price)
            db.session.add(oi)
        # Clear cart
        for item in list(active_cart.items):
            db.session.delete(item)
        db.session.commit()
        flash('Đặt hàng thành công! Chúng tôi sẽ liên hệ với bạn sớm.', 'success')
        return redirect(url_for('index'))
    return render_template('cart.html', cart=active_cart, checkout_mode=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        user = User.query.filter(
            (User.username == login_id) | (User.email == login_id)
        ).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Email hoặc mật khẩu không đúng.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash('Email này đã được sử dụng. Vui lòng dùng email khác.', 'error')
        return redirect(url_for('login') + '#register')

    new_user = User(
        username=name,
        email=email,
        password_hash=generate_password_hash(password, method='pbkdf2:sha256')
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

@app.route('/contact', methods=['GET', 'POST'])
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
    analytics = get_analytics_data()

    return render_template('admin.html',
                           products_count=products_count,
                           users_count=users_count,
                           products=all_products,
                           contacts=contacts,
                           categories=categories,
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
    category_id = int(request.form.get('category_id', 1))
    is_new = bool(request.form.get('is_new'))
    is_on_sale = bool(request.form.get('is_on_sale'))

    # Xử lý upload ảnh: ưu tiên file upload, nếu không thì dùng URL
    image_url = request.form.get('image_url', '')
    file = request.files.get('image_file')
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = url_for('static', filename=f'uploads/{filename}')

    product = Product(
        name=name, price=price, old_price=old_price,
        image_url=image_url, description=description,
        category_id=category_id, is_new=is_new, is_on_sale=is_on_sale
    )
    db.session.add(product)
    db.session.commit()
    flash(f'Đã thêm sản phẩm "{name}" thành công!', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=products')


@app.route('/admin/product/delete/<int:product_id>')
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
    db.session.delete(product)
    db.session.commit()
    flash('Đã xóa sản phẩm.', 'info')
    return redirect(url_for('admin_dashboard') + '?tab=products')


@app.route('/admin/order/<int:order_id>/status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Đã cập nhật trạng thái đơn hàng #{order_id}.', 'success')
    return redirect(url_for('admin_dashboard') + '?tab=analytics')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_db_schema()
    app.run(debug=True, port=5000)
