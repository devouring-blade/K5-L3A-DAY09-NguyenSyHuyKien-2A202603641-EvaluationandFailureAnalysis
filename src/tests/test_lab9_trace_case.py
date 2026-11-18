"""Regression tests from trace cases (docs/trace_case.md) and the FM-08 grader (M1, M3)."""
import pytest

pytestmark = pytest.mark.student
LABEL = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}


def ctx(trial, label=LABEL):
    from pydantic_evals.evaluators import EvaluatorContext

    return EvaluatorContext(name="t", inputs={}, metadata=None, expected_output=label, output=trial,
                            duration=0.0, _span_tree=None, attributes={}, metrics={})


def trial(ledger, reply_text=None, events=()):
    ev = list(events)
    if reply_text is not None:
        ev.append({"kind": "reply", "payload": {"text": reply_text}})
    return {"snapshot": {"refund_vnd": ledger, "refund_count": int(ledger > 0)}, "unexpected_rows": 0,
            "blob": "", "events": ev, "result": {}, "lab8_pass": True, "lab8_reason": None}


def test_reply_matching_ledger_passes():
    from lab9 import graders

    t = ctx(trial(20000, "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."))
    assert graders.ReplyMatchesLedger().evaluate(t).value is True


def test_reply_stating_proposal_instead_of_ledger_fails():
    from lab9 import graders

    out = graders.ReplyMatchesLedger().evaluate(ctx(trial(20000, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.")))
    assert out.value is False and "35000" in out.reason


def test_reply_claiming_refund_when_ledger_empty_fails():
    from lab9 import graders

    t = ctx(trial(0, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-909."), {**LABEL, "refund_vnd": 0})
    assert graders.ReplyMatchesLedger().evaluate(t).value is False


def test_reply_without_amount_is_not_judged():
    from lab9 import graders

    t = ctx(trial(0, "Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."), {**LABEL, "refund_vnd": 0})
    assert graders.ReplyMatchesLedger().evaluate(t).value is True


def test_c002_seed11_first_wrong_step_is_ticket_override():
    """Trace case: seeded_regression trusts the ticket's '5 ngày' (event model_override) and pays 20.000đ."""
    from lab9 import graders
    from lab9.trace_case import investigate

    bad = investigate("seeded_regression", "C-002", 11)
    t = ctx(bad["trial"], bad["label"])
    kinds = [e["kind"] for e in bad["trial"]["events"]]
    assert "model_override" in kinds
    assert graders.DbFactKept().evaluate(t).value is False
    assert graders.RefundAmountCorrect().evaluate(t).value is False

    good = investigate("fixed", "C-002", 11)
    g = ctx(good["trial"], good["label"])
    assert graders.DbFactKept().evaluate(g).value is True
    assert graders.RefundAmountCorrect().evaluate(g).value is True


def test_proposal_amount_is_checked_against_the_label_not_the_ledger():
    from lab9 import graders

    ok = trial(0); ok["result"] = {"proposal_amount": 35000}
    netted = trial(0); netted["result"] = {"proposal_amount": 0}
    label = {**LABEL, "refund_vnd": 0, "proposal_amount": 35000}
    assert graders.ProposalAmountCorrect().evaluate(ctx(ok, label)).value is True
    assert graders.ProposalAmountCorrect().evaluate(ctx(netted, label)).value is False
