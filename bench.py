import os
from dotenv import load_dotenv

load_dotenv()
os.environ["EMBEDDING_PROVIDER"] = "local"

from ingest import build_knowledge_base
from src.chunking import RecursiveChunker
from src.agent import KnowledgeBaseAgent

try:
    from src import LocalEmbedder
    embedding_fn = LocalEmbedder()
except Exception:
    from src import _mock_embed
    embedding_fn = _mock_embed

# 1. Chọn chunker của riêng bạn (Strategy riêng)
chunk_size = 150
chunker = RecursiveChunker(chunk_size=chunk_size)

print(f"============================================================")
print(f"CHIẾN LƯỢC CHUNKING: RecursiveChunker (chunk_size={chunk_size})")
print(f"Mô hình nhúng: {getattr(embedding_fn, '_backend_name', 'Mock')}")
print(f"============================================================\n")

# 2. Nạp cả thư mục corpus
store = build_knowledge_base("data/k4_ecommerce", embedding_fn, chunker=chunker, collection_name="bench_collection")
agent = KnowledgeBaseAgent(store, llm_fn=lambda x: "[LLM Answer Placeholder]")

print(f"-> Đã nạp tổng cộng {store.get_collection_size()} chunks vào EmbeddingStore.\n")

# 3. Chạy 5 query đánh giá
queries = [
    {
        "q": "Theo quy định của Shopee, mã giảm giá có được hoàn lại nếu tôi khiếu nại trả hàng/hoàn tiền một phần đơn hàng không?",
        "filter": None
    },
    {
        "q": "Tại Thế Giới Di Động, nếu tôi mua điện thoại và muốn hoàn tiền (trả máy) trong tháng thứ 2 thì phí hoàn tiền sẽ được tính như thế nào?",
        "filter": None
    },
    {
        "q": "Đối với các sản phẩm thể thao không do Decathlon sản xuất như của thương hiệu Garmin, tôi có được hưởng chính sách đổi trả tại cửa hàng Decathlon không?",
        "filter": None
    },
    {
        "q": "Trên Lazada, khi nào tính năng Autobypass (tự động duyệt yêu cầu đổi trả) sẽ được kích hoạt?",
        "filter": None
    },
    {
        "q": "Tôi mua một chiếc tivi (cần lắp đặt) giá 4.000.000đ tại Thế Giới Di Động và nhà cách siêu thị 15km thì phí vận chuyển tính như thế nào?",
        "filter": {"category": "shipping"} # Query yêu cầu lọc theo category bắt buộc
    }
]

for i, item in enumerate(queries, 1):
    q = item["q"]
    meta_filter = item["filter"]
    print(f"\n[Câu hỏi {i}]: {q}")
    if meta_filter:
        print(f"(Áp dụng Metadata Filter: {meta_filter})")
        retrieved = store.search_with_filter(q, top_k=3, metadata_filter=meta_filter)
    else:
        retrieved = store.search(q, top_k=3)
        
    print("Top-3 Chunks truy xuất được:")
    for rank, doc in enumerate(retrieved, 1):
        score = doc.get("score", 0.0)
        doc_id = doc.get("metadata", {}).get("doc_id", "unknown")
        content = doc.get("content", "").replace('\n', ' ')
        preview = (content[:100] + '...') if len(content) > 100 else content
        print(f"  #{rank} | Score: {score:.4f} | Doc_id: {doc_id} | Preview: {preview}")
        
    # Gọi agent
    # Agent hiện tại đang search lại bên trong nó (top_k=3 mặc định)
    # Vì bài yêu cầu in ra câu trả lời của agent
    answer = agent.answer(q, top_k=3)
    print(f"Agent Answer: {answer}")
