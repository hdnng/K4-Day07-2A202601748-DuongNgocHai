import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from ingest import build_knowledge_base
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker
from src.agent import KnowledgeBaseAgent

# Default to mock embedder if OPENAI_API_KEY is not set or Local is not installed
try:
    from src import LocalEmbedder
    embedder = LocalEmbedder()
except Exception:
    from src import _mock_embed
    embedder = _mock_embed

queries = [
    "Theo quy định của Shopee, mã giảm giá có được hoàn lại nếu tôi khiếu nại trả hàng/hoàn tiền một phần đơn hàng không?",
    "Tại Thế Giới Di Động, nếu tôi mua điện thoại và muốn hoàn tiền (trả máy) trong tháng thứ 2 thì phí hoàn tiền sẽ được tính như thế nào?",
    "Đối với các sản phẩm thể thao không do Decathlon sản xuất như của thương hiệu Garmin, tôi có được hưởng chính sách đổi trả tại cửa hàng Decathlon không?",
    "Trên Lazada, khi nào tính năng Autobypass (tự động duyệt yêu cầu đổi trả) sẽ được kích hoạt?",
    "Tôi mua một chiếc tivi (cần lắp đặt) giá 4.000.000đ tại Thế Giới Di Động và nhà cách siêu thị 15km thì phí vận chuyển tính như thế nào?"
]

chunkers = {
    "FixedSize": FixedSizeChunker(chunk_size=150, overlap=30),
    "Sentence": SentenceChunker(max_sentences_per_chunk=3),
    "Recursive": RecursiveChunker(chunk_size=150)
}

print(f"Sử dụng mô hình Embedder: {getattr(embedder, '_backend_name', 'Mock')}\n")

for name, chunker in chunkers.items():
    print(f"\n{'='*60}")
    print(f"CHIẾN LƯỢC CHUNKING: {name.upper()}")
    print(f"{'='*60}")
    
    # Build store
    store = build_knowledge_base(
        data_dir="data/k4_ecommerce", 
        embedding_fn=embedder, 
        chunker=chunker, 
        collection_name=f"benchmark_{name.lower()}"
    )
    
    agent = KnowledgeBaseAgent(store, llm_fn=lambda x: "[Mock LLM Generation]")
    
    for i, q in enumerate(queries, 1):
        print(f"\n[Câu hỏi {i}]: {q}")
        
        # In this mock environment, agent.answer() just returns a mock answer based on retrieved contexts.
        # So we also manually print the top retrieved chunk to evaluate retrieval quality.
        retrieved = store.search(q, top_k=1)
        if retrieved:
            top_doc = retrieved[0]
            doc_id = top_doc.get('metadata', {}).get('doc_id', 'unknown')
            content = top_doc.get('content', '')
            print(f"> Chunk tốt nhất (doc_id: {doc_id}): {repr(content[:150])}...")
        else:
            print("> Không tìm thấy thông tin nào phù hợp.")
