#!/usr/bin/env python3
"""AI出力の評価スクリプト（抽出・分類タスク向け、標準ライブラリのみ）

正解CSVとAI出力CSVを突き合わせて、03章で定義した指標を出します。
業務ごとの違い（列名、誤りの重さ、まとまりの単位）は設定ファイル（JSON）で指定します。

使い方:
    python evaluate.py --config sample/journal/config.json \\
        --truth sample/journal/ground_truth.csv --pred sample/journal/predictions.csv \\
        --errors errors.csv

設定ファイルの例（sample/journal/config.json）:
    {
      "name": "仕訳入力",
      "keys": ["doc_id", "line_no"],         # 1行を特定する列（正解とAI出力で共通）
      "group_by": "doc_id",                  # まとまりの単位（書類など）。省略可
      "segment": "segment",                  # 型別に集計する列（正解CSV側）。省略可
      "review_column": "needs_review",       # AIが「要確認」にしたかの列（AI出力側）。省略可
      "missing_severity": "致命的",           # AIが出力しなかった行の重さ
      "fields": {
        "account": {"label": "勘定科目", "severity": "重大"},
        "amount":  {"label": "金額", "severity": "致命的", "type": "number"}
      }
    }

正解CSVに "acceptable_<項目名>" 列があれば、そこに ; 区切りで書いた値も正解として扱います。
"""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict

SEVERITIES = ["致命的", "重大", "軽微"]


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def norm(value):
    return (value or "").strip()


