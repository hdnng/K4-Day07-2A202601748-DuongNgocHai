# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Hoinguoicaotuoi
**Thành viên:** 
1. Trần Duy Sơn
2. Sai Hoài Nam
3. Phạm Hoàng Nam
4. Dương Ngọc Hải

**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> *Chính sách đổi trả, hoàn tiền, vận chuyển và bảo hành của các sàn thương mại điện tử (Shopee, Lazada, Thế Giới Di Động, Decathlon).*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định chung về Trả hàng/Hoàn tiền của Shopee | [Shopee Help](https://help.shopee.vn/4/article/188931-%5BTr%E1%BA%A3-h%C3%A0ng%2FHo%C3%A0n-ti%E1%BB%81n%5D-Nh%E1%BB%AFng-quy-%C4%91%E1%BB%8Bnh-chung-v%E1%BB%81-Tr%E1%BA%A3-h%C3%A0ng%2FHo%C3%A0n-ti%E1%BB%81n-c%E1%BB%A7a-Shopee) | 2026-08-03 / not-stated | ~5,000 | `platform`, `category` |
| 2 | Chính sách bảo hành sản phẩm của Thế Giới Di Động | [TGDD](https://www.thegioididong.com/chinh-sach-bao-hanh-san-pham) | 2026-08-03 / 2024-11-10 | ~8,000 | `platform`, `category` |
| 3 | Chính sách đổi trả hàng \| Decathlon Việt Nam | [Decathlon](https://www.decathlon.vn/s/chinh-sach-doi-tra-hang) | 2026-08-03 / 1.0 | ~4,000 | `platform`, `category` |
| 4 | Chính sách Trả hàng trực tiếp cho NBH LazMall | [Lazada](https://sellercenter.lazada.vn/helpcenter/s/faq/knowledge?categoryId=1000028758&m_station=faq&questionId=1000149669) | 2026-08-03 / 1.0 | ~6,000 | `platform`, `customer_role`, `category` |
| 5 | Chính sách giao hàng của Thế Giới Di Động | [TGDD](https://www.thegioididong.com/giao-hang) | 2026-08-03 / 2024-05-21 | ~3,000 | `platform`, `category` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `platform` | str | `shopee`, `tgdd` | Lọc kết quả theo nền tảng, tránh nhầm lẫn chính sách giữa các sàn. |
| `category` | str | `return`, `shipping` | Thu hẹp phạm vi tìm kiếm theo chủ đề như vận chuyển, đổi trả hoặc bảo hành. |
| `customer_role` | str | `buyer`, `seller` | Lọc thông tin đặc thù dành cho người mua hoặc người bán (ví dụ: Lazada cho nhà bán hàng LazMall). |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy so sánh các chiến lược Chunking trên tài liệu mẫu để đánh giá tổng quan (bao gồm cả thuật toán tuỳ chỉnh):

| Thành viên | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|:---|:---|:---:|:---:|:---|
| **Phạm Hoàng Nam** | `FixedSizeChunker(300, overlap=50)` | 71 | 198.44 | Ngữ cảnh dễ bị cắt đứt giữa câu hoặc ý quan trọng. |
| **Trần Duy Sơn** | `SentenceChunker(2 câu/chunk)` | 28 | 451.46 | Giữ ngữ cảnh câu tốt, nhưng số câu/chunk không đồng đều. |
| **Dương Ngọc Hải** | `RecursiveChunker(chunk_size=150)` | 96 | 130.62 | Cân bằng hơn, tôn trọng dấu đoạn văn/xuống dòng nhưng chunk khá ngắn. |
| **Sai Hoài Nam** | `HeadingChunker(chunk_size=500)` | 80 | 361.27 | Giữ cấu trúc phân cấp xuất sắc nhờ tiêu đề (Heading), ngữ cảnh cực tốt. |

### Chiến lược của từng thành viên

**Thành viên 1 — Trần Duy Sơn**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=2)`
- **Mô tả & lý do chọn cho chủ đề này:** Tách các ý chi tiết cụ thể để không bị nhiễu. Dùng tối đa 2 câu/chunk giúp các điều kiện (ví dụ: điều kiện Autobypass và thời hạn 30 ngày) nằm chung trong một chunk rõ ràng để dễ truy xuất.

**Thành viên 2 — Sai Hoài Nam**
- **Loại chiến lược:** Custom `HeadingChunker(chunk_size=500)`
- **Mô tả & lý do chọn cho chủ đề này:** Dựa vào Heading Markdown (H1-H6) để duy trì cấu trúc hierarchy của tài liệu chính sách. Việc lặp lại `heading_path` giúp embedding luôn biết ngữ cảnh của các câu ngắn (như “trừ 10%” hoặc “50.000đ”).
- **Code snippet (nếu custom):**
```python
# Đại diện logic:
# 1. Nhận diện Markdown heading từ H1 đến H6 và duy trì hierarchy.
# 2. Gán heading_path vào đầu mỗi chunk để luôn giữ ngữ cảnh tổng.
# 3. Phân chia tiếp theo paragraph, dòng, câu, và từ; hard split chỉ dùng cuối cùng.
```

**Thành viên 3 — Phạm Hoàng Nam**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=300, overlap=50)`
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng chunking kích thước cố định với overlap vừa phải để bảo đảm giữ trọn vẹn được một ý/chính sách, đặc biệt khi các thông số điều kiện thay đổi rất nhanh trên cùng một đoạn. Kích thước 300 đủ để không quá ngắn và overlap 50 đủ để giữ ngữ cảnh.

**Thành viên 4 — Dương Ngọc Hải**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=150)`
- **Mô tả & lý do chọn cho chủ đề này:** Chia nhỏ theo từng đoạn văn/chấm câu để tìm thông tin chi tiết với granularity cao. Chunk ngắn giúp model dễ focus vào các con số điều kiện như "10%", "30 ngày" mà không bị pha loãng bởi văn bản xung quanh.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Duy Sơn | `SentenceChunker(2 câu/chunk)` | 10/10 | Rất linh hoạt, bắt các mốc thời gian và điều kiện rất chuẩn do ý không bị gộp chung. | Có thể bị mất context tổng quát (chủ đề chính sách). |
| Sai Hoài Nam | `HeadingChunker(chunk_size=500)` | 9/10 | Giữ ngữ cảnh hierarchy rất tốt (ví dụ: tiền phí thuộc phần nào). | Đòi hỏi xử lý custom phức tạp, chunk size lớn đôi khi gây nhiễu từ khóa. |
| Phạm Hoàng Nam | `FixedSizeChunker(300, overlap=50)` | 9/10 | Dễ triển khai, kết quả khá ổn định cho các thông tin rải rác. | Dễ cắt đứt ngữ nghĩa ở ranh giới 2 chunk mặc dù có overlap. |
| Dương Ngọc Hải | `RecursiveChunker(chunk_size=150)` | 9/10 | Bắt chi tiết nhạy bén (thông tin số liệu, tỷ lệ phần trăm). Code đơn giản. | Ngữ cảnh (vd: nền tảng nào) dễ bị mất vì chunk quá nhỏ. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Mặc dù `SentenceChunker` của Trần Duy Sơn đạt điểm cao nhất trên bộ câu hỏi (10/10), nhưng về mặt kiến trúc lâu dài cho tài liệu chính sách, chiến lược `HeadingChunker` kết hợp Metadata Filtering của Sai Hoài Nam là tốt và toàn diện nhất. Lý do là chính sách thương mại điện tử thường được trình bày dạng phân nhánh (Heading). Việc lặp lại `heading_path` giúp các thông số như 50.000đ ở section "Phí Vận Chuyển TGDD" không bị tách rời ý nghĩa bối cảnh tổng quát.*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mã giảm giá có được hoàn lại nếu tôi khiếu nại trả hàng/hoàn tiền một phần đơn hàng Shopee không? | Không, chỉ được hoàn lại khi trả toàn bộ đơn hàng (thuộc diện không nhận hàng hoặc gói hàng rỗng). | `k4-shopee-return-refund::chunk_0` / Heading `Điều khoản hoàn tiền` |
| 2 | Phí hoàn tiền điện thoại TGDD trong tháng thứ 2 tính thế nào? | Tháng 2–12 trừ 10%/tháng; (thiếu hộp trừ 2%, thiếu phụ kiện trừ tối đa 5%). | `k4-tgdd-warranty-policy::chunk_2` / `chunk_3`, `chunk_5` |
| 3 | Sản phẩm Garmin có áp dụng đổi trả tại Decathlon không? | Không, sản phẩm Garmin do nhà sản xuất (hãng) chịu trách nhiệm hậu mãi, không thuộc chính sách đổi trả của Decathlon. | `decathlon-doi-tra::chunk_21`, `chunk_27` / Heading `1. Chính sách đổi, trả hàng` |
| 4 | (Lazada LazMall) Khi nào tính năng Autobypass tự kích hoạt? | Kích hoạt nếu NBH không phản hồi sau khi hoàn tất QC trong vòng 30 ngày. | `lazada-doi-tra::chunk_12`, `chunk_14` / Heading `2. Cách xử lý đơn hàng yêu cầu đổi trả` |
| 5 | Phí giao tivi cần lắp đặt 4 triệu đồng, cách 15km tại TGDD là bao nhiêu? | 50.000đ cho 10km đầu và 5.000đ/km cho 5km tiếp theo, tổng là 75.000đ. | `k4-tgdd-shipping-policy::chunk_2`, `chunk_5` / Heading `Phí vận chuyển` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Trả mã giảm giá Shopee | Tất cả | Có (Top 1-2) | Khớp chính xác trên mọi chiến lược. |
| 2 | Phí hoàn tiền TGDD tháng 2 | `HeadingChunker` / `SentenceChunker` | Có | Fixed/Recursive mất điểm vì thiếu chi tiết phụ (phí mất hộp/phụ kiện). |
| 3 | Đổi trả Garmin Decathlon | Tất cả | Có (Top 1) | Tất cả đều truy xuất chính xác thông tin. |
| 4 | Autobypass Lazada | `RecursiveChunker` / `SentenceChunker` | Có | Chunk ngắn giúp bắt chính xác "30 ngày". Bắt buộc dùng filter `customer_role=seller`. |
| 5 | Phí ship Tivi TGDD 15km | `HeadingChunker(500)` + metadata | Có (Top 1) | `HeadingChunker` giúp agent suy luận 75k tốt nhất nhờ cung cấp đủ context từ đề mục "Phí vận chuyển". |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Rất hữu ích, đặc biệt cho câu 2, 4 và 5. Câu 4 bắt buộc dùng `customer_role=seller` để không nhầm với quy định của người mua. Câu 5 dùng `category=shipping` để loại bỏ các chunk nói về "tiền phí" liên quan đến bảo hành/đổi trả (giúp vượt qua nhiễu giữa "phí vận chuyển" và "phí hoàn tiền").*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Thiết kế Chunking theo cấu trúc tài liệu (Heading) thường giữ bối cảnh tốt nhất cho các tài liệu pháp lý/chính sách.
> 2. Kích thước chunk nhỏ (vd: Recursive 150 hoặc Sentence) giúp bắt chi tiết cực tốt (số liệu 10%, 30 ngày) nhưng lại đánh rơi bối cảnh (nền tảng nào, chính sách nào).
> 3. Các thuật ngữ "phí", "hoàn tiền", "tháng" thường gây nhiễu chéo (ví dụ: truy vấn phí của TGDD lại trả về chunk của Shopee do cosine similarity cao). Metadata Filtering là giải pháp cốt lõi để loại bỏ nhiễu này.

**Bài học rút ra khi so sánh trong nhóm:**
> *Mỗi chiến lược có một thế mạnh riêng biệt. Cùng một tài liệu, chiến lược Sentence/Recursive sẽ bắt các con số keyword cực nhạy bén, nhưng chiến lược Heading lại cung cấp bối cảnh toàn diện giúp LLM không bị ảo giác ngữ cảnh. Không có chiến lược nào hoàn hảo tuyệt đối.*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Nhóm sẽ triển khai một thuật toán kết hợp: HeadingChunker để giữ cấu trúc, nhưng khi chia nhỏ phần bên trong sẽ áp dụng Recursive/SentenceChunker linh hoạt. Ngoài ra, cần làm mịn bộ Metadata Filtering hơn nữa (thêm `applicable_products`, `conditions`).*

---

## Tự Đánh Giá (Phần Nhóm)

Đánh giá dựa trên sự công tâm, khách quan và kết quả thực tế của cả 4 thành viên:

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **37 / 40** |