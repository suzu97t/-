# -*- coding: utf-8 -*-
"""base.html（new_deck.py の出力）の CSS を流用し、本文セクションを実物に差し替える。"""
import pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
base = (HERE / "base.html").read_text(encoding="utf-8")
head = base.split('<main class="deck skin-warm">')[0]

LOGO = "A社 情報システム部"

EXTRA_CSS = """
/* ===== このデッキ側の調整（slide-rules 手順9: パーツのCSSはデッキ側で直してよい） ===== */
/* エグゼクティブサマリー（現状→理由→打ち手の3段。§7.16） */
.slide .es-grp{display:grid;grid-template-columns:160px 1fr;column-gap:32px;padding:22px 0;border-top:1px solid var(--rule);align-items:start}
.slide .es-grp:first-child{border-top:0;padding-top:0}
.slide .es-grp:last-child{padding-bottom:0}
.slide .es-lab{font-family:var(--font-serif);font-size:23px;font-weight:700;color:var(--blue);line-height:1.3}
.slide .es-body ul{margin:0;padding-left:24px;font-size:21px;line-height:1.42}
.slide .es-body li{margin:0 0 11px}
.slide .es-body li:last-child{margin-bottom:0}
/* 横棒チャート（項目比較は横棒。§5.12） */
.s .hbar{display:grid;grid-template-columns:56mm 1fr 14mm;column-gap:3.5mm;row-gap:3mm;align-items:center;font-size:10pt;color:var(--ink)}
.s .hbar .track{height:5.4mm;background:none}
.s .hbar .fill{height:100%;background:var(--rule)}
.s .hbar .fill.on{background:var(--accent)}
.s .hbar .val{text-align:right;font-weight:700}
/* 選択肢の比較表を5列にする（案3つ＋読み取り） */
.slide .comparison{grid-template-columns:0.92fr 0.86fr 0.86fr 0.98fr 1.5fr}
.slide .comparison > div{border-bottom:1px solid var(--hairline)}
.slide .comparison > div:nth-last-child(-n+5){border-bottom:0}
.slide .comparison .na{background:var(--hairline);color:var(--muted)}
.slide .comparison .win{font-weight:700}
.slide .comparison ul{margin:0;padding-left:18px}
.slide .comparison li{margin:0 0 6px}
.slide .comparison li:last-child{margin-bottom:0}
/* リスク表: 列幅を決めて列名・セルの泣き別れを防ぐ（§6 列名は泣き別れしない） */
.slide .risk-table{table-layout:fixed}
.slide .risk-table th:nth-child(1),.slide .risk-table td:nth-child(1){width:22%}
.slide .risk-table th:nth-child(2),.slide .risk-table td:nth-child(2){width:26%}
.slide .risk-table th:nth-child(3),.slide .risk-table td:nth-child(3){width:35%}
.slide .risk-table th:nth-child(4),.slide .risk-table td:nth-child(4){width:17%}
/* リスク表のセルは2件以上ならブレットで列挙する（§6 詳細セルの厚み） */
.slide .risk-table .rl{font-weight:700}
.slide .risk-table ul{margin:0;padding-left:18px}
.slide .risk-table li{margin:0 0 6px}
.slide .risk-table li:last-child{margin-bottom:0}
/* 増減ブリッジの凡例（色を分けたら凡例を置く。§5.2） */
.slide .wf-legend{display:flex;gap:30px;margin-top:20px;font-size:16px;color:var(--ink)}
.slide .wf-legend span{display:flex;align-items:center;gap:8px}
.slide .wf-legend i{width:16px;height:16px;display:inline-block}
.slide .wf-legend .c-down{background:var(--cyan)}
.slide .twf-bar.up{background:none;border:1.8px solid var(--ink)}
.slide .wf-legend .c-up{background:none;border:1.8px solid var(--ink)}
.slide .wf-legend .c-tot{background:var(--ink)}
/* ロードマップ: 説明文は本文と同じ濃さで読ませ、器を内容の高さに合わせる（§5.13 引き伸ばし禁止） */
.slide .phase-copy{color:var(--ink)}
.slide .phase{min-height:auto}
.slide .phase-out{margin-top:16px;padding-top:12px;border-top:1px solid var(--hairline);font-size:17px;line-height:1.35}
"""


