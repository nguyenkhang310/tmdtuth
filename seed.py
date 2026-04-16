import os
from werkzeug.security import generate_password_hash
from app import app
from extensions import db
from models import User, Category, Product

PRODUCTS = [
    # ======= ÁO =======
    {
        "name": "Áo Sơ Mi Silk-Cotton Premium",
        "description": (
            "Được dệt từ chất liệu silk-cotton cao cấp tỷ lệ 60/40, áo sơ mi này mang đến cảm giác mềm mại, "
            "nhẹ nhàng và cực kỳ thoáng mát trong suốt ngày dài. Thiết kế cổ bẻ cổ điển kết hợp với đường may "
            "tinh xảo tạo nên vẻ ngoài chỉn chu, phù hợp cho cả môi trường học thuật lẫn công sở. Phần vải co "
            "giãn nhẹ giúp tôn dáng và không bó sát khó chịu. Có các màu: trắng ngà, xanh nhạt, hồng pastel."
        ),
        "price": 590000, "old_price": 750000,
        "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Áo Khoác Blazer Elite Tweed",
        "description": (
            "Blazer cao cấp được may từ chất liệu tweed nhập khẩu, kết hợp sợi len và polyester bền đẹp. "
            "Đường cắt may slim-fit tôn lên vóc dáng thanh mảnh và chuyên nghiệp. Lớp lót bên trong mềm mịn "
            "giúp mặc thoải mái cả ngày. Hai túi hộp phía trước và một túi ngực tiện dụng. Phù hợp mặc cùng "
            "chân váy, quần tây hoặc quần jeans để tạo phong cách business-casual hoàn hảo."
        ),
        "price": 1250000, "old_price": 1800000,
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&q=80",
        "category": "Áo", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Áo Len Crop Cashmere Blend",
        "description": (
            "Áo len croptop được dệt từ hỗn hợp cashmere 30% và len merino 70%, mềm mịn như nhung và giữ ấm "
            "vượt trội trong những ngày trời lạnh. Thiết kế cổ tròn đơn giản nhưng tinh tế, phần tay dài vừa "
            "đủ để gấp lên tạo điểm nhấn. Form crop tôn eo, dễ phối cùng quần high-waist hoặc váy midi. "
            "Màu sắc đa dạng: kem, beige, caramel, navy, burgundy."
        ),
        "price": 720000,
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Áo Phông Oversize Organic Cotton",
        "description": (
            "Làm từ 100% cotton hữu cơ được chứng nhận GOTS, áo phông oversize này thân thiện với môi trường "
            "và cực kỳ thoải mái để mặc hàng ngày. Trọng lượng vải 220g/m² cho cảm giác dày dặn nhưng không "
            "nóng bức. Form oversize boxy mang lại vẻ ngoài trendy, cool ngầu. In nổi logo UTH Store nhỏ ở "
            "ngực trái. Có 10 màu từ trơn basic đến pastel nhẹ nhàng."
        ),
        "price": 320000, "old_price": 420000,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Áo Croptop Ren Vintage Lace",
        "description": (
            "Áo croptop được làm từ chất liệu ren cổ điển nhập từ Ý, mỏng nhẹ và tinh tế. Phần ren được xử "
            "lý đặc biệt để chống xổ và giữ form tốt theo thời gian. Thiết kế cổ vuông nữ tính kết hợp tay "
            "phồng nhẹ tạo điểm nhấn lãng mạn. Phù hợp mặc kèm quần tây high-waist hoặc váy xòe để tạo "
            "phong cách vintage-chic cuốn hút. Màu trắng kem và đen."
        ),
        "price": 450000,
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Áo Cardigan Knit Dày Dặn",
        "description": (
            "Cardigan dệt kim dày dặn với đường đan chunky nổi bật — xu hướng hot nhất Thu Đông 2026. "
            "Chất liệu acrylic cao cấp không xù, không ra màu sau nhiều lần giặt. Form dáng rộng oversized "
            "thoải mái, dễ mặc layering. Hai túi lớn ở hai bên thêm tính tiện dụng. Đây là chiếc áo đa năng "
            "có thể mặc như một lớp áo ngoài hoặc thay cho jacket trong ngày se lạnh."
        ),
        "price": 580000, "old_price": 720000,
        "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&q=80",
        "category": "Áo", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Áo Polo Classic Piqué",
        "description": (
            "Áo polo cổ điển được làm từ vải piqué cotton 100% thoáng khí và nhẹ mát. Cổ polo 2 nút tinh "
            "tế, phần gấu áo và tay áo viền sườn chắc chắn không bị cong sau khi giặt. Màu sắc trơn trang "
            "nhã phù hợp cho nhiều dịp: học tập, đi chơi, thể thao nhẹ. Size từ XS đến XXL. Một item "
            "không thể thiếu trong tủ đồ của người yêu thích phong cách preppy-clean."
        ),
        "price": 380000,
        "image_url": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=600&q=80",
        "category": "Áo", "is_new": False, "is_on_sale": False,
    },

    # ======= QUẦN =======
    {
        "name": "Quần Tây Slim Fit Wool Blend",
        "description": (
            "Quần tây slim fit được may từ chất liệu wool blend cao cấp — hỗn hợp len 45% và polyester 55% "
            "cho độ bền vượt trội và ít nhăn. Đường may chắc chắn, cạp quần có dây đai vải và khóa kéo ẩn "
            "tinh tế. Form slim vừa vặn tôn dáng mà không bó sát gây khó chịu. Phù hợp mặc với áo sơ mi, "
            "blazer hoặc áo len. Màu sắc: đen, xám than, xanh navy, be."
        ),
        "price": 680000, "old_price": 900000,
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Quần Jean Slim Wash Dark",
        "description": (
            "Quần jean slim với màu wash tối đặc trưng — chắc chắn, bền bỉ nhưng vẫn cực kỳ thời thượng. "
            "Chất denim 12oz co giãn 2% spandex cho sự thoải mái khi di chuyển. Đường may contrast nổi bật, "
            "5 túi tiêu chuẩn. Wash đặc biệt giúp màu ổn định sau nhiều lần giặt. Phù hợp phối cùng áo phông "
            "oversize, áo sơ mi hoặc blazer để tạo nhiều style khác nhau. Kích thước: 26-34."
        ),
        "price": 750000, "old_price": 950000,
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80",
        "category": "Quần", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Quần Culottes Linen Trắng",
        "description": (
            "Quần culottes ống rộng được làm từ 100% linen tự nhiên — thoáng mát, thấm hút tốt, lý tưởng "
            "cho khí hậu nhiệt đới Việt Nam. Chiều dài đến bắp chân tạo vẻ thanh lịch và hiện đại. Cạp "
            "chun sau thoải mái, dễ mặc cả ngày. Màu trắng tinh khôi giúp dễ phối đồ. Một item must-have "
            "trong tủ đồ hè, dễ phối từ casual đến smart-casual."
        ),
        "price": 490000,
        "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4851b2?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Quần Short Bermuda Kẻ Caro",
        "description": (
            "Quần short Bermuda dài đến gối với họa tiết kẻ caro classic — vừa năng động vừa thanh lịch. "
            "Chất liệu cotton twill dày dặn 240g, không nhăn và giữ form tốt. 4 túi thực dụng (2 trước + "
            "2 sau). Thiết kế cạp vải, thắt lưng giả giúp trông gọn gàng. Phù hợp mặc đi học, đi chơi "
            "hoặc thể thao nhẹ. Màu: kẻ đỏ-trắng, kẻ xanh-trắng, kẻ đen-trắng."
        ),
        "price": 350000, "old_price": 450000,
        "image_url": "https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=600&q=80",
        "category": "Quần", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Quần Jogger Kaki Premium",
        "description": (
            "Quần jogger kaki cao cấp — sự kết hợp hoàn hảo giữa thoải mái và phong cách. Chất liệu cotton "
            "kaki 260g mềm mại, bền chắc và kháng bụi bẩn tốt. Phần cạp và gấu ống co giãn giúp vận động "
            "tự do. Túi bên có khóa kéo an toàn cho đồ dùng cá nhân. Phù hợp cho lifestyle năng động: đi "
            "học, café, mua sắm hay dạo phố cuối tuần. Màu: beige, olive, xám, đen."
        ),
        "price": 420000,
        "image_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Quần Palazzo Wide Leg Nhung",
        "description": (
            "Quần palazzo ống rộng chất nhung mịn — item sang chảnh nhất mùa Thu Đông năm nay. Vải nhung "
            "dập hoa tinh xảo tạo hiệu ứng ánh sáng lung linh khi di chuyển. Cạp cao tôn eo, ống quần "
            "rộng che khéo phần đùi. Phối cùng áo croptop hoặc áo tucked-in để tạo tỉ lệ hoàn hảo. "
            "Phù hợp đi tiệc, sự kiện hoặc thậm chí cà phê cuối tuần. Màu: đen, tím mận, xanh navy."
        ),
        "price": 620000, "old_price": 800000,
        "image_url": "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=600&q=80",
        "category": "Quần", "is_new": False, "is_on_sale": True,
    },

    # ======= VÁY =======
    {
        "name": "Váy Linen Academia Xanh Rêu",
        "description": (
            "Chiếc váy linen cao cấp với màu xanh rêu trầm mặc — biểu tượng của phong cách Dark Academia "
            "đang cực hot trên toàn thế giới. Chất linen 100% tự nhiên cực kỳ thoáng mát và nhẹ nhàng. "
            "Form dáng A-line thanh lịch, dài qua gối, phù hợp mọi vóc dáng. Hai túi bên rộng thực dụng. "
            "Phối cùng áo sơ mi trắng, blazer và giày oxford để hoàn thiện look học thuật chuẩn chỉnh."
        ),
        "price": 850000, "old_price": 1200000,
        "image_url": "https://images.unsplash.com/photo-1566479179817-0b6491e1e4da?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Set Đầm Blazer Midnight Blue",
        "description": (
            "Bộ set đầm kết hợp blazer sang trọng màu midnight blue — sự lựa chọn hoàn hảo cho những dịp "
            "cần tạo ấn tượng mạnh. Blazer được may từ chất liệu polyester cao cấp với lớp lót mềm mịn. "
            "Đầm ôm dáng đi kèm có chiều dài midi thanh lịch. Hai món có thể mặc rời để tạo nhiều outfit "
            "khác nhau. Phù hợp phỏng vấn, thuyết trình, sự kiện hoặc tiệc công ty. Size XS-XL."
        ),
        "price": 1450000, "old_price": 2100000,
        "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&q=80",
        "category": "Váy", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Váy Xếp Ly Midi Plissé",
        "description": (
            "Váy xếp ly theo kỹ thuật plissé châu Âu — mỗi nếp gấp được dập cố định vĩnh viễn để giữ "
            "form suốt vòng đời sản phẩm. Chất liệu satin poly ánh nhẹ tạo vẻ đẹp nữ tính và sang trọng. "
            "Chiều dài midi qua gối, cạp chun co dãn tiện lợi. Phối cùng áo croptop, áo len hoặc blazer "
            "đều đẹp. Màu sắc rực rỡ: hồng coral, tím lavender, xanh sage, vàng mù tạt."
        ),
        "price": 920000,
        "image_url": "https://images.unsplash.com/photo-1572804013427-4d7ca7268217?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Đầm Wrap Hoa Nhí Vintage",
        "description": (
            "Đầm wrap (quấn) với họa tiết hoa nhí vintage đầy nữ tính và duyên dáng. Chất liệu viscose "
            "mềm mại rũ nhẹ theo dáng, thấm hút mồ hôi tốt. Phần cổ V tự nhiên và eo thắt lại bằng dây "
            "buộc tạo tỉ lệ eo-hông hoàn hảo. Phù hợp đi học, đi chơi, dạo phố hay cafe cùng bạn bè. "
            "Dài qua gối, form A-line nhẹ nhàng, tôn dáng mọi vóc dáng."
        ),
        "price": 680000, "old_price": 890000,
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Váy Mini Trễ Vai Romantic",
        "description": (
            "Váy mini trễ vai với thiết kế đầy lãng mạn và nữ tính — item được tìm kiếm nhiều nhất mùa hè "
            "này. Chất liệu cotton poplin thoáng mát với phần thân váy cấu trúc nhẹ. Đường xếp bèo nhỏ "
            "ở ngực tạo độ nữ tính tinh tế. Chiều dài mini tôn chân dài. Phối giày bệt hoặc sandal đế "
            "bằng để ra phố, thêm blazer để lên đồ công sở."
        ),
        "price": 540000,
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Váy Maxi Boho Tassels",
        "description": (
            "Váy maxi boho với chi tiết tassels (tua rua) thủ công — mỗi chiếc tua rua được đính tay tỉ "
            "mỉ. Chất liệu cotton muslin nhẹ và thoáng, phù hợp cho khí hậu nhiệt đới. Chiều dài maxi đến "
            "mắt cá chân tạo vẻ bay bổng, tự do. Cổ V sâu vừa phải nữ tính. Phối cùng sandal đế platform "
            "và túi rơm để hoàn thiện look resort/boho. Màu: trắng, be kem, terracotta."
        ),
        "price": 790000, "old_price": 1050000,
        "image_url": "https://images.unsplash.com/photo-1572804013310-6b0f3bb54694?w=600&q=80",
        "category": "Váy", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Váy Denim Button Front",
        "description": (
            "Váy denim button-front — item thời trang vượt thời gian, không bao giờ lỗi mốt. Chất denim "
            "11oz vừa đủ nặng để giữ form, vừa đủ nhẹ để mặc thoải mái. Hàng cúc giả phía trước trang "
            "trí tạo điểm nhấn. Hai túi bên rộng thực dụng. Phối cùng áo phông oversize, áo len gọn hoặc "
            "áo sơ mi. Màu: xanh nhạt, xanh đậm, đen. Size 26-34."
        ),
        "price": 620000,
        "image_url": "https://images.unsplash.com/photo-1582533561751-ef6f6ab93a2e?w=600&q=80",
        "category": "Váy", "is_new": False, "is_on_sale": False,
    },

    # ======= PHỤ KIỆN =======
    {
        "name": "Túi Tote Da Thật Premium",
        "description": (
            "Túi tote được làm từ da thật full-grain cao cấp nhất — loại da chỉ qua xử lý tối thiểu, giữ "
            "lại vẻ đẹp tự nhiên và càng dùng càng đẹp hơn theo thời gian (patina). Kích thước rộng 38cm "
            "x cao 32cm x sâu 15cm — đủ chứa laptop 15', sách, ví và đồ cá nhân. Dây đeo bằng da bền chắc. "
            "Khóa miệng bằng từ tính tiện lợi. Nội thất có 3 ngăn nhỏ và 1 ngăn khóa kéo. Màu: caramel, "
            "nâu đen, đen, xanh navy."
        ),
        "price": 1850000,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Túi Bucket Đan Lát Thủ Công",
        "description": (
            "Túi bucket được đan lát hoàn toàn bằng tay từ sợi cói tự nhiên — mỗi chiếc là một tác phẩm "
            "thủ công độc đáo. Kích thước vừa đủ để đựng đồ đi biển, đi cafe hay đi chơi cuối tuần. Phần "
            "miệng túi có khóa kéo và dây rút an toàn. Kèm theo túi vải nhỏ đựng ví và điện thoại bên "
            "trong. Bền đẹp với thời gian, càng dùng càng có độ patina tự nhiên đẹp."
        ),
        "price": 450000, "old_price": 580000,
        "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Mũ Bucket Corduroy Vintage",
        "description": (
            "Mũ bucket làm từ vải corduroy (nhung kẻ) — chất liệu đặc trưng của phong cách vintage và "
            "thời trang 90s đang cực hot comeback. Vành mũ rộng 5cm che nắng hiệu quả. Có dây điều chỉnh "
            "size bên trong phù hợp nhiều vòng đầu. Gấp nhỏ gọn khi du lịch. Màu sắc: caramel, xanh "
            "olive, đen, kem, đỏ burgundy. Phối cùng áo phông oversize và quần jean cho look street style."
        ),
        "price": 280000,
        "image_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Thắt Lưng Da Bò Handcraft",
        "description": (
            "Thắt lưng được làm từ da bò full-grain dày 3.5mm, gia công thủ công từng đường kim mũi chỉ. "
            "Đường viền được đánh bóng và nhuộm màu thủ công tạo độ bóng đẹp. Khóa kim loại mạ đồng "
            "anti-rust bền đẹp. Chiều rộng 3.5cm phù hợp với hầu hết các loại quần có dây đai. Chiều "
            "dài từ 85-125cm, có nhiều bậc điều chỉnh. Kèm hộp quà sang trọng — lựa chọn quà tặng hoàn hảo."
        ),
        "price": 580000,
        "image_url": "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600&q=80",
        "category": "Phụ kiện", "is_new": False, "is_on_sale": False,
    },
    {
        "name": "Khăn Lụa Silk Print Họa Tiết",
        "description": (
            "Khăn lụa 100% silk với họa tiết in digital sắc nét, màu sắc rực rỡ không phai. Kích thước "
            "90x90cm đủ lớn để đội đầu, quàng cổ, buộc túi xách hay làm áo crop trong những ngày hè nóng. "
            "Chất lụa mềm mại, trơn nhẹ và có ánh sáng tự nhiên đẹp khi chụp ảnh. Họa tiết đa dạng: hoa "
            "lớn, geometric, animal print, abstract. Kèm hộp cứng bảo quản."
        ),
        "price": 420000, "old_price": 560000,
        "image_url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&q=80",
        "category": "Phụ kiện", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Dây Chuyền Layering Gold-Fill",
        "description": (
            "Bộ 3 dây chuyền layering mạ vàng 18k gold-fill — lớp mạ dày hơn gold-plated thông thường, "
            "không đen, không xỉn và bền màu theo thời gian. Chiều dài 3 sợi: 40cm, 45cm, 50cm tạo hiệu "
            "ứng layering hoàn hảo. Mặt dây khác nhau: hình tròn, chữ nhật và hình thoi. Phù hợp đeo với "
            "áo cổ V, cổ thuyền hay trễ vai. Chống dị ứng, phù hợp da nhạy cảm."
        ),
        "price": 350000,
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Kính Mát UV400 Vintage Round",
        "description": (
            "Kính mát gọng tròn vintage đặc trưng của phong cách retro-chic. Tròng kính chống tia UV400 "
            "100% bảo vệ mắt tối ưu. Gọng kim loại nhẹ chỉ 18g, không gây đau tai hay mũi khi đeo lâu. "
            "Mắt kính có màu khói nhẹ hoặc gradient cho hiệu ứng thẩm mỹ cao. Kèm túi da đựng kính và "
            "khăn lau. Gọng có thể điều chỉnh phù hợp nhiều khuôn mặt. Màu: vàng, bạc, đen."
        ),
        "price": 490000, "old_price": 650000,
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=80",
        "category": "Phụ kiện", "is_new": False, "is_on_sale": True,
    },
    {
        "name": "Mũ Beret Woolen Đan Tay",
        "description": (
            "Mũ beret đan tay từ len merino 100% — mềm mịn, không ngứa và giữ ấm xuất sắc. Đây là item "
            "xu hướng của mùa Thu Đông được ưa thích ở cả Việt Nam và thế giới. Kiểu đội linh hoạt: ngay "
            "ngắn, lệch một bên hay kéo xuống che tai. Phối với áo len, áo khoác hay thậm chí trench coat "
            "đều đẹp. Màu: đen, be, caramel, đỏ burgundy, xanh navy."
        ),
        "price": 320000,
        "image_url": "https://images.unsplash.com/photo-1510598969022-c4c6c5d05769?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Ví Da Dài Minimalist",
        "description": (
            "Ví da dài theo phong cách tối giản — chỉ giữ lại những gì cần thiết. Làm từ da PU cao cấp "
            "mềm mịn và bền đẹp. Bên trong có 12 khe đựng thẻ, 2 ngăn tiền lớn và 1 ngăn khóa kéo. "
            "Kích thước vừa vặn với các loại túi xách phổ biến. Độ dày chỉ 8mm khi không đựng thẻ. "
            "Có thể dùng như clutch cầm tay. Màu: đen, trắng, nude, caramel, xanh navy."
        ),
        "price": 380000, "old_price": 480000,
        "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&q=80",
        "category": "Phụ kiện", "is_new": False, "is_on_sale": True,
    },

    # ======= BỘ SƯU TẬP SPECIAL EDITION =======
    {
        "name": "Áo Hoodie UTH Campus Limited",
        "description": (
            "Áo hoodie limited in logo UTH Campus độc quyền, form unisex oversize cực chất. Vải nỉ bông "
            "320gsm dày dặn, bên trong lót lông mềm siêu ấm. Bo tay và gấu áo dệt rib chắc chắn, không bai "
            "sau nhiều lần giặt. Phù hợp đi học, đi chơi, mix cùng quần jean hay jogger đều đẹp."
        ),
        "price": 690000, "old_price": 850000,
        "image_url": "https://images.unsplash.com/photo-1543076447-215ad9ba6923?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Set Tracksuit Thể Thao Streetwear",
        "description": (
            "Set tracksuit áo khoác + quần thể thao phong cách streetwear, chất nỉ co giãn 4 chiều thoải "
            "mái vận động. Áo khoác có khóa kéo full zip, mũ trùm và túi kengroo; quần jogger bo gấu, có "
            "dây rút bản lớn. Phù hợp tập gym, chạy bộ hoặc đi chơi cuối tuần. Form unisex, dễ phối đồ."
        ),
        "price": 980000, "old_price": 1250000,
        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Đầm Satin Dự Tiệc Aurora",
        "description": (
            "Đầm satin dự tiệc với bề mặt bóng nhẹ sang trọng, phom dáng ôm nhẹ phần eo, xòe nhẹ phần chân "
            "tạo hiệu ứng uyển chuyển khi di chuyển. Dây áo mảnh có thể điều chỉnh, phần lưng khoét chữ V "
            "gợi cảm nhưng vẫn tinh tế. Thích hợp dự tiệc, prom, chụp kỷ yếu hoặc dạ hội."
        ),
        "price": 1350000, "old_price": 1790000,
        "image_url": "https://images.unsplash.com/photo-1514996937319-344454492b37?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Váy Babydoll Cotton Candy",
        "description": (
            "Váy babydoll cotton form rộng dễ thương, phù hợp mọi dáng người. Chất liệu cotton poplin "
            "thoáng mát, lên form phồng nhẹ tự nhiên. Tầng váy xếp babydoll tạo độ bồng đáng yêu, cổ vuông "
            "nữ tính, tay phồng nhẹ. Item hoàn hảo cho những buổi picnic, dạo phố hay đi học."
        ),
        "price": 520000,
        "image_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600&q=80",
        "category": "Váy", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Quần Cargo Utility Multi-Pocket",
        "description": (
            "Quần cargo utility đa túi đúng chất Y2K, chất vải kaki dày dặn nhưng vẫn mềm mại. 6 túi hộp "
            "được bố trí cân đối ở hai bên đùi và hông, vừa thời trang vừa thực dụng. Cạp có dây rút và "
            "đai đính kèm, ống có thể rút gọn bằng dây kéo. Phù hợp phong cách streetwear, hiphop."
        ),
        "price": 640000, "old_price": 790000,
        "image_url": "https://images.unsplash.com/photo-1542272605-15d6c8f2dd9f?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Quần Jean Wide Leg Ultra High-Waist",
        "description": (
            "Quần jean ống rộng cạp siêu cao, giúp hack chân dài tối đa. Chất denim 13oz đứng form, wash "
            "nhạt vintage cực trend. Đường may contrast màu vàng camel, cạp có 2 nút tạo điểm nhấn. "
            "Phối cùng áo croptop hoặc áo sơ mi đóng thùng đều đẹp."
        ),
        "price": 820000,
        "image_url": "https://images.unsplash.com/photo-1555685812-4b943f1cb0eb?w=600&q=80",
        "category": "Quần", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Áo Sơ Mi Lụa Classic Office",
        "description": (
            "Áo sơ mi lụa mềm rũ, phù hợp môi trường văn phòng chỉn chu. Bề mặt lụa mờ, ít nhăn, màu sắc "
            "trung tính dễ phối như trắng, kem, nude, xanh pastel. Cổ đức nhỏ gọn, hàng cúc ẩn giúp tổng "
            "thể tối giản nhưng vẫn sang trọng."
        ),
        "price": 610000,
        "image_url": "https://images.unsplash.com/photo-1540411025311-95e2dd7565ce?w=600&q=80",
        "category": "Áo", "is_new": False, "is_on_sale": False,
    },
    {
        "name": "Áo Thun Graphic Artwork UTH Studio",
        "description": (
            "Áo thun in graphic artwork do UTH Studio thiết kế độc quyền. Vải cotton 230gsm dày dặn, "
            "in lụa cao cấp không nứt, không bong tróc. Form boxy trẻ trung, cổ bo gân chắc chắn. "
            "Phù hợp cho các bạn yêu thích phong cách street art và local brand."
        ),
        "price": 390000, "old_price": 450000,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80",
        "category": "Áo", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Sneaker Low-top Everyday Comfort",
        "description": (
            "Sneaker low-top classic với đế cao su đúc nguyên khối chống trơn trượt. Thân giày bằng canvas "
            "phối da tổng hợp, lót trong bằng vải mesh thoáng khí. Đế lót memory foam êm chân, đi bộ cả "
            "ngày không mỏi. Màu: trắng, đen, beige, xanh navy."
        ),
        "price": 890000, "old_price": 1090000,
        "image_url": "https://images.unsplash.com/photo-1514986888952-8cd320577b68?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": True,
    },
    {
        "name": "Giày Loafer Da Mũi Vuông",
        "description": (
            "Giày loafer da mũi vuông hiện đại, hợp trend office-chic. Thân giày làm từ da bò thật xử lý "
            "mờ sang trọng, lót trong da mềm chống phồng rộp. Gót 3cm giúp tôn dáng nhưng vẫn dễ đi. "
            "Phối đẹp với váy midi, quần tây hay jean ống đứng."
        ),
        "price": 1250000,
        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
    {
        "name": "Balô Laptop Urban Tech",
        "description": (
            "Balô laptop phong cách urban-tech với nhiều ngăn chức năng: ngăn laptop 15.6', ngăn tablet, "
            "ngăn phụ cho sạc dự phòng, chuột, sổ tay. Chất vải polyester chống nước nhẹ, đệm lưng 3D "
            "thoáng khí. Cổng sạc USB tích hợp, dây đeo êm vai. Phù hợp cho sinh viên và dân văn phòng."
        ),
        "price": 990000,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80",
        "category": "Phụ kiện", "is_new": True, "is_on_sale": False,
    },
]


def seed_data():
    with app.app_context():
        db.create_all()

        # Users
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@uthstore.com',
                password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(
                username='user',
                email='user@uthstore.com',
                password_hash=generate_password_hash('user123', method='pbkdf2:sha256'),
                role='user'
            )
            db.session.add(user)

        # Categories
        if Category.query.count() == 0:
            cat_map = {}
            for cat_name in ['Áo', 'Quần', 'Váy', 'Phụ kiện']:
                cat = Category(name=cat_name)
                db.session.add(cat)
                db.session.flush()
                cat_map[cat_name] = cat.id

            # Add all products
            for p in PRODUCTS:
                product = Product(
                    name=p['name'],
                    description=p['description'],
                    price=p['price'],
                    old_price=p.get('old_price'),
                    image_url=p['image_url'],
                    category_id=cat_map[p['category']],
                    is_new=p.get('is_new', False),
                    is_on_sale=p.get('is_on_sale', False),
                )
                db.session.add(product)

        db.session.commit()
        total = Product.query.count()
        print(f"[OK] Database seeded! {total} san pham da duoc them vao.")


if __name__ == '__main__':
    seed_data()
