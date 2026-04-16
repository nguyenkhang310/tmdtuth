// Mock Product Data
const products = [
    {
        id: "p1",
        name: "Váy Linen Academia",
        price: 850000,
        originalPrice: 1200000,
        category: "vay",
        categories: ["vay", "dam"],
        colors: ["#000000", "#F5F5DC"],
        sizes: ["S", "M", "L"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuC_86-laMZEGLhZLlKY28QLRVfoug7TGXd_PRUcwRy1QAZ9cJWbISfv5T5i8P3Kd_0cVZzkHa3fjzBvNLl3c-ncBYPf1Okab5wPzM7UjkJ575Bd6ishv-UVg81VMQjdOTHo9ZLYpMAG2Pgu25FE5viND-WZbkfkrSoOnZR09X0_DbJvM_s5ZH2IikWmuYY7jvwJDlid33RW9Hx6IW3gnl_4ouS8iKyzToJdwFmNw0bzLEBzFfk-_8QW4w7OShp-55OePyeSY3FTo20",
        isNew: true,
        isSale: true
    },
    {
        id: "p2",
        name: "Áo Sơ Mi Silk-Cotton",
        price: 590000,
        originalPrice: 750000,
        category: "ao-so-mi",
        categories: ["ao", "ao-so-mi"],
        colors: ["#FFFFFF", "#87CEEB"],
        sizes: ["S", "M", "L", "XL"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuANF5I9wW9peX3RtDcyBU9dy-9broZyCt1mcymvk_VFxIBy1naRRmfv9fwiqQ6fLXR8Ci_giFJFTdqJsCpe72M1iUSf3hTIeVdhHoLycBSFIq1CysbZ7FBNAh_0CzOJG5fMqoJZ9tTyfLY49RYF2hvhgshzlxLGtCUuw3QUHy-DxXUYWEvrVvo5uwGTf6WwqJd1F0kE1YwBszF9bMMr5qRjAKfgoTDvm-R5rsP76rzsPSMINbXop-IxiJyZaMxS-wz_-eF1HyrQ240",
        isNew: true,
        isSale: true
    },
    {
        id: "p3",
        name: "Set Đầm Blazer Midnight",
        price: 1450000,
        originalPrice: 2100000,
        category: "dam",
        categories: ["dam"],
        colors: ["#000000"],
        sizes: ["S", "M"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuB30lpYL9v4DfLER7fmViDuy_8rPYF0SbO2_zHmqajTT92TuuHMRS12-fdi5WxDNJ0WlfFFkDFsbxthtGCtsOCYlaCXcjVsSErjzA28kHnQCAL65HCpEb4uoxfCByAscaDQzIsMOVbZcTFzd8N3NSlAys5oUrmLfoH70osr6T-6etbT-a_JD1XskWuG4azF5ng-IT6MKeugqZrZG4Z09Si0FYk3evbqm9dkHzqa7EzkIUWkyx5pswUW7YwRIyMlNpKpC4Zh_geGyks",
        isSale: true,
        discountLabel: "-30%"
    },
    {
        id: "p4",
        name: "Quần Wide-Leg Canvas",
        price: 720000,
        originalPrice: 950000,
        category: "quan",
        categories: ["quan", "quan-jean"],
        colors: ["#A9A9A9", "#000000", "#FFFFFF"],
        sizes: ["26", "27", "28", "29"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuACCRF99t4rtMb46_jUi2a6_LWGdHIw7CfkOjhSV2MFpeSgjfvTK_riR8Y83jKiump_fP6ZCJ9t_HGbnQ3pp5XpzQHKgSLnSND066Nzf2YkhFeA-z1iXj3rXKRKMPvqOHb13AV_DQB1Kxj8Fy9wzxmEyf1AScNNDPyCSLBwVT31UBSBgFyMEUNMjb-NzR1dCXdFS4P7zyz2N4OMoIm9Huq_cjAMztfNqdNI3n7yeE5Nl_dU5HjtjxKnNBQzjPMCq8LqtVWLLfx075Q"
    },
    {
        id: "p5",
        name: "Outfit Urban Elite",
        price: 2150000,
        originalPrice: null,
        category: "ao",
        categories: ["ao", "quan"],
        colors: ["#333333"],
        sizes: ["S", "M", "L"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDTmiYzTxE__Y5gZitggiHTj9-zSPmgFKPiZ73YkcQRZTAXQCfvVrtx2v9EsdqCbQUGcW-jh4N9TCByeBn8nUJ-bW89LavP971DwsYqcpDLdJWX3cRG6cdB921PtTDniJ6_oI_0Cdx9JL4Fz6PeKFTpeIJVQyyCwtUizuqhLpIHvKRedek8wT6Hl-_1o8Gi96heENkThT3KcncdslCTUv7xirZ7jRnpfPUDEU_jND3W_4TcGJXBs80Rkw-4F6bfO9cNdINDvvIBvK0",
        isBestSeller: true
    },
    {
        id: "p6",
        name: "Bộ Sét Minimalist Beige",
        price: 1890000,
        originalPrice: null,
        category: "dam",
        categories: ["dam", "vay"],
        colors: ["#F5F5DC"],
        sizes: ["S", "M", "L"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuC1ivArpvUEzfXrdR2-S8cLL5Rlg1-2I4ZfdKR9zObkbGopl6QBld_4nCwsJEyPhuiofyg90o0MRR4PEtBXEC9ptXC4xb3k17YdCmWKnFVgSEmQMC3KI4wCbAQeBO0Ohk4LojzquzQK-BDUy-L3wLYN0hMwAGrkB3pOCgztCIrHOLFCGowoS29CXhC_UqT25QKD6IJiepFjUrtbzOlLBlLZgDg8D_fHswbSN7y65ofKvdyXkHEca65y0HgHaLtIRI7sMdsi2OldGlQ",
        isBestSeller: true
    },
    {
        id: "p7",
        name: "Phụ Kiện Artisan Silver",
        price: 450000,
        originalPrice: null,
        category: "phu-kien",
        categories: ["phu-kien"],
        colors: ["#C0C0C0"],
        sizes: ["Free Size"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCdLn6xFkm7TMnXOfUf9WmIFgprrwTQLrREiqHCPda3LrTawPHnXvu2Iqie0n-SfHSNqG8z87s-UV1ecdol7HskIpxssoVRpZmcks1CG0dbNZf918ElOljxbp1sO1rGKRIZLQz7Im_4M4Giq3r2YNZ2IIe-Zz83x5U-2Bs6PkQFPNSaEaeEfLIjOSgLgemT72UCs3W91IWZgX3BSTX_zHK89M-QlMKHk98GXVDhJrpSPgIevfeYVhzU9FpFiv8PbRRwNCE98En73hc",
        isBestSeller: true
    },
    {
        id: "p8",
        name: "Váy Xếp Ly Modernist",
        price: 1250000,
        originalPrice: null,
        category: "vay",
        categories: ["vay"],
        colors: ["#000000", "#FFC0CB"],
        sizes: ["S", "M", "L"],
        image: "https://lh3.googleusercontent.com/aida-public/AB6AXuB5cQlbuFnEWo7iyll8qW0f4eWie3IrODdZQL1yPtkbDteCKnu6okIKJQ0Xnt0riFJlIYYyfZbQqhN7RPHpVfU65b2q4OmRuBuDwUt6VMMyx35wxqBgO0k4PIuMTmddPA4ph1eRlYNGOC5i8Zqz_fuaxicVobCLdoyFQckeVgZYjHKKFvNkGEGfTYiWGW6mcNk7ptLRFZiCUpV4bsYL5nnUeO_2BNWd11WWuBhxlpgzYY0o_tIyMgkEUJt_iTedSw_45Jfmk8CTuJ8",
        isBestSeller: true
    }
];

// Helper Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}
