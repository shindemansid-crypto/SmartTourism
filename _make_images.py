"""Generate labelled local SVG illustrations so every card has a matching image."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "static" / "images"
OUT.mkdir(parents=True, exist_ok=True)


def svg_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def poster(filename, title, subtitle, sky, land, accent, motif="monument"):
    t = svg_escape(title)
    s = svg_escape(subtitle)
    art = MOTIFS[motif]
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{sky}"/>
      <stop offset="1" stop-color="{land}"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#sky)"/>
  <circle cx="640" cy="90" r="48" fill="#F6E7B4" opacity=".85"/>
  {art}
  <rect y="390" width="800" height="110" fill="#0F2B23" opacity=".78"/>
  <text x="40" y="438" fill="#F7F1E6" font-family="Georgia, serif" font-size="32">{t}</text>
  <text x="40" y="472" fill="#C9A227" font-family="Segoe UI, Arial, sans-serif" font-size="16">{s}</text>
  <rect x="40" y="482" width="72" height="4" fill="{accent}"/>
</svg>'''
    (OUT / filename).write_text(content, encoding="utf-8")


MOTIFS = {
    "monument": '''
      <path d="M120 390 L220 250 L320 390Z" fill="#F4E4C1" opacity=".9"/>
      <rect x="210" y="270" width="20" height="120" fill="#E8D4A8"/>
      <ellipse cx="220" cy="250" rx="38" ry="22" fill="#FFF8E7"/>
      <rect x="360" y="300" width="220" height="90" fill="#D9C4A0"/>
      <rect x="380" y="320" width="36" height="50" fill="#3B2A1E" opacity=".55"/>
      <rect x="450" y="320" width="36" height="50" fill="#3B2A1E" opacity=".55"/>
      <rect x="520" y="320" width="36" height="50" fill="#3B2A1E" opacity=".55"/>''',
    "fort": '''
      <rect x="90" y="230" width="520" height="160" fill="#C45C26"/>
      <rect x="90" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="160" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="230" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="300" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="370" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="440" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="510" y="200" width="40" height="40" fill="#A24A1C"/>
      <rect x="570" y="200" width="40" height="40" fill="#A24A1C"/>
      <path d="M300 390 V300 A50 50 0 0 1 400 300 V390Z" fill="#3B2A1E"/>''',
    "beach": '''
      <path d="M0 280 Q200 220 400 270 T800 250 V390 H0Z" fill="#1F6B8A"/>
      <path d="M0 330 Q180 290 380 340 T800 310 V390 H0Z" fill="#2E8A9A"/>
      <path d="M0 370 Q220 340 420 375 T800 360 V390 H0Z" fill="#E8C99A"/>
      <rect x="90" y="250" width="14" height="130" fill="#6B4423"/>
      <ellipse cx="97" cy="240" rx="70" ry="28" fill="#1F6B4A"/>''',
    "hill": '''
      <path d="M0 390 L180 170 L340 390Z" fill="#1F6B4A"/>
      <path d="M220 390 L420 90 L640 390Z" fill="#2E7D57"/>
      <path d="M480 390 L680 180 L800 390Z" fill="#145C3A"/>
      <path d="M380 140 L420 90 L460 140" fill="#F7F1E6" opacity=".7"/>''',
    "temple": '''
      <rect x="250" y="250" width="300" height="140" fill="#E8C36A"/>
      <path d="M220 250 H580 L400 90 Z" fill="#C9A227"/>
      <rect x="370" y="300" width="60" height="90" fill="#5C3B1E"/>
      <circle cx="400" cy="96" r="14" fill="#F6E7B4"/>
      <rect x="140" y="310" width="90" height="80" fill="#D4AF37" opacity=".85"/>
      <rect x="570" y="310" width="90" height="80" fill="#D4AF37" opacity=".85"/>''',
    "lake": '''
      <path d="M0 250 Q200 180 400 240 T800 220 V390 H0Z" fill="#1F6B8A"/>
      <ellipse cx="400" cy="300" rx="260" ry="50" fill="#3AA0B5" opacity=".7"/>
      <path d="M80 250 L160 160 L240 250Z" fill="#1F6B4A"/>
      <rect x="500" y="230" width="90" height="40" fill="#F4E4C1"/>
      <path d="M490 230 H600 L545 190 Z" fill="#C45C26"/>''',
    "cave": '''
      <path d="M60 390 L200 140 L360 390Z" fill="#6B5344"/>
      <path d="M280 390 L480 90 L700 390Z" fill="#8A6A55"/>
      <ellipse cx="400" cy="330" rx="70" ry="90" fill="#2B1D16"/>
      <rect x="120" y="300" width="18" height="90" fill="#C9A227" opacity=".4"/>
      <rect x="160" y="280" width="18" height="110" fill="#C9A227" opacity=".4"/>''',
    "palace": '''
      <rect x="160" y="210" width="480" height="180" fill="#E8D5A3"/>
      <rect x="200" y="150" width="70" height="60" fill="#C45C26"/>
      <rect x="365" y="110" width="70" height="100" fill="#C45C26"/>
      <rect x="530" y="150" width="70" height="60" fill="#C45C26"/>
      <path d="M190 150 H280 L235 100 Z" fill="#8F1D1D"/>
      <path d="M355 110 H445 L400 55 Z" fill="#8F1D1D"/>
      <path d="M520 150 H610 L565 100 Z" fill="#8F1D1D"/>
      <rect x="250" y="260" width="40" height="70" fill="#3B2A1E"/>
      <rect x="380" y="250" width="40" height="80" fill="#3B2A1E"/>
      <rect x="510" y="260" width="40" height="70" fill="#3B2A1E"/>''',
    "food": '''
      <ellipse cx="400" cy="310" rx="210" ry="50" fill="#F4E4C1"/>
      <ellipse cx="400" cy="280" rx="160" ry="70" fill="#C45C26"/>
      <ellipse cx="400" cy="250" rx="110" ry="40" fill="#E8C36A"/>
      <circle cx="250" cy="240" r="34" fill="#1F6B4A"/>
      <circle cx="560" cy="250" r="28" fill="#8F1D1D"/>''',
    "craft": '''
      <rect x="220" y="160" width="360" height="200" fill="#C45C26"/>
      <rect x="250" y="190" width="300" height="140" fill="#F4E4C1"/>
      <path d="M280 260 Q400 180 520 260 Q400 340 280 260Z" fill="#1F6B4A"/>
      <circle cx="400" cy="260" r="28" fill="#C9A227"/>''',
    "festival": '''
      <circle cx="400" cy="220" r="90" fill="#E8C36A"/>
      <circle cx="400" cy="220" r="55" fill="#C45C26"/>
      <rect x="120" y="300" width="70" height="90" fill="#1F6B4A"/>
      <rect x="220" y="270" width="70" height="120" fill="#8F1D1D"/>
      <rect x="510" y="270" width="70" height="120" fill="#1F6B4A"/>
      <rect x="610" y="300" width="70" height="90" fill="#C9A227"/>''',
    "dance": '''
      <circle cx="400" cy="140" r="36" fill="#F4E4C1"/>
      <rect x="372" y="176" width="56" height="120" fill="#C45C26"/>
      <path d="M280 220 Q400 280 520 220" fill="none" stroke="#C9A227" stroke-width="18"/>
      <path d="M360 300 L320 390 L400 330 L480 390 L440 300Z" fill="#1F6B4A"/>''',
    "business": '''
      <rect x="180" y="180" width="440" height="210" fill="#E8D5A3"/>
      <rect x="180" y="150" width="440" height="40" fill="#1F6B4A"/>
      <rect x="240" y="230" width="80" height="90" fill="#5C3B1E"/>
      <rect x="360" y="220" width="80" height="100" fill="#C45C26"/>
      <rect x="480" y="230" width="80" height="90" fill="#5C3B1E"/>''',
    "city": '''
      <rect x="80" y="210" width="90" height="180" fill="#6B8F71"/>
      <rect x="190" y="160" width="110" height="230" fill="#1F6B4A"/>
      <rect x="320" y="190" width="90" height="200" fill="#C45C26"/>
      <rect x="430" y="140" width="120" height="250" fill="#0F3D2E"/>
      <rect x="570" y="220" width="100" height="170" fill="#8A6A55"/>
      <rect x="210" y="190" width="18" height="28" fill="#F6E7B4"/>
      <rect x="250" y="190" width="18" height="28" fill="#F6E7B4"/>''',
}


ITEMS = [
    ("login-bg.svg", "Incredible India", "Discover culture beyond the ordinary", "#1B3A4B", "#0F2B23", "#C9A227", "monument"),
    ("hero.svg", "Discover Incredible India", "Heritage, hills, coasts and culture", "#E39B6A", "#1F4D3A", "#C9A227", "monument"),
    ("fallback.svg", "Smart Tourism", "Image coming soon", "#4A5D52", "#1F2A26", "#C9A227", "city"),
    ("dest-mumbai.svg", "Mumbai", "Maharashtra", "#4B6B8A", "#1F2A40", "#C9A227", "city"),
    ("dest-pune.svg", "Pune", "Maharashtra", "#6B8F71", "#173D32", "#C45C26", "fort"),
    ("dest-sambhajinagar.svg", "Chhatrapati Sambhajinagar", "Maharashtra", "#C9A66B", "#6B4423", "#C9A227", "cave"),
    ("dest-lonavala.svg", "Lonavala", "Maharashtra", "#7BB3C9", "#1F4D3A", "#C9A227", "hill"),
    ("dest-mahableshwar.svg", "Mahabaleshwar", "Maharashtra", "#88B04B", "#145C3A", "#C9A227", "hill"),
    ("dest-delhi.svg", "Delhi", "National Capital", "#8AA0B8", "#2B3A4A", "#C9A227", "monument"),
    ("dest-agra.svg", "Agra", "Uttar Pradesh", "#E8C9A0", "#6B5344", "#C9A227", "monument"),
    ("dest-varanasi.svg", "Varanasi", "Uttar Pradesh", "#E39B6A", "#6B2E1A", "#C9A227", "temple"),
    ("dest-jaipur.svg", "Jaipur", "Rajasthan", "#E07A5F", "#8F1D1D", "#C9A227", "palace"),
    ("dest-udaipur.svg", "Udaipur", "Rajasthan", "#5FA8D3", "#1F4D5A", "#C9A227", "lake"),
    ("dest-amritsar.svg", "Amritsar", "Punjab", "#F0D080", "#4A3B12", "#C9A227", "temple"),
    ("dest-goa.svg", "Goa", "West Coast", "#3AA0B5", "#0F3D3A", "#C9A227", "beach"),
    ("dest-munnar.svg", "Munnar", "Kerala", "#6B8F3A", "#1A3D1A", "#C9A227", "hill"),
    ("dest-alleppey.svg", "Alleppey", "Kerala", "#3AA0B5", "#145C5A", "#C9A227", "lake"),
    ("dest-hampi.svg", "Hampi", "Karnataka", "#D4A373", "#6B4423", "#C9A227", "monument"),
    ("dest-mysore.svg", "Mysuru", "Karnataka", "#E8C36A", "#6B3A1A", "#C9A227", "palace"),
    ("dest-madurai.svg", "Madurai", "Tamil Nadu", "#E07A5F", "#6B1D1A", "#C9A227", "temple"),
    ("dest-ooty.svg", "Ooty", "Tamil Nadu", "#88B04B", "#1F4D3A", "#C9A227", "hill"),
    ("dest-kevadia.svg", "Kevadia", "Gujarat", "#7BB3C9", "#1F3A4D", "#C9A227", "monument"),
    ("dest-kutch.svg", "Rann of Kutch", "Gujarat", "#F0E6C8", "#8A6A3A", "#C9A227", "festival"),
    ("dest-kolkata.svg", "Kolkata", "West Bengal", "#8AA0B8", "#2B3A4A", "#C9A227", "palace"),
    ("dest-darjeeling.svg", "Darjeeling", "West Bengal", "#88B04B", "#1A3D2A", "#C9A227", "hill"),
    ("dest-shimla.svg", "Shimla", "Himachal Pradesh", "#A8C5D4", "#2B4A4A", "#C9A227", "hill"),
    ("dest-manali.svg", "Manali", "Himachal Pradesh", "#7BB3C9", "#1F3A4D", "#C9A227", "hill"),
    ("dest-rishikesh.svg", "Rishikesh", "Uttarakhand", "#7BB3C9", "#1F4D3A", "#C9A227", "temple"),
    ("dest-nainital.svg", "Nainital", "Uttarakhand", "#5FA8D3", "#1F4D5A", "#C9A227", "lake"),
    ("dest-srinagar.svg", "Srinagar", "Jammu & Kashmir", "#5FA8D3", "#1F3A4D", "#C9A227", "lake"),
    ("dest-gulmarg.svg", "Gulmarg", "Jammu & Kashmir", "#D9E6F0", "#4A6B7A", "#C9A227", "hill"),
    ("dest-khajuraho.svg", "Khajuraho", "Madhya Pradesh", "#D4A373", "#6B4423", "#C9A227", "temple"),
    ("ajanta-caves.svg", "Ajanta Caves", "UNESCO Heritage, Maharashtra", "#C9A66B", "#4A3424", "#C9A227", "cave"),
    ("ellora-caves.svg", "Ellora Caves", "UNESCO Heritage, Maharashtra", "#D4A373", "#5C3B1E", "#C9A227", "cave"),
    ("gateway-of-india.svg", "Gateway of India", "Mumbai", "#8AA0B8", "#2B3A4A", "#C9A227", "monument"),
    ("lonavala.svg", "Lonavala", "Sahyadri Hills", "#7BB3C9", "#1F4D3A", "#C9A227", "hill"),
    ("mahabaleshwar.svg", "Mahabaleshwar", "Hill Station", "#88B04B", "#145C3A", "#C9A227", "hill"),
    ("india-gate.svg", "India Gate", "New Delhi", "#A8B8C8", "#3A4A5A", "#C9A227", "monument"),
    ("red-fort.svg", "Red Fort", "Delhi", "#C45C26", "#6B1D1A", "#C9A227", "fort"),
    ("qutub-minar.svg", "Qutub Minar", "Delhi", "#C9A66B", "#5C3B1E", "#C9A227", "monument"),
    ("taj-mahal.svg", "Taj Mahal", "Agra", "#E8EEF2", "#6B7A88", "#C9A227", "monument"),
    ("varanasi-ghats.svg", "Varanasi Ghats", "Uttar Pradesh", "#E39B6A", "#6B2E1A", "#C9A227", "temple"),
    ("hawa-mahal.svg", "Hawa Mahal", "Jaipur", "#E07A5F", "#8F1D1D", "#C9A227", "palace"),
    ("amer-fort.svg", "Amer Fort", "Jaipur", "#D4A373", "#6B3A1A", "#C9A227", "fort"),
    ("city-palace-udaipur.svg", "City Palace", "Udaipur", "#5FA8D3", "#1F4D5A", "#C9A227", "palace"),
    ("golden-temple.svg", "Golden Temple", "Amritsar", "#F0D080", "#4A3B12", "#C9A227", "temple"),
    ("goa-beach.svg", "Goa Beaches", "Arabian Sea", "#3AA0B5", "#0F3D3A", "#C9A227", "beach"),
    ("basilica-bom-jesus.svg", "Basilica of Bom Jesus", "Old Goa", "#C9A66B", "#5C3B1E", "#C9A227", "monument"),
    ("munnar.svg", "Munnar", "Tea Gardens, Kerala", "#6B8F3A", "#1A3D1A", "#C9A227", "hill"),
    ("alleppey-backwaters.svg", "Alleppey Backwaters", "Kerala", "#3AA0B5", "#145C5A", "#C9A227", "lake"),
    ("hampi.svg", "Hampi", "Vijayanagara", "#D4A373", "#6B4423", "#C9A227", "monument"),
    ("mysore-palace.svg", "Mysore Palace", "Mysuru", "#E8C36A", "#6B3A1A", "#C9A227", "palace"),
    ("meenakshi-temple.svg", "Meenakshi Temple", "Madurai", "#E07A5F", "#6B1D1A", "#C9A227", "temple"),
    ("ooty.svg", "Ooty", "Nilgiri Hills", "#88B04B", "#1F4D3A", "#C9A227", "hill"),
    ("statue-of-unity.svg", "Statue of Unity", "Gujarat", "#7BB3C9", "#1F3A4D", "#C9A227", "monument"),
    ("rann-of-kutch.svg", "Rann of Kutch", "Gujarat", "#F0E6C8", "#8A6A3A", "#C9A227", "festival"),
    ("victoria-memorial.svg", "Victoria Memorial", "Kolkata", "#E8EEF2", "#4A5A6A", "#C9A227", "palace"),
    ("darjeeling.svg", "Darjeeling", "Tea Hills", "#88B04B", "#1A3D2A", "#C9A227", "hill"),
    ("shimla.svg", "Shimla", "Himachal Pradesh", "#A8C5D4", "#2B4A4A", "#C9A227", "hill"),
    ("manali.svg", "Manali", "Himachal Pradesh", "#7BB3C9", "#1F3A4D", "#C9A227", "hill"),
    ("rishikesh.svg", "Rishikesh", "Yoga Capital", "#7BB3C9", "#1F4D3A", "#C9A227", "temple"),
    ("nainital.svg", "Nainital", "Lake District", "#5FA8D3", "#1F4D5A", "#C9A227", "lake"),
    ("srinagar.svg", "Dal Lake, Srinagar", "Jammu & Kashmir", "#5FA8D3", "#1F3A4D", "#C9A227", "lake"),
    ("gulmarg.svg", "Gulmarg", "Meadow of Flowers", "#D9E6F0", "#4A6B7A", "#C9A227", "hill"),
    ("khajuraho.svg", "Khajuraho Temples", "Madhya Pradesh", "#D4A373", "#6B4423", "#C9A227", "temple"),
    ("spec-misal-pav.svg", "Misal Pav", "Maharashtra", "#C45C26", "#6B2E1A", "#C9A227", "food"),
    ("spec-puran-poli.svg", "Puran Poli", "Maharashtra", "#E8C36A", "#8A5A1A", "#C9A227", "food"),
    ("spec-modak.svg", "Modak", "Maharashtra", "#E8C36A", "#1F6B4A", "#C9A227", "food"),
    ("spec-vada-pav.svg", "Vada Pav", "Mumbai", "#C45C26", "#5C3B1E", "#C9A227", "food"),
    ("spec-dhokla.svg", "Dhokla", "Gujarat", "#E8C36A", "#6B8F3A", "#C9A227", "food"),
    ("spec-dal-baati.svg", "Dal Baati Churma", "Rajasthan", "#D4A373", "#8A5A1A", "#C9A227", "food"),
    ("spec-amritsari.svg", "Amritsari Kulcha", "Punjab", "#E8C36A", "#8F1D1D", "#C9A227", "food"),
    ("spec-rosogolla.svg", "Rosogolla", "West Bengal", "#F7F1E6", "#8A5A4A", "#C9A227", "food"),
    ("spec-dosa.svg", "Masala Dosa", "South India", "#E8C36A", "#6B4423", "#C9A227", "food"),
    ("spec-goan-curry.svg", "Goan Fish Curry", "Goa", "#C45C26", "#1F4D5A", "#C9A227", "food"),
    ("spec-rogan-josh.svg", "Rogan Josh", "Kashmir", "#8F1D1D", "#4A1A1A", "#C9A227", "food"),
    ("spec-paithani.svg", "Paithani Saree", "Maharashtra", "#C45C26", "#1F6B4A", "#C9A227", "craft"),
    ("spec-blue-pottery.svg", "Blue Pottery", "Jaipur", "#5FA8D3", "#1F3A4D", "#C9A227", "craft"),
    ("spec-pashmina.svg", "Pashmina", "Kashmir", "#7BB3C9", "#4A3B12", "#C9A227", "craft"),
    ("spec-chikankari.svg", "Chikankari", "Lucknow", "#F7F1E6", "#6B8F71", "#C9A227", "craft"),
    ("culture-ganesh-chaturthi.svg", "Ganesh Chaturthi", "Maharashtra Festival", "#E8C36A", "#1F6B4A", "#C9A227", "festival"),
    ("culture-lavani.svg", "Lavani", "Maharashtra Dance", "#C45C26", "#6B1D1A", "#C9A227", "dance"),
    ("culture-kathakali.svg", "Kathakali", "Kerala Dance Drama", "#1F6B4A", "#4A1A1A", "#C9A227", "dance"),
    ("culture-garba.svg", "Garba", "Gujarat Festival", "#E07A5F", "#8F1D1D", "#C9A227", "festival"),
    ("culture-bhangra.svg", "Bhangra", "Punjab Folk Dance", "#E8C36A", "#8F1D1D", "#C9A227", "dance"),
    ("culture-durga-puja.svg", "Durga Puja", "West Bengal", "#E8C36A", "#8F1D1D", "#C9A227", "festival"),
    ("culture-onam.svg", "Onam", "Kerala Harvest", "#6B8F3A", "#1A3D1A", "#C9A227", "festival"),
    ("culture-kathak.svg", "Kathak", "North Indian Dance", "#C45C26", "#4A1A3A", "#C9A227", "dance"),
    ("culture-warli.svg", "Warli Art", "Maharashtra", "#F4E4C1", "#1F2A26", "#C9A227", "craft"),
    ("culture-rajasthani.svg", "Rajasthani Folk", "Rajasthan", "#E07A5F", "#8F1D1D", "#C9A227", "dance"),
    ("culture-kumbh-mela.svg", "Kumbh Mela", "Sacred Gathering", "#E39B6A", "#6B2E1A", "#C9A227", "festival"),
    ("culture-phulkari.svg", "Phulkari", "Punjab Embroidery", "#C45C26", "#1F6B4A", "#C9A227", "craft"),
    ("biz-paithani.svg", "Paithani Weaving Centre", "Handloom", "#C45C26", "#1F6B4A", "#C9A227", "business"),
    ("biz-misal.svg", "Puneri Misal House", "Local Food", "#C45C26", "#6B2E1A", "#C9A227", "business"),
    ("biz-guide-jaipur.svg", "Jaipur Heritage Walks", "Local Guide", "#E07A5F", "#8F1D1D", "#C9A227", "business"),
    ("biz-kashmir-crafts.svg", "Kashmir Craft House", "Handicraft", "#5FA8D3", "#1F3A4D", "#C9A227", "business"),
    ("biz-goa-guide.svg", "Goa Coastal Guides", "Tourism Service", "#3AA0B5", "#0F3D3A", "#C9A227", "business"),
    ("biz-kerala-houseboat.svg", "Alleppey Houseboats", "Tourism Service", "#3AA0B5", "#145C5A", "#C9A227", "business"),
    ("biz-kolkata-sweet.svg", "Kolkata Mishti Ghar", "Food Outlet", "#F7F1E6", "#8A5A4A", "#C9A227", "business"),
    ("biz-varanasi-silk.svg", "Banarasi Silk Atelier", "Handloom", "#E8C36A", "#6B2E1A", "#C9A227", "business"),
    ("biz-amritsar-langar.svg", "Amritsar Culinary Walk", "Cultural Service", "#F0D080", "#4A3B12", "#C9A227", "business"),
    ("biz-chappal.svg", "Kolhapuri Craft Studio", "Artisan", "#6B4423", "#1F2A26", "#C9A227", "business"),
]

for item in ITEMS:
    poster(*item)

print("Wrote", len(ITEMS), "SVG files to", OUT)
