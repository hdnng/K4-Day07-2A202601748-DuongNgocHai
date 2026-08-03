# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Dương Ngọc Hải
**Nhóm:** K4-Ecommerce
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Nghĩa là góc giữa hai vector đại diện cho hai đoạn văn bản rất nhỏ (gần bằng 0), tức là chúng có chung ngữ nghĩa, chung chủ đề hoặc chung ngữ cảnh sử dụng, bất kể độ dài ngắn của văn bản.*

**Ví dụ có độ tương tự CAO:**
- Câu A: Chính sách đổi trả rất tốt.
- Câu B: Chính sách trả hàng rất tuyệt vời.
- Tại sao tương đồng: Chứa các từ đồng nghĩa (đổi trả - trả hàng, rất tốt - rất tuyệt vời) và cùng chung một ngữ nghĩa là khen ngợi chính sách.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Laptop bị hỏng màn hình.
- Câu B: Apple ra mắt iPhone mới.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau (báo cáo lỗi thiết bị vs tin tức ra mắt sản phẩm), không chia sẻ các cụm từ vựng liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Vì khoảng cách Euclid bị ảnh hưởng rất mạnh bởi độ lớn (magnitude) của vector (phụ thuộc trực tiếp vào độ dài câu). Cosine similarity chỉ quan tâm đến HƯỚNG của vector (góc giữa chúng), nên 1 câu rất ngắn và 1 câu rất dài nhưng cùng ý nghĩa (cùng hướng) vẫn sẽ có cosine cao.*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính: Số lượng chunk = (10,000 - 50) / (500 - 50) = 9950 / 450 = 22.11*
> *Đáp án: 23 chunks (do phải làm tròn lên).*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Số lượng chunk sẽ tăng lên: (10,000 - 100) / (500 - 100) = 9900 / 400 = 24.75 -> 25 chunks. Muốn overlap cao hơn để đảm bảo không có bất kỳ một ý quan trọng nào bị cắt đứt gãy làm đôi giữa biên giới của 2 chunk, giúp giữ trọn vẹn ngữ cảnh.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Tôi sử dụng biểu thức chính quy (regex) `(?<=[.!?])\s+|(?<=\.)\n` kết hợp cơ chế lookbehind để tách câu chính xác sau các dấu câu kết thúc mà không làm mất chính dấu câu đó. Loại bỏ các khoảng trắng thừa, sau đó ghép nối các câu lại theo nhóm (ví dụ 3 câu / 1 chunk).*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Dùng thuật toán đệ quy. Bắt đầu cắt với separator ưu tiên nhất (`\n\n`). Nếu sau khi ghép mà phần (part) tạo ra vẫn lớn hơn `chunk_size`, hàm sẽ gọi đệ quy chính nó để cắt đoạn văn đó bằng separator tiếp theo (ví dụ `\n` hoặc dấu chấm `.`)*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Khi `add_documents`, mỗi Document được chuyển thành một dict lưu `id`, `content`, `metadata` và embedding vector. Hàm `search` duyệt qua toàn bộ kho (in-memory fallback), gọi `compute_similarity` để so sánh query embedding với từng chunk, sau đó sort giảm dần theo score và lấy `top_k`.*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Lọc (filter) TRƯỚC khi tính toán: duyệt list các bản ghi, nếu metadata khớp với điều kiện lọc thì mới đem vào mảng để tính Cosine Similarity (giúp tiết kiệm cực kỳ nhiều CPU). Xóa bằng cách tạo lại mảng (loại bỏ các record có `metadata["doc_id"]` khớp với ID truyền vào).*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Gọi `store.search(question)` để lấy về Top K chunks liên quan nhất. Dùng vòng lặp ghép chuỗi `content` của các chunks này lại làm context. Cuối cùng đưa context và question vào chuỗi Prompt định dạng sẵn rồi truyền cho hàm `llm_fn` để sinh câu trả lời.*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\VINUNI\d7\K4-Day07-2A202601748-DuongNgocHai
plugins: anyio-4.14.2
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
... (Các test case ở giữa đều PASSED) ...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.22s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả rất tốt | Chính sách trả hàng rất tuyệt vời | cao | 0.8402 | Có |
| 2 | Bảo hành 12 tháng | Không hỗ trợ đổi trả | thấp | 0.1808 | Có |
| 3 | Phí vận chuyển là 50k | Tiền ship là 50 ngàn | cao | 0.7470 | Có |
| 4 | Mã giảm giá không hoàn lại | Voucher không được trả lại | cao | 0.4857 | Không |
| 5 | Laptop bị hỏng màn hình | Apple ra mắt iPhone mới | thấp | 0.1084 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Kết quả ở Cặp 4 (Mã giảm giá vs Voucher) làm tôi bất ngờ nhất. Tôi nghĩ nó phải đạt điểm > 0.8 vì đồng nghĩa hoàn toàn, nhưng thực tế chỉ đạt ~0.48 (mức trung bình). Điều này cho thấy Embedder (mô hình MiniLM) học ý nghĩa thống kê của từ ngữ trên các không gian ngôn ngữ chung chung, và vẫn còn hạn chế trong việc bắt cặp các từ mượn tiếng Anh phổ biến tại Việt Nam.*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mã giảm giá có được hoàn lại nếu khiếu nại trả hàng 1 phần đơn không? | "# Quy định chung về Trả hàng/Hoàn tiền..." | 0.7049 | Có | Không, chỉ được hoàn lại khi trả toàn bộ đơn hàng. |
| 2 | TGDD hoàn tiền tháng thứ 2 tính phí ntn? | "Đơn hàng dưới 5.000.000đ: phí cơ bản 50.000đ..." | 0.5668 | Có | Tính phí hoàn tiền bị trừ 10%. |
| 3 | Sản phẩm Garmin mua tại Decathlon có đổi trả được không? | "- Sản phẩm được mua bằng thẻ quà tặng..." | 0.6882 | Có | Sản phẩm bên thứ ba do nhà sản xuất bảo hành. |
| 4 | Trên Lazada, khi nào tính năng Autobypass tự kích hoạt? | "*Lưu ý: Nếu NBH không thực hiện các phản hồi sau khi hoàn tất quy trình QC..."| 0.5478 | Có | Kích hoạt sau 30 ngày nếu NBH không phản hồi. |
| 5 | Tivi 4tr cách TGDD 15km thì phí ship bao nhiêu? | "- Đơn hàng dưới 5.000.000đ: phí cơ bản 50.000đ, sau đó 5.000đ/km." | 0.6082 | Có | Phí 50.000đ cho 10km đầu + 25.000đ cho 5km sau = 75.000đ. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Việc gán Metadata thiết thực đôi khi còn quan trọng hơn cả việc loay hoay tinh chỉnh thuật toán Chunking. Khi kho dữ liệu quá lớn (tích hợp hàng chục chính sách từ các nguồn khác nhau), các chunk nói về "tiền phí" vận chuyển rất dễ bị trùng lặp với "tiền phí" hoàn trả nếu chỉ dựa vào thuật toán nhúng; Metadata Filter chính là chìa khóa.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Bằng chứng / Đánh giá khách quan (Unbiased Evaluation) |
|----------|-------------------|-----------------------------------------------------|
| Khởi động (Warm-up) | 5 / 5 | Trả lời đúng trọng tâm bản chất Cosine (dựa vào hướng vector) và tính toán chính xác số lượng Chunk (23). |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 | Đã giải thích rõ ràng luồng xử lý của các hàm. Tuy nhiên, tự trừ 1 điểm vì phần phân tích chưa đánh giá sâu về độ phức tạp thời gian (Time Complexity) khi đệ quy với văn bản cực dài. |
| Hoàn thiện code (Core Implementation) | 30 / 30 | Đạt tuyệt đối. Bằng chứng: Vượt qua toàn bộ **42/42 test cases** không có ngoại lệ (log đính kèm). |
| Dự đoán độ tương tự (Predictions) | 5 / 5 | Tính toán trung thực bằng Local Embedder. Phát hiện và lý giải được điểm bất thường thú vị ở cặp từ khóa tiếng Anh "Voucher" và "Mã giảm giá". |
| Kết quả truy xuất (Competition Results) | 9 / 10 | Trả về đúng 5/5 câu hỏi trong Top-3. Tuy nhiên, tự trừ 1 điểm vì điểm Score của Câu 2 và Câu 4 hơi thấp (chỉ khoảng 0.54 - 0.56), cho thấy kích thước `chunk_size=150` vẫn có thể chưa phải là thông số hoàn hảo nhất. |
| **Tổng phần cá nhân** | **58 / 60** | **Tự đánh giá khách quan, trung thực và nhận thức rõ các điểm có thể tối ưu thêm.** |
