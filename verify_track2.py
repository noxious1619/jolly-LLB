"""
Lightweight standalone verification — no LangChain, no API keys, no FAISS.
Tests only logic.eligibility_engine to prove the deterministic engine works.
Output is written to verify_results.txt.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic.eligibility_engine import verify_eligibility

results = []
PASS = "PASS"
FAIL = "FAIL"

def check(label, got_ok, got_reason, expect_ok, expect_text_in_reason=""):
    status = PASS if (got_ok == expect_ok and (expect_text_in_reason.lower() in got_reason.lower() if expect_text_in_reason else True)) else FAIL
    results.append(f"[{status}] {label}: ok={got_ok}, reason='{got_reason}'")
    return status == PASS

# ── scheme_001 tests ──────────────────────────────────────────────────────────
ok1, r1 = verify_eligibility({"age":12,"income":80000,"community":"Muslim"}, "scheme_001")
check("001-eligible-basic", ok1, r1, True)

ok2, r2 = verify_eligibility({"age":12,"income":200000,"community":"Muslim"}, "scheme_001")
check("001-income-too-high", ok2, r2, False, "income")

ok3, r3 = verify_eligibility({"age":18,"income":80000,"community":"Muslim"}, "scheme_001")
check("001-age-too-high", ok3, r3, False, "age")

ok4, r4 = verify_eligibility({"age":12,"income":80000,"community":"Hindu"}, "scheme_001")
check("001-wrong-community", ok4, r4, False, "community")

ok5, r5 = verify_eligibility({"age":12,"income":80000,"community":"buddhist"}, "scheme_001")
check("001-community-case-insensitive", ok5, r5, True)

# ── scheme_002 tests ──────────────────────────────────────────────────────────
ok6, r6 = verify_eligibility({"age":40,"is_farmer":True,"occupation":"farmer"}, "scheme_002")
check("002-eligible-farmer", ok6, r6, True)

ok7, r7 = verify_eligibility({"age":40,"is_farmer":False}, "scheme_002")
check("002-not-a-farmer", ok7, r7, False, "farmer")

ok8, r8 = verify_eligibility({"age":40,"is_farmer":True,"occupation":"income_tax_payer"}, "scheme_002")
check("002-excluded-occupation", ok8, r8, False, "excluded")

ok9, r9 = verify_eligibility({"age":16,"is_farmer":True}, "scheme_002")
check("002-underage", ok9, r9, False, "age")

# ── scheme_003 tests ──────────────────────────────────────────────────────────
ok10, r10 = verify_eligibility({"age":28,"dpiit_recognised":True,"startup_age_years":1.5,"prior_govt_funding_inr":500000}, "scheme_003")
check("003-eligible-startup", ok10, r10, True)

ok11, r11 = verify_eligibility({"age":28,"dpiit_recognised":False,"startup_age_years":1}, "scheme_003")
check("003-no-dpiit", ok11, r11, False, "DPIIT")

ok12, r12 = verify_eligibility({"age":28,"dpiit_recognised":True,"startup_age_years":3}, "scheme_003")
check("003-startup-too-old", ok12, r12, False, "year")

ok13, r13 = verify_eligibility({"age":28,"dpiit_recognised":True,"startup_age_years":1,"prior_govt_funding_inr":2000000}, "scheme_003")
check("003-over-funded", ok13, r13, False, "funding")

# ── scheme_007 tests ──────────────────────────────────────────────────────────
ok14, r14 = verify_eligibility({"age":22}, "scheme_007")
check("007-eligible-youth", ok14, r14, True)

ok15, r15 = verify_eligibility({"age":46}, "scheme_007")
check("007-too-old", ok15, r15, False, "age")

# ── scheme_008 tests ──────────────────────────────────────────────────────────
ok16, r16 = verify_eligibility({"age":65,"is_bpl":True}, "scheme_008")
check("008-eligible-senior", ok16, r16, True)

ok17, r17 = verify_eligibility({"age":59,"is_bpl":True}, "scheme_008")
check("008-too-young", ok17, r17, False, "age")

ok18, r18 = verify_eligibility({"age":65,"is_bpl":False}, "scheme_008")
check("008-not-bpl", ok18, r18, False, "BPL")

# ── scheme_010 tests ──────────────────────────────────────────────────────────
ok19, r19 = verify_eligibility({"age":19,"income":200000,"community":"SC"}, "scheme_010")
check("010-eligible-sc", ok19, r19, True)

ok20, r20 = verify_eligibility({"age":19,"income":300000,"community":"Scheduled Caste"}, "scheme_010")
check("010-income-too-high", ok20, r20, False, "income")

# ── unknown policy ────────────────────────────────────────────────────────────
ok21, r21 = verify_eligibility({"age":25,"income":50000}, "scheme_999")
check("unknown-policy", ok21, r21, False, "not found")

# ── income as string ─────────────────────────────────────────────────────────
ok22, r22 = verify_eligibility({"age":12,"income":"80000","community":"Christian"}, "scheme_001")
check("income-as-string", ok22, r22, True)

passed = sum(1 for r in results if r.startswith("[PASS]"))
failed = sum(1 for r in results if r.startswith("[FAIL]"))

with open("verify_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
    f.write(f"\n\n{'='*50}\n")
    f.write(f"TOTAL: {len(results)} tests — {passed} PASSED, {failed} FAILED\n")
    if failed == 0:
        f.write("✅ ALL TESTS PASSED — Eligibility Engine is working correctly!\n")
    else:
        f.write("❌ SOME TESTS FAILED — See above for details.\n")

print(f"Done. {passed}/{len(results)} passed. See verify_results.txt")
