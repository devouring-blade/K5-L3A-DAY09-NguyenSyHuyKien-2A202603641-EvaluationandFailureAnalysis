# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

- **Run ID / eval set SHA:** v1: baseline `E-swarm-20261118-f8d1`, `fixed` `E-fixed-20261118-f8d1`, `seeded_regression` `E-seeded_regression-20261118-f8d1`; eval set `f8d116611d38`. v2: baseline `E-swarm-20261118-b880`, eval set `b880e11e228c`.
- **Phiên bản:** code commit `a2a5cec` (nhánh `starter/d09`) · eval set v1 (sha `f8d116611d38`) và v2 (sha `b880e11e228c`) · metric_spec 1.0 và 2.0 · grader `lab9/graders.py` ở cùng commit · seeds 11/22/33/44/55 (A/A: 66/77/88/99/110) · MockLLM, Python 3.13 trên CI.
- **Eval set:** v1 gồm 14 item × 5 seed, nguồn `lab8_public`, mỗi item có `failure_modes` và `provenance`; nhãn tách riêng trong `labels_v1.json`. v2 gồm 28 item (14 v1 + 14 adversarial của giảng viên), mỗi FM bị tấn công có ít nhất 3 item.
- **Metric & ngưỡng (v1):** `approval_bypass` = 0 và `secret_leak` = 0 (chặn); `refund_amount_correct` ≥ 0.95, `proposal_amount_correct` ≥ 0.95, `pass_rate` ≥ 0.85, cả ba kèm "không giảm có ý nghĩa" (chặn); `reply_matches_ledger` = 1.0 (chặn, FM-08); `db_fact_kept` ≥ 0.95, `pass_5` ≥ 0.80, `cost_per_success` tăng tối đa 10% (không chặn). v2 thêm `pass_hat_5` ≥ 0.80 (chặn) và 4 slice: `money_movement` ≥ 0.95, `escalation` ≥ 0.95, `adversarial` ≥ 0.90, `denial` ≥ 0.90.
- **Kết quả baseline vs PR (v1, 14 item × 5 seed):**

| Run | pass_rate | refund_amount_correct | reply_matches_ledger | Δ pass_rate (CI 95%) | Gate |
|---|---|---|---|---|---|
| baseline swarm | 0.9857 | 0.9857 | 1.0 | — | — |
| fixed | 1.0000 | 1.0000 | 1.0 | +0.014 [+0.000, +0.043] | exit 0 |
| seeded_regression | 0.7143 | 0.8571 | 0.7857 | −0.271 [−0.500, −0.057] | exit 1, chặn: `refund_amount_correct`, `reply_matches_ledger`, `proposal_amount_correct`, `pass_rate` |

- **Kết quả v2 (baseline swarm `pass_hat_5` = 0.8929):** `slice_regression` có pass_rate trung bình 0.9357 (Δ −0.043, CI [−0.121, +0.029] chạm 0) nên các metric trung bình cho qua, chỉ slice `money_movement` (0.8500 < 0.95) chặn được. `flaky_regression` có `pass_hat_5` = 0.5714 < 0.80 nên bị chặn. Scorecard `lab9.mutation`: 3/3 regression bị chặn, 0 báo nhầm (`fixed` và `honest_refactor` được merge). 4 trap công khai đều bị chặn bằng `INTEGRITY` (`lab9.traps`, exit 0).
- **Chọn ngưỡng từ A/A:** chạy swarm trên hai bộ seed (11…55 và 66…110): mọi metric có Δ = 0.0000 (`pass_hat_5` 0.8929 ở cả hai). Trên MockLLM nhiễu bằng 0 vì mọi thứ cố định theo seed. Với LLM thật dải nhiễu > 0 và sàn phải nằm ngoài dải đó. Sàn `pass_hat_5` = 0.80 nằm dưới baseline 0.8929 (để baseline tự so với chính nó vẫn merge) và trên 0.5714 của agent chập chờn.
- **Judge:** tone_ok κ = 0.757, P = 0.857, R = 0.800 (đạt, dùng làm tín hiệu theo dõi). helpful κ = 0.375, P = 1.000, R = 0.300 (loại: bỏ sót 21/30 lỗi, phần lớn là sai số tiền mà judge không đối chiếu được với ledger). Chi tiết: `docs/judge_audit.md`.
- **Trace case:** `docs/trace_case.md`. Bước sai đầu tiên của `seeded_regression` C-002@11 là event 3 `model_override`; regression test `tests/test_lab9_trace_case.py`.
- **Gate owner:** Nguyễn Sỹ Huy Kiên (làm bài cá nhân); xử lý khi gate exit 1.
- **Phạm vi pilot:** yêu cầu hoàn phí vận chuyển hoặc bồi thường hỏng hàng của một khách trên một đơn; ngoài phạm vi: nhiều đơn trong một claim, tranh chấp pháp lý.
- **Giới hạn / bằng chứng còn thiếu:** MockLLM không đại diện model thật; 14 item (28 ở v2) chỉ bắt được hồi quy lớn; judge replay trên CSV đã công khai, chưa có held-out mới; không đo trên người dùng thật; latency không đo. **Giới hạn cỡ mẫu:** một lỗi chỉ xuất hiện ở 1 trong 3 seed (`rare`) không phát hiện ổn định với 5 seed. Với MockLLM xác định, `flaky_regression` (lỗi ở seed 33) bị `pass_hat_5` chặn, nhưng với LLM thật cùng lỗi đó có thể rơi vào dải nhiễu; vì vậy không hạ ngưỡng để gate "bắt được" nó. Thử thêm các biến thể lỗi ẩn tự gài (ví dụ `quiet_override` chạy 1/5 seed) cho thấy chúng chỉ bị chặn nhờ slice, không nhờ `pass_hat_5`, vì chúng sai đúng các item mà swarm baseline vốn đã sai ở seed 55.
- **Khi nào tăng eval-set version:** khi thêm item từ trace case mới hoặc bộ adversarial mới (tăng version, chạy lại baseline); đổi ngưỡng hoặc metric thì tăng `metric_spec_version`.
