#!/usr/bin/env python3
"""仕訳AIの評価スクリプト（標準ライブラリのみ）

正解CSVとAI出力CSVを突き合わせて、03章で定義した指標を出します。

使い方:
    python evaluate.py --truth sample/ground_truth.csv --pred sample/predictions.csv
    python evaluate.py --truth ... --pred ... --errors errors.csv   # 誤った行をCSVに書き出す

正解CSVの列:
    doc_id, line_no, segment, account, sub_account, department, tax_category, amount,
    acceptable_accounts（任意。どちらでも正解とする科目を ; 区切り）
AI出力CSVの列:
    doc_id, line_no, account, sub_account, department, tax_category, amount,
    needs_review（true/false。true の行は「要確認」として人に回す）

誤りの重さ（03章 3-3）:
    致命的 = 税区分・金額の誤り、明細の取り漏れ
    重大   = 勘定科目の誤り
    軽微   = 部門・補助科目の誤り
"""

import argparse
import csv
import math
from collections import Counter, defaultdict

FIELDS = ["account", "sub_account", "department", "tax_category", "amount"]
FIELD_LABELS = {
    "account": "勘定科目",
    "sub_account": "補助科目",
    "department": "部門",
    "tax_category": "税区分",
    "amount": "金額",
}
CRITICAL_FIELDS = {"tax_category", "amount"}
MAJOR_FIELDS = {"account"}


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def key(row):
    return (row["doc_id"].strip(), int(row["line_no"]))


def norm(value):
    return (value or "").strip()


def to_amount(value):
    value = norm(value).replace(",", "")
    if value == "":
        return None
    return round(float(value))


def is_true(value):
    return norm(value).lower() in {"true", "1", "yes", "y", "要確認"}


def field_correct(field, truth, pred):
    if pred is None:
        return False
    if field == "amount":
        return to_amount(truth["amount"]) == to_amount(pred.get("amount"))
    if field == "account":
        accepted = {norm(truth["account"])}
        accepted |= {norm(a) for a in norm(truth.get("acceptable_accounts")).split(";") if norm(a)}
        return norm(pred.get("account")) in accepted
    return norm(truth.get(field)) == norm(pred.get(field))


def severity(wrong_fields, missing):
    if missing or wrong_fields & CRITICAL_FIELDS:
        return "致命的"
    if wrong_fields & MAJOR_FIELDS:
        return "重大"
    if wrong_fields:
        return "軽微"
    return ""


def pct(num, den):
    return f"{num / den * 100:5.1f}%" if den else "   - "


def ci95(num, den):
    """正解率の95%信頼区間の半幅（正規近似）。件数が少ないときの目安用。"""
    if not den:
        return ""
    p = num / den
    return f"±{1.96 * math.sqrt(p * (1 - p) / den) * 100:.1f}pt"


def evaluate(truth_rows, pred_rows):
    preds = {}
    for row in pred_rows:
        preds[key(row)] = row
    truth_keys = {key(r) for r in truth_rows}
    extra = sorted(k for k in preds if k not in truth_keys)

    results = []
    for t in truth_rows:
        p = preds.get(key(t))
        missing = p is None
        wrong = {f for f in FIELDS if not field_correct(f, t, p)}
        results.append({
            "doc_id": t["doc_id"].strip(),
            "line_no": int(t["line_no"]),
            "segment": norm(t.get("segment")) or "(なし)",
            "truth": t,
            "pred": p,
            "missing": missing,
            # 取り漏れは人が気付けないので「回答した（自動で通った）」扱いにする
            "answered": missing or not is_true(p.get("needs_review")),
            "wrong": wrong,
            "exact": not wrong,
            "severity": severity(wrong, missing),
        })
    return results, extra


def summarize(results):
    n = len(results)
    answered = [r for r in results if r["answered"]]
    a = len(answered)
    exact_all = sum(r["exact"] for r in results)
    exact_ans = sum(r["exact"] for r in answered)
    critical_ans = sum(r["severity"] == "致命的" for r in answered)

    docs = defaultdict(list)
    for r in results:
        docs[r["doc_id"]].append(r)
    doc_exact = sum(all(r["exact"] for r in rs) for rs in docs.values())
    doc_auto = sum(all(r["exact"] and r["answered"] for r in rs) for rs in docs.values())

    return {
        "lines": n,
        "docs": len(docs),
        "missing": sum(r["missing"] for r in results),
        "field_acc": {f: sum(f not in r["wrong"] for r in results) for f in FIELDS},
        "exact_all": exact_all,
        "answered": a,
        "exact_ans": exact_ans,
        "critical_ans": critical_ans,
        "doc_exact": doc_exact,
        "doc_auto": doc_auto,
    }


