"""
Script để thêm sản phẩm mẫu bổ sung vào DB (không xóa dữ liệu cũ).
Chạy: python add_more_products.py
"""
from app import app
from extensions import db
from models import Product, Category

EXTRA_PRODUCTS = [
    # ===== ÁO =====
    {"name": "Áo Thun Trơn Basic Heavyweight", "price": 270000, "old_price": 350000,
     "image_url": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": True,
     "description": "Áo thun trơn 100% cotton 230g heavyweight, không bai không nhão. Màu sắc phong phú."},
    {"name": "Áo Khoác Bomber Thêu Hoa", "price": 890000, "old_price": 1200000,
     "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": True,
     "description": "Áo khoác bomber thêu hoa tinh xảo, phong cách harajuku trendy."},
    {"name": "Áo Sơ Mi Flannel Kẻ Caro", "price": 450000,
     "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": False,
     "description": "Áo sơ mi flannel kẻ caro ấm áp mùa thu đông, chất liệu cao cấp."},
    {"name": "Áo Len Turtleneck Rib-Knit", "price": 620000,
     "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": False,
     "description": "Áo len cổ lọ rib-knit dày dặn, giữ ấm tốt, form ôm nhẹ tôn dáng."},
    {"name": "Áo Croptop Halter Backless", "price": 320000, "old_price": 420000,
     "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": True,
     "description": "Áo croptop halter hở lưng sexy, phù hợp đi biển hoặc sự kiện mùa hè."},
    {"name": "Áo Blazer Tweed Houndstooth", "price": 1350000, "old_price": 1800000,
     "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&q=80",
     "category": "Áo", "is_new": False, "is_on_sale": True,
     "description": "Áo blazer tweed họa tiết houndstooth cổ điển, chuẩn office look."},
    {"name": "Áo Tank Top Rib Cotton", "price": 180000,
     "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80",
     "category": "Áo", "is_new": True, "is_on_sale": False,
     "description": "Áo ba lỗ rib cotton co giãn 4 chiều, thoáng mát mùa hè."},
    {"name": "Áo Sơ Mi Linen Trắng Tinh", "price": 480000,
     "image_url": "https://images.unsplash.com/photo-1540411025311-95e2dd7565ce?w=600&q=80",
     "category": "Áo", "is_new": False, "is_on_sale": False,
     "description": "Áo sơ mi linen trắng tinh khôi, thoáng mát và phong cách tối giản."},

    # ===== QUẦN =====
    {"name": "Quần Jean Mom High-Waist", "price": 680000, "old_price": 890000,
     "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80",
     "category": "Quần", "is_new": True, "is_on_sale": True,
     "description": "Quần jean mom dáng cạp cao, wash vintage cực trend, tôn dáng hiệu quả."},
    {"name": "Quần Shorts Linen Thanh Lịch", "price": 320000,
     "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4851b2?w=600&q=80",
     "category": "Quần", "is_new": True, "is_on_sale": False,
     "description": "Quần short linen 100% tự nhiên, thanh lịch và thoáng mát cho mùa hè."},
    {"name": "Quần Legging Thể Thao Cao Cấp", "price": 350000, "old_price": 450000,
     "image_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=600&q=80",
     "category": "Quần", "is_new": True, "is_on_sale": True,
     "description": "Quần legging thể thao co giãn 4 chiều, tôn dáng và chống nhìn xuyên."},
    {"name": "Quần Tây Ống Suông Linen", "price": 590000,
     "image_url": "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=600&q=80",
     "category": "Quần", "is_new": False, "is_on_sale": False,
     "description": "Quần tây ống suông chất linen cao cấp, phù hợp đi làm và dự sự kiện."},
    {"name": "Quần Baggy Jeans Y2K", "price": 750000, "old_price": 950000,
     "image_url": "https://images.unsplash.com/photo-1555685812-4b943f1cb0eb?w=600&q=80",
     "category": "Quần", "is_new": True, "is_on_sale": True,
     "description": "Quần baggy jeans phong cách Y2K, form rộng cực cool, wash đặc biệt."},
    {"name": "Quần Palazzo Satin Nhũ", "price": 680000,
     "image_url": "https://images.unsplash.com/photo-1573408301185-9519f94bf0db?w=600&q=80",
     "category": "Quần", "is_new": True, "is_on_sale": False,
     "description": "Quần palazzo satin nhũ bóng nhẹ sang trọng, phù hợp dự tiệc và sự kiện."},

    # ===== VÁY =====
    {"name": "Chân Váy Pleated Mini Pastel", "price": 480000,
     "image_url": "https://images.unsplash.com/photo-1572804013427-4d7ca7268217?w=600&q=80",
     "category": "Váy", "is_new": True, "is_on_sale": False,
     "description": "Chân váy xếp ly mini màu pastel nhẹ nhàng, phong cách fairy/coquette."},
    {"name": "Đầm Trễ Vai Satine Dự Tiệc", "price": 1150000, "old_price": 1500000,
     "image_url": "https://images.unsplash.com/photo-1514996937319-344454492b37?w=600&q=80",
     "category": "Váy", "is_new": True, "is_on_sale": True,
     "description": "Đầm trễ vai satin sang trọng, form ôm nhẹ, phù hợp dự tiệc và prom."},
    {"name": "Váy Tweed Mini Phong Cách Chanel", "price": 980000, "old_price": 1300000,
     "image_url": "https://images.unsplash.com/photo-1566479179817-0b6491e1e4da?w=600&q=80",
     "category": "Váy", "is_new": False, "is_on_sale": True,
     "description": "Váy tweed mini phong cách Chanel cổ điển, viền kim tuyến tinh tế."},
    {"name": "Đầm Babydoll Floral Vintage", "price": 550000,
     "image_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600&q=80",
     "category": "Váy", "is_new": True, "is_on_sale": False,
     "description": "Đầm babydoll họa tiết hoa vintage, tay phồng nhẹ đáng yêu, thoáng mát."},
    {"name": "Chân Váy Denim Midi A-line", "price": 620000,
     "image_url": "https://images.unsplash.com/photo-1582533561751-ef6f6ab93a2e?w=600&q=80",
     "category": "Váy", "is_new": True, "is_on_sale": False,
     "description": "Chân váy denim midi A-line cổ điển, dễ phối với nhiều kiểu áo."},
    {"name": "Đầm Ôm Cổ Yếm Nữ Tính", "price": 720000, "old_price": 950000,
     "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80",
     "category": "Váy", "is_new": False, "is_on_sale": True,
     "description": "Đầm ôm cổ yếm nữ tính, chiều dài midi, chất liệu satin nhẹ."},
    {"name": "Váy Xòe Floral Maxi Resort", "price": 850000,
     "image_url": "https://images.unsplash.com/photo-1572804013310-6b0f3bb54694?w=600&q=80",
     "category": "Váy", "is_new": True, "is_on_sale": False,
     "description": "Váy maxi hoa rực rỡ kiểu resort, thoáng mát và bay bổng cho mùa hè."},

    # ===== PHỤ KIỆN =====
    {"name": "Túi Chanel Boy Bag Mini", "price": 2200000, "old_price": 2800000,
     "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": True,
     "description": "Túi boy bag mini phong cách Chanel, da PU cao cấp khóa CC, đầy sang trọng."},
    {"name": "Nón Bucket Hat Canvas", "price": 220000,
     "image_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
     "description": "Nón bucket hat canvas unisex, chống nắng hiệu quả, dễ phối đồ."},
    {"name": "Kính Mát Cat-Eye Retro", "price": 380000, "old_price": 520000,
     "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": True,
     "description": "Kính mát cat-eye retro gọng nhựa ace, tròng UV400, phong cách cổ điển."},
    {"name": "Vòng Tay Pearl Ngọc Trai", "price": 280000,
     "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
     "description": "Vòng tay ngọc trai nhân tạo cao cấp, phong cách coquette đang hot."},
    {"name": "Belt Bag / Túi Đeo Hông", "price": 420000, "old_price": 580000,
     "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": True,
     "description": "Túi đeo hông belt bag tiện lợi, da PU chống nước, phù hợp du lịch."},
    {"name": "Beret Len Mùa Thu Phong Cách Pháp", "price": 290000,
     "image_url": "https://images.unsplash.com/photo-1510598969022-c4c6c5d05769?w=600&q=80",
     "category": "Phụ kiện", "is_new": False, "is_on_sale": False,
     "description": "Mũ beret len mềm phong cách Pháp classic, dễ phối với mọi trang phục."},
    {"name": "Clutch Da Tối Giản Evening", "price": 650000,
     "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&q=80",
     "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
     "description": "Ví clutch da tối giản cho buổi tối, phù hợp dự tiệc hoặc dinner."},
]


def add_products():
    with app.app_context():
        # Build category map
        cats = {c.name: c.id for c in Category.query.all()}
        if not cats:
            print("[ERROR] Không tìm thấy danh mục. Chạy seed.py trước!")
            return

        count = 0
        for p in EXTRA_PRODUCTS:
            cat_id = cats.get(p["category"])
            if not cat_id:
                print(f"  [SKIP] Không tìm thấy danh mục: {p['category']}")
                continue
            # Check if product already exists
            existing = Product.query.filter_by(name=p["name"]).first()
            if existing:
                print(f"  [EXISTS] {p['name']}")
                continue
            product = Product(
                name=p["name"],
                description=p.get("description", ""),
                price=p["price"],
                old_price=p.get("old_price"),
                image_url=p["image_url"],
                category_id=cat_id,
                is_new=p.get("is_new", False),
                is_on_sale=p.get("is_on_sale", False),
                stock=100,
            )
            db.session.add(product)
            count += 1
            print(f"  [ADD] {p['name']}")

        db.session.commit()
        total = Product.query.count()
        print(f"\n✅ Đã thêm {count} sản phẩm mới. Tổng DB: {total} sản phẩm.")


if __name__ == "__main__":
    add_products()
