# Báo Cáo Nhóm (Làm độc lập) — Lab 7: Embedding & Vector Store

**Thành viên:** Dương Ngọc Hải (Kế thừa vai trò Nhóm)
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) được nộp trong `REPORT_CANHAN.md`. Do làm độc lập, báo cáo này đại diện cho toàn bộ hệ thống đánh giá bằng 1 chiến lược duy nhất được chọn.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể tập trung:**
> *Tập trung vào các chính sách đổi trả, bảo hành, quyền riêng tư và chính sách vận chuyển của các nền tảng thương mại điện tử lớn (Shopee, Lazada) và chuỗi bán lẻ (Thế Giới Di Động, Decathlon).*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Metadata đã gán (customer_role) |
|---|--------------|------------|--------------------|-----------------|
| 1 | `decathlon-doi-tra.md` | www.decathlon.vn | 2026-08-03 / v1.0 | both |
| 2 | `k4-shopee-return-refund.md` | help.shopee.vn | 2026-08-03 / not-stated | buyer |
| 3 | `k4-tgdd-shipping-policy.md` | thegioididong.com | 2026-08-03 / 2024-05-21 | both |
| 4 | `k4-tgdd-warranty-policy.md` | thegioididong.com | 2026-08-03 / 2024-11-10 | both |
| 5 | `lazada-doi-tra.md` | sellercenter.lazada.vn | 2026-08-03 / v1.0 | seller |
| 6 | `shopee-bao-hanh.md` | help.shopee.vn | 2026-08-03 / v1.0 | both |
| 7 | `shopee-privacy-policy.md` | help.shopee.vn | 2026-08-03 / 2026-06-11 | both |
| 8 | `shopee-shipping-policy.md` | help.shopee.vn | 2026-08-03 / not-stated | buyer |
| 9 | `shopee-terms-of-service.md` | help.shopee.vn | 2026-08-03 / not-stated | buyer |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `category` | string | `returns`, `warranty`, `shipping` | Cho phép Agent lọc trước (pre-filter) khi có câu hỏi chuyên biệt về một lĩnh vực (ví dụ: chỉ tìm trong mảng 'vận chuyển' thay vì tìm trong toàn bộ kho). |
| `customer_role` | string | `buyer`, `seller`, `both` | Giúp phân tách rõ ràng chính sách dành cho người mua và người bán, tránh việc lấy nhầm quy định của NBH để trả lời cho Khách hàng. |

---

## 2. Thiết kế chiến lược (Strategy Design) (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

*(Chạy bằng script `ChunkingStrategyComparator().compare()` trên 2 file: lazada-doi-tra.md và decathlon-doi-tra.md để đánh giá tổng quan cả 3 cơ chế)*

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| decathlon & lazada | FixedSizeChunker (`fixed_size`) | 71 | 198.44 ký tự | Tạm ổn, nhưng thỉnh thoảng cắt ngang giữa một câu mô tả điều kiện đổi trả quan trọng. |
| decathlon & lazada | SentenceChunker (`by_sentences`) | 28 | 451.46 ký tự | Giữ được trọn vẹn ngữ nghĩa của từng câu đơn lẻ nhưng thiếu tính liên kết ngữ cảnh trước/sau (do ghép nhiều câu lại). |
| decathlon & lazada | RecursiveChunker (`recursive`) | 96 | 130.62 ký tự | Tốt nhất. Giữ được toàn bộ đoạn văn bản nhỏ hoặc cấu trúc gạch đầu dòng Markdown một cách chặt chẽ. |

### Lựa Chọn Chiến Lược Thực Tế (Dương Ngọc Hải)

Dựa vào phân tích Baseline ở trên, tôi đã quyết định chọn **RecursiveChunker** làm chiến lược truy xuất chính (và duy nhất) cho toàn bộ hệ thống đánh giá.

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất dự kiến | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Dương Ngọc Hải | RecursiveChunker (150) | 9/10 | Tối ưu cho file Markdown. Luôn cố giữ các đoạn văn `\n\n` liền mạch với nhau, bảo toàn trọn vẹn ngữ cảnh của các điều kiện đi kèm. | Triển khai thuật toán phức tạp hơn. Một số chunk có thể dài hơn 150 ký tự nếu đoạn văn không có dấu câu ngắt dòng. |