def print_summary(title, s):
    n, a = s["lines"], s["answered"]
    print(f"\n## {title}（{s['docs']}証憑 / {n}行）")
    print(f"  明細の取り漏れ                 : {s['missing']}行")
    for f in FIELDS:
        print(f"  項目別正解率 {FIELD_LABELS[f]:<6}        : {pct(s['field_acc'][f], n)}")
    print(f"  行の完全一致率（全行）         : {pct(s['exact_all'], n)} {ci95(s['exact_all'], n)}")
    print(f"  証憑単位の完全一致率           : {pct(s['doc_exact'], s['docs'])}")
    print(f"  カバレッジ（要確認以外の割合） : {pct(a, n)}")
    print(f"  回答した行の完全一致率         : {pct(s['exact_ans'], a)} {ci95(s['exact_ans'], a)}")
    print(f"  回答した行の致命的誤り率       : {pct(s['critical_ans'], a)}")
    print(f"  証憑まるごと自動で正解の割合   : {pct(s['doc_auto'], s['docs'])}")


def print_segment_table(results):
    by_seg = defaultdict(list)
    for r in results:
        by_seg[r["segment"]].append(r)
    print("\n## 型（segment）別")
    print("| 型 | 行数 | 完全一致率 | カバレッジ | 回答分の一致率 | 回答分の致命的誤り率 |")
    print("|---|---|---|---|---|---|")
    for seg in sorted(by_seg):
        s = summarize(by_seg[seg])
        print(f"| {seg} | {s['lines']} | {pct(s['exact_all'], s['lines']).strip()} "
              f"| {pct(s['answered'], s['lines']).strip()} "
              f"| {pct(s['exact_ans'], s['answered']).strip()} "
              f"| {pct(s['critical_ans'], s['answered']).strip()} |")
    small = [seg for seg, rs in by_seg.items() if len(rs) < 30]
    if small:
        print(f"\n  ※ 30行未満の型は誤差が大きいので参考値: {', '.join(sorted(small))}")


def print_confusions(results, field, top=5):
    pairs = Counter()
    for r in results:
        if r["pred"] is not None and field in r["wrong"]:
            pairs[(norm(r["truth"].get(field)), norm(r["pred"].get(field)))] += 1
    if not pairs:
        return
    print(f"\n## よくある取り違え：{FIELD_LABELS[field]}（正解 → AI出力）")
    for (t, p), c in pairs.most_common(top):
        print(f"  {c:3d}件  {t} → {p}")


def print_severity(results):
    counts = Counter(r["severity"] for r in results if r["severity"])
    review = Counter(r["severity"] for r in results if r["severity"] and not r["answered"])
    print("\n## 誤りの重さ別（カッコ内は要確認に回せていた件数）")
    for sev in ["致命的", "重大", "軽微"]:
        print(f"  {sev}: {counts.get(sev, 0)}行（{review.get(sev, 0)}）")


def write_errors(path, results):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["doc_id", "line_no", "segment", "重さ", "要確認にしたか", "誤った項目", "正解", "AIの出力",
                    "原因の部品", "誤りパターン", "対策の案"])
        for r in results:
            if r["exact"]:
                continue
            fields = [f for f in FIELDS if f in r["wrong"]]
            truth = " / ".join(norm(r["truth"].get(f)) for f in fields)
            pred = "（取り漏れ）" if r["missing"] else " / ".join(norm(r["pred"].get(f)) for f in fields)
            w.writerow([r["doc_id"], r["line_no"], r["segment"], r["severity"],
                        "いいえ" if r["answered"] else "はい",
                        " / ".join(FIELD_LABELS[f] for f in fields), truth, pred, "", "", ""])


def main():
    parser = argparse.ArgumentParser(description="仕訳AIの評価スクリプト")
    parser.add_argument("--truth", required=True, help="正解CSV")
    parser.add_argument("--pred", required=True, help="AI出力CSV")
    parser.add_argument("--errors", help="誤った行を書き出すCSV（エラー分析シートの下書き）")
    args = parser.parse_args()

    results, extra = evaluate(read_csv(args.truth), read_csv(args.pred))
    print("# 仕訳AI 評価結果")
    print_summary("全体", summarize(results))
    print_segment_table(results)
    print_severity(results)
    for field in ["account", "tax_category", "department"]:
        print_confusions(results, field)
    if extra:
        print(f"\n## 正解にない行をAIが出力（余計な行）: {len(extra)}行")
        for doc_id, line_no in extra[:10]:
            print(f"  {doc_id} 行{line_no}")
    if args.errors:
        write_errors(args.errors, results)
        print(f"\n誤った行を {args.errors} に書き出しました（エラー分析シートの下書きとして使えます）")


if __name__ == "__main__":
    main()