def to_number(value):
    value = norm(value).replace(",", "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return value


def is_true(value):
    return norm(value).lower() in {"true", "1", "yes", "y", "要確認"}


def pct(num, den):
    return f"{num / den * 100:5.1f}%" if den else "   - "


def ci95(num, den):
    """正解率の95%信頼区間の半幅（正規近似）。件数が少ないときの目安用。"""
    if not den:
        return ""
    p = num / den
    return f"±{1.96 * math.sqrt(p * (1 - p) / den) * 100:.1f}pt"


class Evaluator:
    def __init__(self, config):
        self.name = config.get("name", "")
        self.keys = config["keys"]
        self.group_by = config.get("group_by")
        self.segment = config.get("segment")
        self.review_column = config.get("review_column")
        self.missing_severity = config.get("missing_severity", "致命的")
        self.fields = config["fields"]
        for name, spec in self.fields.items():
            if spec.get("severity", "軽微") not in SEVERITIES:
                raise ValueError(f"{name} の severity は {SEVERITIES} のいずれかにしてください")

    def label(self, field):
        return self.fields[field].get("label", field)

    def key(self, row):
        return tuple(norm(row.get(k)) for k in self.keys)

    def field_correct(self, field, truth, pred):
        if pred is None:
            return False
        if self.fields[field].get("type") == "number":
            return to_number(truth.get(field)) == to_number(pred.get(field))
        accepted = {norm(truth.get(field))}
        accepted |= {norm(v) for v in norm(truth.get(f"acceptable_{field}")).split(";") if norm(v)}
        return norm(pred.get(field)) in accepted

    def severity(self, wrong, missing):
        found = {self.missing_severity} if missing else set()
        found |= {self.fields[f].get("severity", "軽微") for f in wrong}
        for sev in SEVERITIES:
            if sev in found:
                return sev
        return ""

    def evaluate(self, truth_rows, pred_rows):
        preds = {self.key(r): r for r in pred_rows}
        truth_keys = {self.key(r) for r in truth_rows}
        extra = sorted(k for k in preds if k not in truth_keys)
        results = []
        for t in truth_rows:
            p = preds.get(self.key(t))
            missing = p is None
            wrong = {f for f in self.fields if not self.field_correct(f, t, p)}
            needs_review = bool(p and self.review_column and is_true(p.get(self.review_column)))
            results.append({
                "key": self.key(t),
                "group": norm(t.get(self.group_by)) if self.group_by else None,
                "segment": (norm(t.get(self.segment)) if self.segment else "") or "(なし)",
                "truth": t,
                "pred": p,
                "missing": missing,
                # 出力しなかった行は人が気付けないので「回答した（自動で通った）」扱いにする
                "answered": not needs_review,
                "wrong": wrong,
                "exact": not wrong,
                "severity": self.severity(wrong, missing),
            })
        return results, extra

    def summarize(self, results):
        answered = [r for r in results if r["answered"]]
        s = {
            "n": len(results),
            "missing": sum(r["missing"] for r in results),
            "field_ok": {f: sum(f not in r["wrong"] for r in results) for f in self.fields},
            "exact": sum(r["exact"] for r in results),
            "answered": len(answered),
            "exact_ans": sum(r["exact"] for r in answered),
            "critical_ans": sum(r["severity"] == "致命的" for r in answered),
        }
        if self.group_by:
            groups = defaultdict(list)
            for r in results:
                groups[r["group"]].append(r)
            s["groups"] = len(groups)
            s["group_exact"] = sum(all(r["exact"] for r in rs) for rs in groups.values())
            s["group_auto"] = sum(all(r["exact"] and r["answered"] for r in rs) for rs in groups.values())
        return s

    def print_summary(self, s):
        n, a = s["n"], s["answered"]
        unit = f"{s['groups']}まとまり（{self.group_by}単位） / " if self.group_by else ""
        print(f"\n## 全体（{unit}{n}行）")
        print(f"  AIが出力しなかった行（取り漏れ）   : {s['missing']}行")
        for f in self.fields:
            print(f"  項目別正解率 {pct(s['field_ok'][f], n)} : {self.label(f)}")
        print(f"  完全一致率（全行）                 : {pct(s['exact'], n)} {ci95(s['exact'], n)}")
        if self.group_by:
            print(f"  まとまり単位の完全一致率           : {pct(s['group_exact'], s['groups'])}")
        if self.review_column:
            print(f"  カバレッジ（要確認にしなかった割合）: {pct(a, n)}")
            print(f"  回答した行の完全一致率             : {pct(s['exact_ans'], a)} {ci95(s['exact_ans'], a)}")
        print(f"  回答した行の致命的誤り率           : {pct(s['critical_ans'], a)}")
        if self.group_by and self.review_column:
            print(f"  まとまりごと自動で正解の割合       : {pct(s['group_auto'], s['groups'])}")

    def print_segments(self, results):
        if not self.segment:
            return
        by_seg = defaultdict(list)
        for r in results:
            by_seg[r["segment"]].append(r)
        print("\n## 型（segment）別")
        print("| 型 | 行数 | 完全一致率 | カバレッジ | 回答分の一致率 | 回答分の致命的誤り率 |")
        print("|---|---|---|---|---|---|")
        for seg in sorted(by_seg):
            s = self.summarize(by_seg[seg])
            print(f"| {seg} | {s['n']} | {pct(s['exact'], s['n']).strip()} "
                  f"| {pct(s['answered'], s['n']).strip()} "
                  f"| {pct(s['exact_ans'], s['answered']).strip()} "
                  f"| {pct(s['critical_ans'], s['answered']).strip()} |")
        small = sorted(seg for seg, rs in by_seg.items() if len(rs) < 30)
        if small:
            print(f"\n  ※ 30行未満の型は誤差が大きいので参考値: {', '.join(small)}")

    def print_severity(self, results):
        counts = Counter(r["severity"] for r in results if r["severity"])
        review = Counter(r["severity"] for r in results if r["severity"] and not r["answered"])
        print("\n## 誤りの重さ別（カッコ内は要確認に回せていた件数）")
        for sev in SEVERITIES:
            print(f"  {sev}: {counts.get(sev, 0)}行（{review.get(sev, 0)}）")

    def print_confusions(self, results, top=5):
        for field in self.fields:
            if self.fields[field].get("type") == "number":
                continue
            pairs = Counter()
            for r in results:
                if r["pred"] is not None and field in r["wrong"]:
                    pairs[(norm(r["truth"].get(field)), norm(r["pred"].get(field)))] += 1
            if pairs:
                print(f"\n## よくある取り違え：{self.label(field)}（正解 → AI出力）")
                for (t, p), c in pairs.most_common(top):
                    print(f"  {c:3d}件  {t or '(空)'} → {p or '(空)'}")

    def write_errors(self, path, results):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(self.keys + ["segment", "重さ", "要確認にしたか", "誤った項目", "正解", "AIの出力",
                                    "原因の部品", "誤りパターン", "対策の案"])
            for r in results:
                if r["exact"]:
                    continue
                fields = [f for f in self.fields if f in r["wrong"]]
                truth = " / ".join(norm(r["truth"].get(f)) for f in fields)
                pred = "（出力なし）" if r["missing"] else " / ".join(norm(r["pred"].get(f)) for f in fields)
                w.writerow(list(r["key"]) + [r["segment"], r["severity"],
                                             "いいえ" if r["answered"] else "はい",
                                             " / ".join(self.label(f) for f in fields), truth, pred, "", "", ""])


def main():
    parser = argparse.ArgumentParser(description="AI出力の評価スクリプト（抽出・分類タスク向け）")
    parser.add_argument("--config", required=True, help="設定ファイル（JSON）")
    parser.add_argument("--truth", required=True, help="正解CSV")
    parser.add_argument("--pred", required=True, help="AI出力CSV")
    parser.add_argument("--errors", help="誤った行を書き出すCSV（エラー分析シートの下書き）")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        ev = Evaluator(json.load(f))
    results, extra = ev.evaluate(read_csv(args.truth), read_csv(args.pred))

    print(f"# 評価結果：{ev.name}")
    ev.print_summary(ev.summarize(results))
    ev.print_segments(results)
    ev.print_severity(results)
    ev.print_confusions(results)
    if extra:
        print(f"\n## 正解にない行をAIが出力（余計な行）: {len(extra)}行")
        for k in extra[:10]:
            print(f"  {' / '.join(k)}")
    if args.errors:
        ev.write_errors(args.errors, results)
        print(f"\n誤った行を {args.errors} に書き出しました（エラー分析シートの下書きとして使えます）")


if __name__ == "__main__":
    main()
