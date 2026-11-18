#!/usr/bin/env bash
set -u; . "$TASK_DIR/../_lib.sh"
dups=$(grep -rEn 'def _?fmt_(money|pct)' reports | wc -l)
[ "$dups" -le 2 ] || { echo "helpers still duplicated ($dups definitions)"; exit 1; }
[ -f reports/fmt.py ] || { echo "reports/fmt.py missing"; exit 1; }
grep -q 'fmt_money' reports/fmt.py && grep -q 'fmt_pct' reports/fmt.py || { echo "fmt.py lacks helpers"; exit 1; }
for m in csv_report text_report html_report; do
  grep -q 'fmt' reports/$m.py && ! grep -Eq 'def _?fmt_(money|pct)' reports/$m.py \
    || { echo "$m still defines its own helper"; exit 1; }
done
install_hidden
run_pytest tests