def s_head(kicker):
    return f'  <div class="bar"><div class="logo">{LOGO}</div><div class="date">{kicker}</div></div>'


def s_foot(page):
    return f'  <div class="foot"><b>{LOGO}</b><span>{page}</span></div>'


def slide_head(kicker):
    return f'    <div class="hdr"><div class="logo">{LOGO}</div><div class="date">{kicker}</div></div>'


# ── 表紙 ───────────────────────────────────────────────────────────────
cover = f"""<section class="s cover">
{s_head("2026年9月17日")}
  <div class="big">社内ヘルプデスクの一次対応を<br>どこまで自動化するか</div>
  <div class="rule"></div>
  <div class="sub">情報システム部　運営会議　提出</div>
  <div class="foot"><b>{LOGO}</b><span></span></div>
</section>"""

# ── p1 エグゼクティブサマリー ──────────────────────────────────────────
p1 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("要約")}
    <h1 class="title">一次対応は自動応答に寄せ、情報システム部は例外と承認に残る</h1>
    <div class="rule"></div>
    <div class="content">
      <div class="es-grp"><div class="es-lab">現状</div><div class="es-body"><ul>
        <li>問い合わせは月800件まで増えたが、一次対応は情報システム部の2名が兼務で受けている</li>
        <li>初回の回答は7月に11.8時間まで遅れ、翌営業日にずれ込む案件が出ている</li>
      </ul></div></div>
      <div class="es-grp"><div class="es-lab">遅れの理由</div><div class="es-body"><ul>
        <li>件数の半分はパスワード再発行と経費精算の差し戻しで、どちらも手順が決まっている</li>
        <li><strong>手順が決まった問い合わせを人が読んで返している間、判断が必要な案件が待たされている</strong></li>
      </ul></div></div>
      <div class="es-grp"><div class="es-lab">打ち手と判断</div><div class="es-body"><ul>
        <li>既存のチャットに自動応答を足してパスワード再発行から置き換えると、工数は月160時間から116時間まで落ちる</li>
        <li>回答の確定は担当者が行い、例外処理と承認は情報システム部に残す</li>
        <li>対象とする種別と承認の持ち方と費用枠を今週決める</li>
      </ul></div></div>
    </div>
    <footer class="footer"><span class="source">注：架空の事例。数値は問い合わせ管理システムの記録を模した仮置きの値</span><span>1</span></footer>
  </div>
</section>"""

# ── p2 初回回答までの時間 ─────────────────────────────────────────────
bars = [("4月", "5.2", 39), ("5月", "6.4", 48), ("6月", "9.1", 68), ("7月", "11.8", 88)]
bar_html = "".join(
    f'<div class="bar-wrap"><div class="bar-value">{v}</div>'
    f'<div class="bar" style="height:{h}%"></div><div class="bar-label">{lab}</div></div>'
    for lab, v, h in bars
)
p2 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("回答までの時間")}
    <h1 class="title">初回の回答は7月に11.8時間まで遅れ、翌営業日にずれ込む案件が出ている</h1>
    <div class="rule"></div>
    <div class="content"><div class="two-col">
      <div><div class="section-label">初回の回答までの平均時間、営業時間、2026年</div>
        <div class="bar-chart">{bar_html}</div>
      </div>
      <div class="insight-panel"><div class="section-label">遅れが出ている理由</div>
        <ul class="bullets">
          <li>一次対応は情報システム部の2名が<br>他の業務と兼務で受けている</li>
          <li>6月からは端末の入れ替えが重なり、<br>件数が1.3倍に増えている</li>
          <li>手順が決まった問い合わせも、<br>担当者が本文を読んで返している</li>
        </ul>
      </div>
    </div></div>
    <footer class="footer"><span class="source">出典：問い合わせ管理システムの記録（2026年4〜7月）。営業時間は1日8時間で換算。数値は仮置き</span><span>2</span></footer>
  </div>
</section>"""

