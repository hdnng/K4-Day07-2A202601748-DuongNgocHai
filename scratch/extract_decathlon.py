import json
import re
from bs4 import BeautifulSoup

file_path = r'C:\Users\Admin\.gemini\antigravity-ide\brain\3bc8b4f0-02c0-43d3-9885-2f3544f2234a\.system_generated\steps\197\content.md'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # We want to extract text from the JSON. The JSON has 'nodeType': 'text', 'value': '...'
    def extract_text(node):
        result = []
        if isinstance(node, dict):
            if node.get('nodeType') == 'text' and 'value' in node:
                result.append(node['value'])
            
            # also look for headlines if they exist directly
            if 'contentHeadline' in node:
                result.append('\n## ' + node['contentHeadline'] + '\n')
                
            for k, v in node.items():
                result.extend(extract_text(v))
        elif isinstance(node, list):
            for item in node:
                result.extend(extract_text(item))
        return result
        
    extracted_strings = extract_text(data)
    
    # Clean up and join
    policy_text = ""
    for s in extracted_strings:
        if s.startswith('\n##'):
            policy_text += s
        else:
            policy_text += s + " "
    
    # Clean up double spaces or bad formatting
    policy_text = policy_text.replace('  ', ' ')
    
    md_content = f"""---
doc_id: decathlon-doi-tra
title: "Chính sách đổi trả hàng | Decathlon Việt Nam"
customer_role: both
category: returns
language: vi
source_url: https://www.decathlon.vn/s/chinh-sach-doi-tra-hang
retrieved_at: 2026-08-03
document_version: "1.0"
---

# Chính sách đổi trả hàng | Decathlon Việt Nam

{policy_text}
"""
    with open('data/k4_ecommerce/decathlon-doi-tra.md', 'w', encoding='utf-8') as f2:
        f2.write(md_content)
    print("Successfully extracted policy to data/k4_ecommerce/decathlon-doi-tra.md")
else:
    print("Could not find __NEXT_DATA__ in the file")
