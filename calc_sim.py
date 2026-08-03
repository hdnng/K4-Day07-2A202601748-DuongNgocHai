import os
from dotenv import load_dotenv

load_dotenv()
os.environ["EMBEDDING_PROVIDER"] = "local"

from src import LocalEmbedder
from src.chunking import compute_similarity

embedder = LocalEmbedder()

pairs = [
    ("Chính sách đổi trả rất tốt", "Chính sách trả hàng rất tuyệt vời"),
    ("Bảo hành 12 tháng", "Không hỗ trợ đổi trả"),
    ("Phí vận chuyển là 50k", "Tiền ship là 50 ngàn"),
    ("Mã giảm giá không hoàn lại", "Voucher không được trả lại"),
    ("Laptop bị hỏng màn hình", "Apple ra mắt iPhone mới")
]

for i, (a, b) in enumerate(pairs, 1):
    vec_a = embedder(a)
    vec_b = embedder(b)
    score = compute_similarity(vec_a, vec_b)
    print(f"Pair {i}: {score:.4f}")
