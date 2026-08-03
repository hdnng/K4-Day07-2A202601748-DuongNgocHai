import os
from pathlib import Path
from src.chunking import ChunkingStrategyComparator

data_dir = Path("data/k4_ecommerce")
docs = []
for p in data_dir.glob("*.md"):
    if "lazada" in p.name or "decathlon" in p.name:
        content = p.read_text(encoding="utf-8")
        # Bỏ YAML front matter
        parts = content.split('---')
        if len(parts) > 2:
            body = '---'.join(parts[2:]).strip()
        else:
            body = content.strip()
        docs.append(body)

comparator = ChunkingStrategyComparator()
text_to_compare = "\n\n".join(docs)
results = comparator.compare(text_to_compare)

for strategy, stats in results.items():
    print(f"Strategy: {strategy}")
    print(f"Count: {stats['count']}")
    print(f"Avg Length: {stats['avg_length']:.2f}")
    print("-----------")
