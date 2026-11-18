# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`. Nhãn nhị phân PASS/FAIL, FAIL là lớp dương (judge phải tìm ra lỗi). Dữ liệu là bản replay đã công khai trong `data/eval/`.

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | Đạt (confusion tp 24, fp 4, fn 6, tn 66) | **Dùng** |
| helpful (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | **Không đạt** κ và recall (tp 9, fp 0, fn 21, tn 70) | **Loại** khỏi gate |

Tỉ lệ FAIL sau hiệu chỉnh Rogan-Gladen: tone quan sát 0.28, hiệu chỉnh 0.30. Helpful quan sát 0.09, hiệu chỉnh **0.30**: nếu tin judge thì báo cáo 9% lỗi trong khi lỗi thật khoảng 30%.

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha" | PASS | FAIL | Người: xưng "em" và "nha" quá suồng sã | Thêm quy tắc: mở bằng "Dạ", xưng "LogiX", gọi khách là "anh/chị"; cấm "em… nha" |
| 2 | H-029 "…không cần nhắn thêm" | PASS | FAIL | Người: giọng ra lệnh | Thêm quy tắc: không câu mệnh lệnh với khách; judge chỉ thấy "Dạ, vui lòng" nên cần ví dụ đối chứng |
| 3 | H-042 "…đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người: ngắn nhưng đủ ý, judge phạt vì thiếu xin lỗi | Bỏ yêu cầu bắt buộc xin lỗi; chỉ yêu cầu khi đơn bị trễ hoặc hỏng |
| 4 | H-051 "…đã refund 90.000đ" | FAIL | PASS | Người: CS LogiX cho phép từ "refund" | Thêm danh sách từ được phép (refund) vào rubric |
| 5 | H-081 "đơn O-107 chưa đủ điều kiện hoàn" | FAIL | PASS | **Judge đúng**: nhãn người đọc nhầm ticket (ghi chú trong CSV) | Sửa nhãn người thành FAIL; không sửa rubric. Nếu sửa: tp 25, fp 3, P 0.893, R 0.806, κ 0.784 |
| 6 | H-063 "đã hoàn 20.000đ và sẽ hoàn thêm" | PASS | FAIL | Người: hứa hoàn thêm ngoài kết quả hệ thống | Thêm quy tắc: không hứa điều hệ thống chưa làm. Phần số tiền thuộc FM-08, giao cho code |
| 7 | H-094 "Da, LogiX da hoan 40.000đ…" | PASS | FAIL | Người: mất dấu tiếng Việt (dịch máy) | Thêm quy tắc: bắt buộc có dấu tiếng Việt |
| 8 | H-088 "Dạ, dạ, LogiX đã hoàn…" | FAIL | PASS | Chưa rõ: lỗi gõ lặp từ, người cho qua | Rubric: lỗi lặp từ không đủ để FAIL nếu nội dung đúng; cần người thứ hai xác nhận |

## Kết luận
- **helpful bị loại** vì recall 0.30 và κ 0.375: judge bỏ sót 21 trong 30 reply bị người gán FAIL. 18 ca là "sai tiền" (ví dụ HL-015 nói 55.000đ trong khi ledger ghi 40.000đ) vì judge không nhìn thấy ledger; 3 ca là sai xưng hô ("Ok bạn… nhé"). Judge còn bị thuyết phục bởi câu xin lỗi lặp dài (HL-016, HL-028 đều PASS dù sai tiền). Precision 1.000 chỉ có nghĩa judge hiếm khi báo nhầm, không bù được việc bỏ sót.
- Lỗi "sai tiền" không giao cho judge: chuyển sang grader code `ReplyMatchesLedger` (FM-08), đối chiếu số trong reply với ledger.
- **tone_ok dùng được** làm tín hiệu theo dõi (đạt cả ba ngưỡng), nhưng không dùng để quyết định tiền hay approval. Khi báo tỉ lệ lỗi, dùng số đã hiệu chỉnh Rogan-Gladen.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật. Nhãn người cũng có thể sai (ca H-081), nên cần người thứ hai xác nhận các ca bất đồng.
