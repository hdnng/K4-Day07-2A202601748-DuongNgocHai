import csv, re
from pathlib import Path

D = Path('data/k4_ecommerce')
REQ = ['doc_id','title','source_url','retrieved_at','document_version']
mds = sorted(D.glob('*.md'))
rows = list(csv.DictReader(open(D/'sources.csv', encoding='utf-8')))
ids, roles = [], {}
KEY = 'customer_role'

for p in mds:
    # Lấy YAML front matter
    content = p.read_text(encoding='utf-8')
    parts = content.split('---')
    if len(parts) > 2:
        front_matter = parts[1]
    else:
        front_matter = ""
        
    fm = dict(re.findall(r'^(\w+):\s*(.+)$', front_matter, re.M))
    ids.append(fm.get('doc_id'))
    roles[fm.get(KEY)] = roles.get(fm.get(KEY), 0) + 1
    
    ok = all(k in fm for k in REQ) and KEY in fm and fm.get('doc_id') == p.stem
    print(f'{p.name:40} {"OK" if ok else "THIEU METADATA"}')

print('so file :', len(mds), '(can 5-10)')
print('csv     :', 'khop' if sorted(r['doc_id'] for r in rows) == sorted(ids) else 'LECH')
print(KEY, ':', roles)
