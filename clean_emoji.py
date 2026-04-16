import re

# Map emoji -> replacement (material icon span or clean text)
def icon(name):
    return f'<span class="material-symbols-outlined" style="font-size:1.1rem">{name}</span>'

replacements = {
    # base.html nav
    '🔥 Sale': 'Sale',
    '🔥 Xem Sale': 'Xem khuyến mãi',
    # marquee
    '✦': '—',
    # hero
    '✨ ': '',
    # index categories
    '👕': icon('checkroom'),
    '👖': icon('straighten'),
    '👗': icon('styler'),
    '👜': icon('local_mall'),
    '🔥': icon('local_fire_department'),
    '🆕': icon('new_releases'),
    # features strip
    '🚚': icon('local_shipping'),
    '🔄': icon('autorenew'),
    '🛡️': icon('shield'),
    '💎': icon('diamond'),
    # cart
    '🛒': '',
    '🛒 ': '',
    ' 🛒': '',
    '💳': '',
    '🏦': '',
    '💵': '',
    '📱': '',
    # contact
    '📍': icon('location_on'),
    '📞': icon('phone'),
    '✉️': icon('email'),
    '⏰': icon('schedule'),
    # policy
    '🔒': icon('lock'),
    # admin stats
    '📦': icon('inventory_2'),
    '👥': icon('group'),
    '💰': icon('payments'),
    # admin nav / headings
    '➕ ': '',
    '✉️ ': '',
    '📦 ': '',
    # general star/check
    # cart empty
    '🔍': icon('search'),
    # footer contacts
}

import os

templates = [
    'templates/base.html',
    'templates/index.html',
    'templates/products.html',
    'templates/product-detail.html',
    'templates/cart.html',
    'templates/contact.html',
    'templates/policy.html',
    'templates/admin.html',
    'templates/login.html',
]

for filepath in templates:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Cleaned: {filepath}')
    else:
        print(f'No change: {filepath}')

print('Done!')