# ── p3 種別ごとの件数 ─────────────────────────────────────────────────
rows = [
    ("パスワード再発行", 240, True),
    ("経費精算の差し戻し", 160, True),
    ("会議室と備品の貸出", 92, False),
    ("端末の不調", 84, False),
    ("権限の申請", 76, False),
    ("経費規程の確認", 58, False),
    ("ソフトウェアの導入依頼", 46, False),
    ("その他", 44, False),
]
hb = "".join(
    f'<div class="cat">{n}</div>'
    f'<div class="track"><div class="fill{" on" if on else ""}" style="width:{v / 240 * 100:.1f}%"></div></div>'
    f'<div class="val">{v}</div>'
    for n, v, on in rows
)
p3 = f"""<section class="s">
{s_head("問い合わせの内訳")}
  <h1>問い合わせの半分は、パスワード再発行と経費精算の差し戻しに集まる</h1>
  <div class="c">
    <div class="two" style="grid-template-columns:1.7fr 1fr">
      <div>
        <div class="axh"><span>問い合わせの件数</span><span class="u">件／月、2026年4〜7月の平均</span></div>
        <div class="hbar">{hb}</div>
        <div class="legend left" style="margin-top:4mm"><span><i style="background:var(--accent)"></i>自動応答に寄せる種別</span><span><i style="background:var(--rule)"></i>人が受け続ける種別</span></div>
      </div>
      <div>
        <div class="colh">置き換えの向き不向き</div>
        <ul>
          <li>パスワード再発行は手順が1本で、担当者の判断が入らない</li>
          <li>経費精算の差し戻しは、理由が規程の5類型に収まる</li>
          <li>端末の不調から下は現物と現場の確認が入るため、<br>人が受け続ける</li>
          <li>権限の申請は承認の判断が入るため、<br>自動応答の対象から外す</li>
        </ul>
      </div>
    </div>
    <div class="src">出典：問い合わせ管理システムの記録（2026年4〜7月の月平均）。数値は仮置き</div>
  </div>
{s_foot(3)}
</section>"""

# ── p4 工数の試算（増減ブリッジ） ─────────────────────────────────────
K = 1.625  # 1時間 = 1.625px
wf = [
    ("現状の一次対応", "160", "base", 160 * K, 0),
    ("パスワード再発行の自動応答", "−34", "down", 34 * K, 126 * K),
    ("経費精算の差し戻しの自動応答", "−22", "down", 22 * K, 104 * K),
    ("例外処理と回答文の整備", "+12", "up", 12 * K, 104 * K),
    ("自動応答を入れた場合", "116", "total", 116 * K, 0),
]
wf_html = "".join(
    f'<div class="twf-col"><div class="twf-value">{v}</div>'
    f'<div class="twf-bar {c}" style="height:{h:.0f}px;margin-bottom:{mb:.0f}px"></div>'
    f'<div class="twf-label">{lab}</div></div>'
    for lab, v, c, h, mb in wf
)
p4 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("工数の試算")}
    <h1 class="title">一次対応の工数は月160時間から116時間まで落ちるが、例外処理は残る</h1>
    <div class="rule"></div>
    <div class="content">
      <div class="chart-unit">一次対応にかかる工数、時間／月、自動応答を入れた場合の試算</div>
      <div class="twf">{wf_html}</div>
      <div class="wf-legend"><span><i class="c-tot"></i>起点と着地</span><span><i class="c-down"></i>自動応答で減る分</span><span><i class="c-up"></i>新たに増える分</span></div>
    </div>
    <footer class="footer"><span class="source">試算の前提：問い合わせは月800件、一次対応は1件あたり12分、自動応答で解決する割合は実測がないため7割と仮置き。増える分は回答文の整備と例外の引き継ぎ</span><span>4</span></footer>
  </div>