**Tại sao chọn chiến lược này?**
> *Chiến lược **Recursive Chunker** là tối ưu nhất cho văn bản chính sách thương mại điện tử (thường dùng định dạng Markdown với nhiều list điều kiện). Nó tuân theo cấu trúc đoạn văn tự nhiên, giúp giữ nguyên vẹn một cụm "điều kiện đổi trả" liền mạch, cung cấp đủ bối cảnh (Context) để LLM sinh ra câu trả lời chuẩn xác.*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Theo quy định Shopee, mã giảm giá có được hoàn lại nếu trả hàng 1 phần không? | Không. Mã giảm giá chỉ được hoàn lại khi khiếu nại trả hàng toàn bộ đơn hàng. | `k4-shopee-return-refund.md` |
| 2 | Tại TGDD, mua điện thoại muốn hoàn tiền tháng thứ 2 tính phí ntn? | Trong tháng thứ 2 (đến tháng 12), phí hoàn tiền bị trừ 10%/tháng. | `k4-tgdd-warranty-policy.md` |
| 3 | Sản phẩm Garmin mua tại Decathlon có được đổi trả ở Decathlon không? | Không, sản phẩm Garmin sẽ do đơn vị sản xuất trực tiếp bảo hành. | `decathlon-doi-tra.md` |
| 4 | Trên Lazada, khi nào tính năng Autobypass tự động được kích hoạt? | Nếu NBH không phản hồi trong vòng 30 ngày sau quy trình kiểm tra chất lượng (QC). | `lazada-doi-tra.md` |
| 5 | Mua tivi 4 triệu tại TGDD cách nhà 15km thì phí vận chuyển bao nhiêu? | Dưới 5 triệu, phí cơ bản 50.000đ + (5km x 5.000đ) = 75.000đ. | `k4-tgdd-shipping-policy.md` |

### Tổng hợp chất lượng truy xuất (RecursiveChunker)

> *Chạy đánh giá bằng mô hình thực tế `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` kết hợp `RecursiveChunker`.*

| # | Câu hỏi | Có chunk liên quan trong top-3 không? | Phân tích lỗi / Đánh giá (Failure Analysis) |
|---|---------|--------------------------------------|---------------------------------------------|
| 1 | Câu 1 | Có (Top 1) | Điểm Score 0.7049, bắt đúng chunk nói về quy định hoàn lại mã giảm giá của Shopee nhờ bảo toàn được ngữ cảnh. |
| 2 | Câu 2 | Có (Top 3) | Lấy chính xác được dòng phần trăm phí (`- Tháng thứ 2-12: tính phí 10%...`). Do có nhiều đoạn nói về đổi trả nên đoạn này tụt xuống top 3. |
| 3 | Câu 3 | Có (Top 1) | Giữ được trọn vẹn ngữ cảnh đoạn quy định ngoại lệ dành riêng cho Garmin, không bị tách chữ Garmin ra khỏi quy định. |
| 4 | Câu 4 | Có (Top 1) | Tự động ghép đúng từ "Autobypass" vào cùng chunk có câu điều kiện 30 ngày. Truy xuất xuất sắc. |
| 5 | Câu 5 | Có (Top 1) | **Phải dùng Filter**. Nếu không có Filter, truy xuất bị nhiễu do điểm Score các văn bản đổi trả cũng khá cao. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Việc lọc (Metadata Filter) hỗ trợ rất lớn. Ở Câu 5 (hỏi về phí vận chuyển), nếu áp dụng Metadata Filter `{"category": "shipping"}`, hệ thống sẽ loại trừ hoàn toàn các tài liệu nói về bảo hành hoặc đổi trả. Điều này giúp loại bỏ rác (noise) ngay từ vòng gửi xe, tăng độ chính xác truy xuất lên 100% trong Top 1.*

---

## 4. Thuyết trình (Demo) & Bài học (5 điểm)

**Những phân tích (insights) hay nhất đã rút ra:**
> - Mô hình nhúng (Embedder) tiếng Việt đa ngữ là yếu tố quyết định; dùng Mock Embedder sẽ dẫn đến kết quả sai lệch hoàn toàn về mặt ngữ nghĩa (Truy xuất ngẫu nhiên).
> - Chiến lược `RecursiveChunker` thực sự ưu việt khi làm việc với tài liệu Markdown vì nó biết tôn trọng cấu trúc câu, giữ được các gạch đầu dòng (bullets) dính liền với ý chính của chúng.

**Nếu làm lại, sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> - Sẽ phân tách Metadata sâu hơn xuống cấp độ đoạn (Paragraph-level Metadata) thay vì chỉ gán cho toàn bộ tài liệu (Document-level) để bộ lọc phát huy sức mạnh tối đa hơn nữa đối với các file dài có chứa nhiều chủ đề con.
