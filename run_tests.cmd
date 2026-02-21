@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM  JOLLY-LLB — Unified Test Runner
REM  Run all tests that don't require API keys or a live FAISS index.
REM
REM  Usage:  run_tests.cmd
REM ─────────────────────────────────────────────────────────────────────────────

echo.
echo ============================================================
echo   JOLLY-LLB — Running All Offline Tests
echo ============================================================

echo.
echo [1/3] Track-2 Eligibility Engine (22 deterministic unit tests)
echo ----------------------------------------------------------------
venv\Scripts\python verify_track2.py
if errorlevel 1 goto :fail

echo.
echo [2/3] Integration Tests (9 mocked pipeline tests)
echo ----------------------------------------------------------------
venv\Scripts\python -m pytest test_integration.py -v
if errorlevel 1 goto :fail

echo.
echo [3/3] Track-2 Dedicated Test Suite (tests/ folder)
echo ----------------------------------------------------------------
venv\Scripts\python -m pytest tests/test_eligibility.py tests/test_next_best_action.py -v
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   ALL TESTS PASSED
echo ============================================================
goto :end

:fail
echo.
echo ============================================================
echo   SOME TESTS FAILED — See output above
echo ============================================================
exit /b 1

:end