</section>"""

# ── p5 案の比較 ───────────────────────────────────────────────────────
cmp_cells = [
    ("head", "評価軸"), ("head", "現行のまま"), ("head", "手順書を書き直す"),
    ("head", "自動応答を足す"), ("head", "読み取り"),
    ("row-label", "初期の費用"), ("win", "0円"), ("", "20万円"), ("", "80万円"),
    ("", "<ul><li>自動応答の80万円は、削れる工数44時間の2か月分で戻る</li></ul>"),
    ("row-label", "着手から効果が出るまで"), ("na", "—"), ("", "3か月"), ("win", "1か月"),
    ("", "<ul><li>手順書は書いても読まれず、件数が下がるまで時間がかかる</li></ul>"),
    ("row-label", "一次対応の工数"), ("", "160時間のまま"), ("", "140時間まで"), ("win", "116時間まで"),
    ("", "<ul><li>工数が実際に落ちるのは自動応答だけ</li><li>手順書の書き直しは自動応答の回答文としても使える</li></ul>"),
    ("row-label", "誤回答のリスク"), ("win", "なし"), ("win", "なし"), ("", "回答範囲を絞れば小さい"),
    ("", "<ul><li>自動応答を選ぶなら、範囲を絞る手当てが前提になる</li></ul>"),
]
cmp_html = "".join(
    (f'<div class="{c}">{t}</div>' if c else f'<div>{t}</div>') for c, t in cmp_cells
)
p5 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("案の比較")}
    <h1 class="title">既存のチャットに自動応答を足す案なら、費用も着手までの時間も小さい</h1>
    <div class="rule"></div>
    <div class="content"><div class="comparison">{cmp_html}</div></div>
    <footer class="footer"><span class="source">注：費用と期間は3社への概算照会を模した仮置きの値。工数は前ページの試算、人件費は1時間9千円で換算。太字は評価軸ごとに勝っている案</span><span>5</span></footer>
  </div>
</section>"""

# ── p6 リスクと対応 ───────────────────────────────────────────────────
risks = [
    ("自動応答が古い手順を返す",
     ["再問い合わせが週5件を超える", "未解決の申告が2割を超える"],
     ["回答の範囲をパスワード再発行の手順に絞る", "手順が変わった日に回答文を差し替える"],
     "情報システム部"),
    ("社内の情報が回答文に混ざる",
     ["回答文に個人名や口座番号が出る"],
     ["参照先を公開済みの手順書だけに限る", "回答の確定は担当者が行う"],
     "情報システム部と法務部"),
    ("手順書の更新が止まる",
     ["手順書の最終更新から3か月が過ぎる"],
     ["四半期ごとに手順書の棚卸しを行う", "更新の止まった手順は自動応答の対象から外す"],
     "業務基盤グループ"),
    ("利用が定着せず電話に戻る",
     ["チャット経由の比率が3割を下回る"],
     ["電話の一次窓口を受付時間の後半に寄せる", "自動応答で解決した件数を月次で共有する"],
     "業務基盤グループ"),
]


def ul(items):
    if len(items) == 1:
        return items[0]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


risk_rows = "".join(
    f'<tr><td class="rl">{name}</td><td>{ul(sig)}</td><td>{ul(act)}</td><td>{owner}</td></tr>'
    for name, sig, act, owner in risks
)
p6 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("リスクと対応")}
    <h1 class="title">どのリスクも先に兆候が出るため、基準値を決めて手前で止める</h1>
    <div class="rule"></div>
    <div class="content"><table class="risk-table">
      <thead><tr><th>起きうること</th><th>先に出る兆候</th><th>対応策</th><th>持つ部署</th></tr></thead>
      <tbody>{risk_rows}</tbody>
    </table></div>
    <footer class="footer"><span class="source">注：兆候の基準値は10月の試験導入の実績を見て見直す</span><span>6</span></footer>
  </div>
