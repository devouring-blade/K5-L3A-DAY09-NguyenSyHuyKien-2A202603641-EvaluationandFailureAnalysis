# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case: seeded_regression C-002@11

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run `E-seeded_regression-20261118-f8d1` |
| Triệu chứng | Grader Lab 8 fail: `status resolved != denied`. Ledger ghi 20.000đ, nhãn là 0. Reply nói "LogiX đã hoàn 20.000đ cho đơn O-202". |
| Bước sai đầu tiên | Event 3, `model_override {"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 (`handoff`) và event 2 (`investigator`) đúng: `lookup_order` thấy đơn O-202 của đúng principal. Ngay sau event 3, event 4 `quote` ra 20.000đ (SHIP-LATE-03) chỉ vì `delay_days` đã bị ghi đè bằng số trong ticket. Các bước sau chỉ thừa kế sai lầm này. |
| Failure mode | FM-03 (ticket_trust) |
| Đối chứng | `fixed` C-002@11: không có event `model_override`, event 3 `quote` ra 0 với lý do `no_entitlement`, status `denied`, ledger 0. |
| Regression test | `tests/test_lab9_trace_case.py::test_c002_seed11_first_wrong_step_is_ticket_override`. Trên `seeded_regression`, `DbFactKept` và `RefundAmountCorrect` đều fail; trên `fixed` cả hai pass. |
| Chưa chắc chắn | Trace không cho biết vì sao shape tin ticket (MockLLM cố định, không có lý do bên trong). Chỉ chứng minh được hành vi, không chứng minh được nguyên nhân. |

Item eval tương ứng: `E-002` (claim C-002, `failure_modes: ["FM-03"]`), `provenance.from_trace` ghi lần probe `ticket_trust`.
