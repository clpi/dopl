#!/bin/bash
# Ado vs C Benchmark Suite
# Runs equivalent programs in both Ado and C, comparing results and timing.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC="$(dirname "$SCRIPT_DIR")/doc"

BENCHMARKS=("fib" "prime" "collatz")
ADO_TOTAL=0
C_TOTAL=0
PASS=0
FAIL=0

if [ ! -f "$DOC" ]; then
    echo "Error: Ado compiler not found. Run 'make' first." >&2
    exit 1
fi

echo "=========================================="
echo "  Ado vs C Benchmark Suite"
echo "=========================================="
echo ""

echo "Building C benchmarks..."
for name in "${BENCHMARKS[@]}"; do
    cc -O2 -o "$SCRIPT_DIR/$name.c.bin" "$SCRIPT_DIR/$name.c"
done
echo "done."
echo ""

printf "%-12s %-22s %-22s %s\n" "Benchmark" "Ado" "C" "Ratio"
printf "%-12s %-22s %-22s %s\n" "---------" "---" "-" "-----"

for name in "${BENCHMARKS[@]}"; do
    ado_file="$SCRIPT_DIR/$name.do"
    c_bin="$SCRIPT_DIR/$name.c.bin"

    ado_t1=$(python3 -c "import time; print(time.time())")
    ado_output=$("$DOC" "$ado_file" 2>/dev/null)
    ado_rc=$?
    ado_t2=$(python3 -c "import time; print(time.time())")

    c_t1=$(python3 -c "import time; print(time.time())")
    c_output=$("$c_bin" 2>/dev/null)
    c_rc=$?
    c_t2=$(python3 -c "import time; print(time.time())")

    ado_time=$(python3 -c "print($ado_t2 - $ado_t1)")
    c_time=$(python3 -c "print($c_t2 - $c_t1)")

    ado_result=$(echo "$ado_output" | grep -oE '[0-9]+$' | tail -1)
    [ -z "$ado_result" ] && ado_result="$ado_rc"

    c_result=$(echo "$c_output" | grep -oE '[0-9]+$' | tail -1)
    [ -z "$c_result" ] && c_result="$c_rc"

    if [ "$ado_result" = "$c_result" ]; then
        status="PASS"
        PASS=$((PASS + 1))
    else
        status="FAIL (Ado=$ado_result C=$c_result)"
        FAIL=$((FAIL + 1))
    fi

    ratio=$(python3 -c "print('%.2fx' % ($ado_time / $c_time))")

    printf "%-12s %-22s %-22s %s\n" \
        "$name" \
        "$(printf '%.4fs' "$ado_time")" \
        "$(printf '%.4fs' "$c_time")" \
        "$ratio  $status"

    ADO_TOTAL=$(python3 -c "print($ADO_TOTAL + $ado_time)")
    C_TOTAL=$(python3 -c "print($C_TOTAL + $c_time)")
done

echo ""
echo "=========================================="
total_ratio=$(python3 -c "print('%.2fx' % ($ADO_TOTAL / $C_TOTAL))")
printf "%-12s %-22s %-22s %s\n" "TOTAL" \
    "$(printf '%.4fs' "$ADO_TOTAL")" \
    "$(printf '%.4fs' "$C_TOTAL")" \
    "$total_ratio"
echo "=========================================="

for name in "${BENCHMARKS[@]}"; do
    rm -f "$SCRIPT_DIR/$name.c.bin"
done

if [ "$FAIL" -gt 0 ]; then
    echo "FAILED: $FAIL benchmarks produced wrong results"
    exit 1
fi
echo "All benchmarks passed!"
exit 0