</section>"""

# ── p7 進め方 ─────────────────────────────────────────────────────────
phases = [
    ("9月", "対象と承認を決める", "パスワード再発行の手順書を1本に整え、回答を確定する担当者を決める",
     "手順書1本と承認の決定"),
    ("10月", "情報システム部内で試す", "部内の20名で試し、誤回答の出方と対応にかかった時間を記録する",
     "誤回答の記録と対応時間"),
    ("11月", "全社に開放する", "パスワード再発行の問い合わせを自動応答に寄せ、電話の窓口を受付時間の後半に移す",
     "自動応答で解決した件数"),
    ("12月以降", "対象を広げる", "経費精算の差し戻しを足し、削れた工数の実績を運営会議で見る",
     "工数の実績と対象の判断"),
]
phase_html = "".join(
    f'<div class="phase"><div class="phase-year">{y}</div>'
    f'<div class="phase-title">{t}</div><div class="phase-copy">{c}</div>'
    f'<div class="phase-out">出るもの：{o}</div></div>'
    for y, t, c, o in phases
)
p7 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("進め方")}
    <h1 class="title">対象はパスワード再発行から始め、12月に経費精算の差し戻しへ広げる</h1>
    <div class="rule"></div>
    <div class="content"><div class="roadmap">{phase_html}</div></div>
    <footer class="footer"><span class="source">注：11月の全社開放は、10月の試験導入で誤回答が兆候の基準値を下回ることを前提とする</span><span>7</span></footer>
  </div>
</section>"""

# ── p8 決めること ─────────────────────────────────────────────────────
decide = [
    ("対象とする種別", "パスワード再発行から始め、経費精算の差し戻しを12月に足す", "情報システム部長",
     ["10月の試験導入が11月以降にずれる", "問い合わせが増える3月に間に合わない"]),
    ("承認の持ち方", "自動応答は下書きまでとし、回答の確定は担当者が行う", "情報システム部長と経理部長",
     ["誤回答の責任の所在が決まらない", "内部監査で運用の記録を求められる"]),
    ("費用枠", "初期の設定に80万円、運用に月15万円までとする", "情報システム部長",
     ["見積の取得に入れない", "10月の着手ができない"]),
]
dec_rows = "".join(
    f'<tr><td class="ax">{a}</td><td>{b}</td><td>{c}</td>'
    f'<td><ul class="cb">' + "".join(f"<li>{x}</li>" for x in d) + "</ul></td></tr>"
    for a, b, c, d in decide
)
p8 = f"""<section class="s">
{s_head("決めること")}
  <h1>今週決めるのは、対象とする種別と承認の持ち方と費用枠</h1>
  <div class="c">
    <table>
      <tr><th class="ax" style="width:40mm">決めること</th><th>事務局の案</th><th style="width:52mm">決める人</th><th style="width:72mm">先送りした場合に起きること</th></tr>
      {dec_rows}
    </table>
    <div class="src">注：費用枠は初期80万円、運用は月15万円を上限とする事務局案。決定は9月19日までに必要</div>
  </div>
{s_foot(8)}
</section>"""

# ── 裏表紙 ───────────────────────────────────────────────────────────
back = f"""<section class="s cover">
{s_head("2026年9月17日")}
  <div class="big" style="margin-top:60mm;font-size:22pt">A社 情報システム部 業務基盤グループ</div>
  <div class="sub">内線 2431／helpdesk-pj@example.co.jp</div>
  <div class="src" style="position:absolute;left:16mm;bottom:14mm">本資料は consulting-pptx-skill（github.com/carnot-tech/consulting-pptx-skill）で作成</div>
  <div class="foot"><b>{LOGO}</b><span></span></div>
</section>"""

body = "\n".join([cover, p1, p2, p3, p4, p5, p6, p7, p8, back])
head = head.replace("</style>", EXTRA_CSS + "</style>")
out = head + '<main class="deck skin-warm">\n' + body + "\n</main>\n</body>\n</html>\n"
(HERE / "deck.html").write_text(out, encoding="utf-8")
print("wrote deck.html", len(out))
