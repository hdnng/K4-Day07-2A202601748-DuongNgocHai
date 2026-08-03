import csv
import re
from pathlib import Path

data_dir = Path("data/k4_ecommerce")
csv_path = data_dir / "sources.csv"
md_files = sorted(data_dir.glob("*.md"))

rows = []
for p in md_files:
    content = p.read_text(encoding='utf-8')
    parts = content.split('---')
    if len(parts) > 2:
        front_matter = parts[1]
    else:
        front_matter = ""
        
    fm = dict(re.findall(r'^(\w+):\s*(.+)$', front_matter, re.M))
    
    doc_id = fm.get('doc_id', p.stem)
    title = fm.get('title', p.stem)
    source_url = fm.get('source_url', '')
    retrieved_at = fm.get('retrieved_at', '2026-08-03')
    document_version = fm.get('document_version', 'not-stated')
    
    rows.append({
        'doc_id': doc_id,
        'file_path': f"data/k4_ecommerce/{p.name}",
        'title': title,
        'source_url': source_url,
        'retrieved_at': retrieved_at,
        'document_version': document_version,
        'license_or_permission': 'public'
    })

fieldnames = ['doc_id', 'file_path', 'title', 'source_url', 'retrieved_at', 'document_version', 'license_or_permission']

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Đã cập nhật {csv_path} với {len(rows)} bản ghi.")
