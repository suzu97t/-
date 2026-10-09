#!/usr/bin/env python3
"""「死ぬほど疲れた」を本気で検証する — 計算スクリプト

解釈 A＋B（research.md 参照）:
  A. エネルギー破産：食べずに動き続け、体脂肪を使い切る
  B. 持続可能な代謝の上限：基礎代謝の約2.5倍（Thurber et al. 2019）
  F. つかみ：伝令ペイディッピデス

実行:  python3 calc.py
出力:  標準出力に結果、figures/*.png にグラフ
依存:  Python 3.9+, matplotlib
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace

# =============================================================================
# 設定値（ここだけ変えれば全体が再計算される）。出典の詳細は research.md
# =============================================================================

# --- モデル人物 ---
WEIGHT_KG = 65.0             # 体重
AGE = 35                     # 年齢（30〜49歳区分）
BODY_FAT_PCT = 20.0          # 体脂肪率 [%]
HEIGHT_CM = 170.0            # 身長（BMIによる致死ラインと Mifflin式の照合に使う。仮置き）

# --- 基礎代謝 ---
BMR_KCAL_PER_KG = 22.5       # 基礎代謝基準値 男性30〜49歳 [kcal/kg/日]（日本人の食事摂取基準2025年版）
PAL_NORMAL = 1.75            # 身体活動レベル「ふつう(II)」（同上）

# --- METs → kcal ---
MET_KCAL_FACTOR = 1.05       # kcal = 1.05 × METs × 時間 × 体重（厚労省「健康づくりのための身体活動基準2013」）
TEF_FRACTION = 0.10          # 食事誘発性熱産生：総消費の約10%（Westerterp 2004）。食べている日にだけ加える

# --- 体のエネルギー貯蔵 ---
FAT_KCAL_PER_KG = 39.5e3 / 4.184   # 体脂肪 39.5 MJ/kg（Hall らのモデル定数）≒ 9,441 kcal/kg
LEAN_KCAL_PER_KG = 7.6e3 / 4.184   # 除脂肪組織 7.6 MJ/kg（同上）≒ 1,816 kcal/kg
FORBES_C_KG = 10.4                 # Forbes 型の分配定数（Hall らのモデル）
ESSENTIAL_FAT_PCT = 3.0            # 必須脂肪：男性で体重の約3%（運動生理学の教科書値）
LETHAL_BMI = 13.0                  # 飢餓で男性はBMI約13が致死的（ENN Field Exchange 15 "The limits of human starvation"）
GLYCOGEN_G = 500.0                 # 肝臓約100g + 筋約400g
GLYCOGEN_KCAL_PER_G = 4.0

# --- 持続可能な上限（Thurber et al. 2019, Sci Adv） ---
SUSTAINABLE_SCOPE = 2.5            # 基礎代謝の約2.5倍
RAUSA_TEE_MJ = (22.39, 25.95)      # 大陸横断レース走者の総消費（Thurber 2016 修士論文）[MJ/日]

# --- 伝令（F） ---
RUN_NET_KCAL_PER_KG_KM = 1.0       # ランニングの正味コスト ≒ 1 kcal/kg/km（Margaria 1963）
ATHENS_SPARTA_KM = 240.0           # アテネ→スパルタ（現代の推定。ヘロドトスは距離を書いていない）
MARATHON_ATHENS_KM = 40.0          # マラトン→アテネ（伝説の「死んだ伝令」の距離、概数）
MARATHON_KM = 42.195

# --- 比較用の食べ物 ---
BANANA_KCAL = 93.0                 # バナナ 可食部100g（日本食品標準成分表2020年版（八訂））

# --- 1日の行動（時間[h], METs, Compendiumコード/根拠） ---
# 残り時間は REST_ACTIVITY で埋める
REST_ACTIVITY = ("帰宅後ソファで放心", 1.3, "07021 sitting quietly")

ACTIVITY_METS = {
    # 名前:            (METs, 出典)
    "睡眠":             (0.95, "07030 sleeping"),
    "身支度":           (2.5,  "13020 dressing, undressing"),
    "食事":             (1.5,  "13030 eating, sitting"),
    "通勤の徒歩":       (3.5,  "17200 walking 2.8-3.2 mph, level"),
    "駅の階段":         (4.0,  "17130 stair climbing, slow pace"),
    "満員電車で立つ":   (1.3,  "07040 standing quietly"),
    "デスクワーク":     (1.5,  "11580 sitting tasks, light (office work)"),
    "社内移動・立ち仕事": (2.8, "17152 walking 2.0 mph, slow"),
    "シャワー":         (2.0,  "推定：身の回り動作の低強度値"),
    "引越し作業":       (5.8,  "05120 moving household items, carrying boxes"),
}

DAYS = {
    "普段の日": {
        "睡眠": 7.0, "身支度": 0.5, "食事": 1.25, "通勤の徒歩": 0.5, "駅の階段": 0.1,
        "満員電車で立つ": 1.5, "デスクワーク": 7.5, "社内移動・立ち仕事": 1.0, "シャワー": 0.25,
    },
    "死ぬほど疲れた日": {   # 繁忙期。睡眠5時間、デスク10.5時間、終電帰り
        "睡眠": 5.0, "身支度": 0.5, "食事": 1.0, "通勤の徒歩": 0.5, "駅の階段": 0.1,
        "満員電車で立つ": 1.5, "デスクワーク": 10.5, "社内移動・立ち仕事": 1.0, "シャワー": 0.25,
    },
    "肉体労働の日": {       # 参考：引越し作業8時間（「体が」死ぬほど疲れた日）
        "睡眠": 7.0, "身支度": 0.5, "食事": 1.25, "通勤の徒歩": 0.5, "駅の階段": 0.1,
        "満員電車で立つ": 1.5, "引越し作業": 8.0, "社内移動・立ち仕事": 0.5, "シャワー": 0.25,
    },
}
HEADLINE_DAY = "死ぬほど疲れた日"
BASELINE_DAY = "普段の日"

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")


# =============================================================================
# 計算
# =============================================================================

@dataclass(frozen=True)
class Params:
    weight_kg: float = WEIGHT_KG
    body_fat_pct: float = BODY_FAT_PCT
    bmr_kcal_per_kg: float = BMR_KCAL_PER_KG
    met_factor: float = MET_KCAL_FACTOR
    tef: float = TEF_FRACTION
    fat_kcal_per_kg: float = FAT_KCAL_PER_KG
    essential_fat_pct: float = ESSENTIAL_FAT_PCT
    sleep_h: float | None = None          # 死ぬほど疲れた日の睡眠（減った分はデスクワークへ）
    train_met: float | None = None        # 満員電車で立つ METs
    scope: float = SUSTAINABLE_SCOPE


def bmr(p: Params) -> float:
    return p.bmr_kcal_per_kg * p.weight_kg


def mifflin_bmr(weight=WEIGHT_KG, height=HEIGHT_CM, age=AGE) -> float:
    """照合用：Mifflin-St Jeor 式（男性）"""
    return 10 * weight + 6.25 * height - 5 * age + 5


def day_schedule(name: str, p: Params) -> list[tuple[str, float, float, str]]:
    sched = dict(DAYS[name])
    if name == HEADLINE_DAY and p.sleep_h is not None:
        delta = sched["睡眠"] - p.sleep_h
        sched["睡眠"] = p.sleep_h
        sched["デスクワーク"] += delta
    rows = []
    for act, h in sched.items():
        met, src = ACTIVITY_METS[act]
        if act == "満員電車で立つ" and p.train_met is not None:
            met = p.train_met
        rows.append((act, h, met, src))
    rest = 24.0 - sum(h for _, h, _, _ in rows)
    assert rest >= -1e-9, f"{name}: 行動の合計が24時間を超えている ({24 - rest:.2f} h)"
    rows.append((REST_ACTIVITY[0], rest, REST_ACTIVITY[1], REST_ACTIVITY[2]))
    return rows


def met_hours(name: str, p: Params) -> float:
    return sum(h * met for _, h, met, _ in day_schedule(name, p))


def tee(name: str, p: Params, fed: bool = True) -> float:
    """1日の総消費 [kcal]。fed=True なら食事誘発性熱産生を加える"""
    activity = p.met_factor * met_hours(name, p) * p.weight_kg
    return activity / (1 - p.tef) if fed else activity


def reserves(p: Params) -> dict[str, float]:
    fat_kg = p.weight_kg * p.body_fat_pct / 100
    essential_kg = p.weight_kg * p.essential_fat_pct / 100
    usable_fat_kcal = (fat_kg - essential_kg) * p.fat_kcal_per_kg
    glycogen_kcal = GLYCOGEN_G * GLYCOGEN_KCAL_PER_G
    return {
        "fat_kg": fat_kg,
        "essential_kg": essential_kg,
        "usable_fat_kcal": usable_fat_kcal,
        "glycogen_kcal": glycogen_kcal,
    }


def simulate_fast(daily_kcal_at_start: float, p: Params, intake: float = 0.0, max_days: int = 3650):
    """絶食（または摂取不足）で動き続けたときの体組成の推移。

    Hall らのモデルの考え方：赤字を脂肪と除脂肪組織に p = C/(C+F) で分配する。
    消費は体重に比例して下がると仮定（代謝適応による追加の低下は無視＝早めに尽きる側）。
    死亡ラインは次のうち早い方：
      (1) 脂肪が必須脂肪まで減った時点（Leiter & Marliss 1982 の解釈）
      (2) BMI が LETHAL_BMI まで下がった時点
    戻り値: (日数, 理由, 軌跡)
    """
    F = p.weight_kg * p.body_fat_pct / 100
    L = p.weight_kg - F
    W0 = p.weight_kg
    rhoF, rhoL = p.fat_kcal_per_kg, LEAN_KCAL_PER_KG
    C = FORBES_C_KG * rhoL / rhoF
    traj = [(0, F, L)]
    for day in range(1, max_days + 1):
        W = F + L
        E = daily_kcal_at_start * W / W0
        deficit = E - intake
        if deficit <= 0:
            traj.append((day, F, L))
            continue
        pL = C / (C + F)
        F -= (1 - pL) * deficit / rhoF
        L -= pL * deficit / rhoL
        traj.append((day, F, L))
        if F <= (F + L) * p.essential_fat_pct / 100:
            return day, "必須脂肪", traj
        if (F + L) / (HEIGHT_CM / 100) ** 2 <= LETHAL_BMI:
            return day, f"BMI{LETHAL_BMI:.0f}", traj
    return None, "到達せず", traj


def equilibrium_weight(day_kcal: float, intake: float, p: Params) -> float:
    """消費∝体重 と仮定したときの、摂取と釣り合う体重"""
    return p.weight_kg * intake / day_kcal


# =============================================================================
# 出力
# =============================================================================

def fmt(x, d=0):
    return f"{x:,.{d}f}"


def main():
    p = Params()
    B = bmr(p)
    ceiling = p.scope * B
    eer = B * PAL_NORMAL
    res = reserves(p)
    reserve_total = res["usable_fat_kcal"] + res["glycogen_kcal"]

    print("=" * 70)
    print("モデル人物:", f"{p.weight_kg}kg / {AGE}歳男性 / 体脂肪率{p.body_fat_pct}%")
    print(f"基礎代謝（食事摂取基準）: {fmt(B)} kcal/日   照合: Mifflin式 {fmt(mifflin_bmr())} kcal/日")
    print(f"推定エネルギー必要量（PAL {PAL_NORMAL}）: {fmt(eer)} kcal/日")
    print(f"持続可能な上限 {p.scope}×BMR: {fmt(ceiling)} kcal/日")
    lo, hi = (x * 1000 / 4.184 for x in RAUSA_TEE_MJ)
    print(f"大陸横断レース走者の総消費: {fmt(lo)}〜{fmt(hi)} kcal/日")

    print("\n--- 1日の消費（METs積み上げ）---")
    tees = {}
    for name in DAYS:
        rows = day_schedule(name, p)
        print(f"\n[{name}]")
        for act, h, met, src in rows:
            kcal = p.met_factor * met * h * p.weight_kg
            print(f"  {act:<14} {h:5.2f} h × {met:4.2f} METs = {kcal:6.0f} kcal   ({src})")
        mh = met_hours(name, p)
        t_unfed = tee(name, p, fed=False)
        t = tee(name, p)
        tees[name] = t
        print(f"  合計 {mh:.2f} METs·h → 活動 {fmt(t_unfed)} kcal、食事誘発性熱産生込み {fmt(t)} kcal"
              f"  (PAL {t / B:.2f}、上限の {100 * t / ceiling:.0f}%)")

    head, base = tees[HEADLINE_DAY], tees[BASELINE_DAY]
    extra = head - base
    print("\n--- 山場の数字 ---")
    print(f"死ぬほど疲れた日 − 普段の日 = {fmt(extra)} kcal（バナナ {extra / BANANA_KCAL:.1f} 本分）")
    print(f"死ぬほど疲れた日 / 持続上限 = {100 * head / ceiling:.0f}%")
    print(f"死ぬほど疲れた日 / 大陸横断走者 = {100 * head / hi:.0f}〜{100 * head / lo:.0f}%")

    print("\n--- 体の貯金（A：エネルギー破産）---")
    print(f"体脂肪 {res['fat_kg']:.2f} kg（必須脂肪 {res['essential_kg']:.2f} kg を除く）"
          f" → 使える脂肪 {fmt(res['usable_fat_kcal'])} kcal + グリコーゲン {fmt(res['glycogen_kcal'])} kcal"
          f" = {fmt(reserve_total)} kcal")
    print(f"死ぬほど疲れた日の総消費は貯金の {100 * head / reserve_total:.1f}%")
    print(f"死ぬほど疲れた日の『追加分』は貯金の {100 * extra / reserve_total:.2f}%"
          f"（追加分だけで貯金を使い切るには {reserve_total / extra:,.0f} 日 ≈ {reserve_total / extra / 365:.0f} 年）")
    one_day_met = reserve_total / (p.met_factor * p.weight_kg * 24)
    run_km = reserve_total / (RUN_NET_KCAL_PER_KG_KM * p.weight_kg)
    print(f"1日で使い切るには 24時間ずっと平均 {one_day_met:.0f} METs が必要"
          f"／走って使い切るなら約 {fmt(run_km)} km（フルマラソン {run_km / MARATHON_KM:.0f} 本）")

    print("\n--- 食べずに続けたら（Hallモデル分配、消費∝体重）---")
    fast_results = {}
    for name in DAYS:
        d, why, traj = simulate_fast(tee(name, p, fed=False), p)
        F, L = traj[-1][1], traj[-1][2]
        fast_results[name] = (d, traj)
        print(f"  {name:<10}: {d} 日で{why}ライン（体重 {F + L:.1f} kg = {100 * (1 - (F + L) / p.weight_kg):.0f}%減、"
              f"脂肪 {F:.1f} kg、除脂肪 {p.weight_kg * (1 - p.body_fat_pct / 100) - L:.1f} kg 減）")
    rest_kcal = p.met_factor * 1.3 * 24 * p.weight_kg
    d_rest, why_rest, _ = simulate_fast(rest_kcal, p)
    print(f"  照合：1日中じっと座っている（1.3 METs、{fmt(rest_kcal)} kcal/日）: {d_rest} 日（{why_rest}）"
          f"  ← 1981年ハンスト死亡例（例：66日）と同じ桁か")

    print("\n--- 食べている場合（推定エネルギー必要量だけ食べ、毎日が死ぬほど疲れた日）---")
    W_eq = equilibrium_weight(head, eer, p)
    print(f"  毎日 {fmt(eer)} kcal 食べると、体重は約 {W_eq:.1f} kg で釣り合う（死なない）")

    print("\n--- 伝令（F）---")
    sparta = RUN_NET_KCAL_PER_KG_KM * p.weight_kg * ATHENS_SPARTA_KM
    legend = RUN_NET_KCAL_PER_KG_KM * p.weight_kg * MARATHON_ATHENS_KM
    print(f"  アテネ→スパルタ {ATHENS_SPARTA_KM:.0f} km を65kgの人が走る正味コスト: {fmt(sparta)} kcal"
          f" = あなたの『死ぬほど』の追加分 {sparta / extra:,.0f} 日分、貯金の {100 * sparta / reserve_total:.0f}%")
    print(f"  伝説のマラトン→アテネ {MARATHON_ATHENS_KM:.0f} km: {fmt(legend)} kcal"
          f" = あなたの『死ぬほど』の追加分 {legend / extra:,.0f} 日分、貯金の {100 * legend / reserve_total:.1f}%")

    verify(p, tees, reserve_total, d_rest)
    sens = sensitivity(p)
    make_figures(p, tees, ceiling, (lo, hi), fast_results, sens)


def verify(p: Params, tees, reserve_total, d_rest):
    """Step 4：単位・桁・別法での概算を照合する。外れたら AssertionError"""
    print("\n--- 検証（別法での概算と照合）---")
    B = bmr(p)
    checks = []
    # 1. 単位：MJ→kcal
    checks.append(("39.5 MJ/kg = 9,441 kcal/kg", abs(FAT_KCAL_PER_KG - 9441) < 1))
    # 2. 時間の合計が24hちょうど
    for name in DAYS:
        checks.append((f"{name} の合計が24h", abs(sum(h for _, h, _, _ in day_schedule(name, p)) - 24) < 1e-9))
    # 3. 普段の日の PAL が食事摂取基準の「ふつう」(1.75) と ±0.15 で一致
    pal_normal = tees[BASELINE_DAY] / B
    checks.append((f"普段の日 PAL {pal_normal:.2f} ≒ 1.75（食事摂取基準）", abs(pal_normal - 1.75) < 0.15))
    # 4. 死ぬほど疲れた日は PAL「ふつう〜高い」(1.75〜2.00) の範囲 → 別法 BMR×PAL と同じ桁
    pal_head = tees[HEADLINE_DAY] / B
    checks.append((f"死ぬほど疲れた日 PAL {pal_head:.2f} が 1.5〜2.0 の範囲", 1.5 <= pal_head <= 2.0))
    # 5. 1 MET 相当の安静代謝（1.05 kcal/kg/h）と基礎代謝の比が 1.0〜1.25（RMR は BMR よりやや高い）
    r = p.met_factor * p.weight_kg * 24 / B
    checks.append((f"1 MET×24h / BMR = {r:.2f}（1.0〜1.25）", 1.0 <= r <= 1.25))
    # 6. 貯金の桁：体脂肪 13 kg × 約9,000 kcal/kg ≒ 10万kcal台
    checks.append((f"貯金 {reserve_total:,.0f} kcal が 8万〜13万", 80_000 <= reserve_total <= 130_000))
    # 7. 安静絶食の生存日数が、報告されている範囲（ハンスト死亡例 約45〜75日）と同じ桁
    checks.append((f"安静絶食 {d_rest} 日 が 40〜100 日", 40 <= d_rest <= 100))
    # 8. 致死BMIでの体重減少率が「40〜50%減は生命の危険」と整合
    loss = 1 - LETHAL_BMI * (HEIGHT_CM / 100) ** 2 / p.weight_kg
    checks.append((f"BMI13 での体重減少 {100 * loss:.0f}% が 35〜50%", 0.35 <= loss <= 0.50))
    for label, ok in checks:
        print(f"  [{'OK' if ok else 'NG'}] {label}")
    assert all(ok for _, ok in checks), "検証に失敗した項目がある"


def sensitivity(p: Params):
    """見出しの数字（追加消費 kcal、上限比 %、貯金比 %、絶食日数）を前提ごとに振る"""
    def metrics(q: Params):
        B = bmr(q)
        h, b = tee(HEADLINE_DAY, q), tee(BASELINE_DAY, q)
        r = reserves(q)
        total = r["usable_fat_kcal"] + r["glycogen_kcal"]
        d, _, _ = simulate_fast(tee(HEADLINE_DAY, q, fed=False), q)
        return {"extra": h - b, "pct_ceiling": 100 * h / (q.scope * B),
                "pct_reserve": 100 * h / total, "fast_days": d}

    base = metrics(p)
    cases = [
        ("体重 55 / 75 kg", replace(p, weight_kg=55), replace(p, weight_kg=75)),
        ("体脂肪率 12 / 28 %", replace(p, body_fat_pct=12), replace(p, body_fat_pct=28)),
        ("死ぬほど日の睡眠 3 / 7 h", replace(p, sleep_h=3), replace(p, sleep_h=7)),
        ("電車で立つ 1.3 / 2.0 METs", p, replace(p, train_met=2.0)),
        ("METs換算 1.00 / 1.05", replace(p, met_factor=1.0), p),
        ("食事誘発性熱産生 0 / 10 %", replace(p, tef=0.0), p),
        ("基礎代謝 Mifflin式", replace(p, bmr_kcal_per_kg=mifflin_bmr() / WEIGHT_KG),
         replace(p, bmr_kcal_per_kg=mifflin_bmr() / WEIGHT_KG)),
        ("持続上限 2.5 / 3.0×BMR", p, replace(p, scope=3.0)),
        ("脂肪 9,441 / 7,700 kcal/kg", replace(p, fat_kcal_per_kg=7700), p),
        ("必須脂肪 3 / 5 %", p, replace(p, essential_fat_pct=5)),
    ]
    print("\n--- 感度分析 ---")
    print(f"{'前提':<28}{'追加kcal':>14}{'上限比%':>14}{'貯金比%':>14}{'絶食日数':>12}")
    print(f"{'基準':<28}{base['extra']:>14.0f}{base['pct_ceiling']:>14.0f}"
          f"{base['pct_reserve']:>14.1f}{base['fast_days']:>12}")
    out = []
    for label, a, b in cases:
        ma, mb = metrics(a), metrics(b)
        out.append((label, ma, mb))
        print(f"{label:<28}"
              f"{ma['extra']:>7.0f}/{mb['extra']:<6.0f}"
              f"{ma['pct_ceiling']:>7.0f}/{mb['pct_ceiling']:<6.0f}"
              f"{ma['pct_reserve']:>7.1f}/{mb['pct_reserve']:<6.1f}"
              f"{str(ma['fast_days']):>6}/{str(mb['fast_days']):<5}")
    # 最悪ケースの組み合わせ：「死ぬほど」が最も大きく見える前提をすべて重ねる
    worst = replace(p, sleep_h=3, train_met=2.0, weight_kg=75, body_fat_pct=12, scope=2.5)
    mw = metrics(worst)
    print(f"{'重ね合わせ（盛る側すべて）':<28}{mw['extra']:>14.0f}{mw['pct_ceiling']:>14.0f}"
          f"{mw['pct_reserve']:>14.1f}{mw['fast_days']:>12}")
    return base, out


# =============================================================================
# グラフ
# =============================================================================

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # 参照パレットの slot 1〜3


def _setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f in ("IPAPGothic", "IPAGothic", "Noto Sans CJK JP"):
        if any(f == x.name for x in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = f
            break
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
    })
    return plt


def make_figures(p, tees, ceiling, rausa, fast_results, sens):
    plt = _setup_mpl()
    os.makedirs(FIG_DIR, exist_ok=True)
    B = bmr(p)

    # --- 図1：1日の消費 vs 持続上限 ---
    labels = ["普段の日", "死ぬほど疲れた日", "肉体労働の日\n（引越し8時間）", "大陸横断レース走者\n（約140日間）"]
    vals = [tees["普段の日"], tees["死ぬほど疲れた日"], tees["肉体労働の日"], sum(rausa) / 2]
    colors = [MUTED, S2, MUTED, MUTED]
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    y = list(range(len(labels)))[::-1]
    ax.barh(y, vals, height=0.55, color=colors, edgecolor=SURFACE, linewidth=2)
    ax.errorbar([sum(rausa) / 2], [y[3]], xerr=[[sum(rausa) / 2 - rausa[0]], [rausa[1] - sum(rausa) / 2]],
                fmt="none", ecolor=INK2, capsize=6, lw=1.5)
    label_x = vals[:3] + [rausa[1]]
    for yi, v, lx in zip(y, vals, label_x):
        txt = f"{v:,.0f} kcal" if lx == v else f"{rausa[0]:,.0f}〜{rausa[1]:,.0f} kcal"
        ax.text(lx + 80, yi, txt, va="center", ha="left", color=INK, fontsize=14)
    ax.axvline(ceiling, color=S1, lw=2, ls="--")
    ax.text(ceiling + 60, y[0] + 0.5, f"人体が長く続けられる上限\n基礎代謝の2.5倍 ≈ {ceiling:,.0f} kcal",
            color=S1, ha="left", va="bottom", fontsize=12)
    ax.set_yticks(y, labels, fontsize=14)
    ax.set_xlim(0, 7600)
    ax.set_ylim(-0.6, len(labels) + 0.1)
    ax.set_xlabel("1日の総消費エネルギー [kcal]")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("あなたの「死ぬほど疲れた日」は、上限のどこにいるか", loc="left", fontsize=17, pad=48)
    fig.text(0.01, 0.01, f"モデル：{p.weight_kg:.0f}kg・{AGE}歳男性。METs積み上げ（Compendium）＋食事誘発性熱産生10%。"
             "上限：Thurber et al. 2019 Sci Adv。走者：Thurber 2016。", fontsize=9, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(FIG_DIR, "fig1_daily_vs_ceiling.png"))
    plt.close(fig)

    # --- 図2：食べずに続けたら、体脂肪はいつ尽きるか ---
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    series = [("普段の日", MUTED, (10, -34)), ("死ぬほど疲れた日", S2, (-130, -40)), ("肉体労働の日", S1, (10, 10))]
    for name, c, off in series:
        d, traj = fast_results[name]
        xs = [t[0] for t in traj]
        fs = [t[1] + t[2] for t in traj]
        ax.plot(xs, fs, color=c, lw=2.5)
        ax.plot([xs[-1]], [fs[-1]], "o", ms=9, color=c, mec=SURFACE, mew=2)
        ax.annotate(f"{name}\n{d}日", (xs[-1], fs[-1]), xytext=off, textcoords="offset points",
                    color=INK, fontsize=12)
    lethal_w = LETHAL_BMI * (HEIGHT_CM / 100) ** 2
    ax.axhline(lethal_w, color=INK2, lw=1, ls=":")
    ax.text(1, lethal_w - 2.2, f"BMI {LETHAL_BMI:.0f}（{lethal_w:.0f} kg）＝ 報告上の致死的なライン", color=INK2, fontsize=11)
    ax.set_xlim(0, 115)
    ax.set_ylim(30, p.weight_kg * 1.05)
    ax.set_xlabel("絶食で同じ1日を繰り返した日数")
    ax.set_ylabel("体重 [kg]")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("もし何も食べずに、毎日「死ぬほど疲れた日」を繰り返したら", loc="left", fontsize=17, pad=14)
    fig.text(0.01, 0.01, "※思考実験。真似しないでください。Hallらのモデル定数（脂肪39.5 MJ/kg、除脂肪7.6 MJ/kg）で"
             "脂肪と除脂肪組織に分配。代謝適応は無視。身長170cm仮定。致死ライン：ENN Field Exchange 15。",
             fontsize=9, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(FIG_DIR, "fig2_fasting_days.png"))
    plt.close(fig)

    # --- 図3：感度分析（上限比 %） ---
    base, rows = sens
    rows = sorted(rows, key=lambda r: abs(r[1]["pct_ceiling"] - r[2]["pct_ceiling"]))
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    b = base["pct_ceiling"]
    for i, (label, ma, mb) in enumerate(rows):
        lo_v, hi_v = sorted([ma["pct_ceiling"], mb["pct_ceiling"]])
        if hi_v - lo_v >= 0.5:
            ax.barh(i, hi_v - lo_v, left=lo_v, height=0.55, color=S2, edgecolor=SURFACE, linewidth=2)
            ax.text(max(hi_v, b) + 1, i, f"{lo_v:.0f}〜{hi_v:.0f}%", va="center", fontsize=11, color=INK)
        else:
            ax.plot([lo_v], [i], "o", ms=8, color=S2, mec=SURFACE, mew=2)
            note = "変化なし" if abs(lo_v - b) < 0.5 else f"{lo_v:.0f}%"
            ax.text(max(lo_v, b) + 1, i, note, va="center", fontsize=11, color=INK2)
    ax.axvline(b, color=INK2, lw=1.2)
    ax.axvline(100, color=S1, lw=2, ls="--")
    ax.text(99, len(rows) - 0.6, "上限（100%）", color=S1, ha="right", fontsize=12)
    ax.text(b + 0.6, -0.9, f"基準 {b:.0f}%", color=INK2, ha="left", fontsize=12)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=12)
    ax.set_xlim(40, 110)
    ax.set_ylim(-1.2, len(rows))
    ax.set_xlabel("「死ぬほど疲れた日」の消費 ÷ 持続可能な上限（基礎代謝×2.5）[%]")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("前提を変えても、上限には届かない", loc="left", fontsize=17, pad=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig3_sensitivity.png"))
    plt.close(fig)
    print(f"\nグラフを出力: {FIG_DIR}/fig1〜3")


if __name__ == "__main__":
    main()
