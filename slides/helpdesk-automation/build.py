# -*- coding: utf-8 -*-
"""base.html（new_deck.py の出力）の CSS を流用し、本文セクションを実物に差し替える。

図のあるページ（P.5 対象の選び方／P.6 流れ／P.7 構成／P.10 判定）は diagram-design の作法で
diagrams.py が描く。デッキの規約は consulting-pptx-skill の references/slide-rules.md。
"""
import pathlib

import diagrams as dg

HERE = pathlib.Path(__file__).resolve().parent
base = (HERE / "base.html").read_text(encoding="utf-8")
head = base.split('<main class="deck skin-warm">')[0]

LOGO = "A社 情報システム部"
# 全体マップで宣言した区分。後続ページの右上にタグチップとして常設する（slide-rules §4.33）
SECTIONS = ["1 現状と対象", "2 仕組み", "3 効果と案", "4 進め方と判断"]

EXTRA_CSS = """
/* ===== このデッキ側の調整（slide-rules 手順9: パーツのCSSはデッキ側で直してよい） ===== */
/* 2つのパーツ集で版面が 3〜22px ずれるので、追加パーツ集（.slide）を基本パーツ集（.s）に合わせる（§4.19） */
.slide .sinner{inset:56px 75.6px 28px 75.6px}
.slide .title{margin-top:21px}
/* 区分のタグチップ（全体マップで立てた軸を後続ページで運ぶ。§4.33） */
.s .chips,.slide .chips{display:flex;align-items:center}
.s .chips span{font-size:7.5pt;letter-spacing:.04em;color:var(--muted);border:1px solid var(--hairline);padding:0.6mm 1.8mm;margin-left:1.2mm}
.s .chips span.on{background:var(--navy);border-color:var(--navy);color:#fff}
.slide .chips span{font-size:12px;letter-spacing:.04em;color:var(--muted);border:1px solid var(--hairline);padding:3px 7px;margin-left:5px}
.slide .chips span.on{background:var(--navy);border-color:var(--navy);color:#fff}
/* 図（diagram-design）。文字はデッキの書体に揃える（1デッキ2書体まで。§1） */
.s .dg{display:block;width:100%;height:auto;flex:0 0 auto}
.s .dg text{font-family:var(--font-sans)}
/* エグゼクティブサマリー（現状→理由→打ち手の3段。§7.16） */
.slide .es-grp{display:grid;grid-template-columns:160px 1fr;column-gap:32px;padding:22px 0;border-top:1px solid var(--rule);align-items:start}
.slide .es-grp:first-child{border-top:0;padding-top:0}
.slide .es-grp:last-child{padding-bottom:0}
.slide .es-lab{font-family:var(--font-serif);font-size:23px;font-weight:700;color:var(--blue);line-height:1.3}
.slide .es-body ul{margin:0;padding-left:24px;font-size:21px;line-height:1.42}
.slide .es-body li{margin:0 0 11px}
.slide .es-body li:last-child{margin-bottom:0}
/* 縦棒に基準線を引く（タイトルの「1営業日」を図から読めるようにする） */
.slide .bar-chart{position:relative}
.slide .ref-line{position:absolute;left:0;right:0;border-top:1px dashed var(--muted)}
.slide .ref-line span{position:absolute;right:0;top:-22px;font-size:15px;color:var(--muted)}
/* 最終ページの表は伸ばさず、軸の縦罫が最終行の下に垂れないようにする（§5.4） */
.s.tight .c{justify-content:center}
.s.tight .c>table{flex:0 1 auto;height:auto}
/* 横棒チャート（項目比較は横棒。§5.12） */
.s .hbar{display:grid;grid-template-columns:56mm 1fr 14mm;column-gap:3.5mm;row-gap:3mm;align-items:center;font-size:10pt;color:var(--ink)}
.s .hbar .track{height:5.4mm;background:none}
.s .hbar .fill{height:100%;background:var(--rule)}
.s .hbar .fill.on{background:var(--accent)}
.s .hbar .val{text-align:right;font-weight:700}
/* 選択肢の比較表を5列にする（案3つ＋示唆） */
.slide .comparison{grid-template-columns:0.92fr 0.8fr 0.86fr 0.92fr 1.6fr}
.slide .comparison > div{min-height:72px;border-bottom:1px solid var(--hairline)}
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
/* 増減ブリッジ: 濃色＝自動応答が効く分（P.4 の横棒と同じ意味）、起点と着地は淡色、増える分は白抜き */
.slide .twf-bar.base,.slide .twf-bar.total{background:rgba(50,32,20,0.10)}
.slide .twf-bar{position:relative}
.slide .twf-bar .lnk{position:absolute;right:-30px;width:30px;border-top:1px dotted var(--muted)}
.slide .twf-bar .lnk.t{top:0}
.slide .twf-bar .lnk.b{bottom:0}
.slide .twf-bar.down{background:var(--accent)}
.slide .twf-bar.up{background:none;border:1.8px solid var(--ink)}
.slide .wf-legend{display:flex;gap:30px;margin-top:20px;font-size:16px;color:var(--ink)}
.slide .wf-legend span{display:flex;align-items:center;gap:8px}
.slide .wf-legend i{width:16px;height:16px;display:inline-block}
.slide .wf-legend .c-tot{background:rgba(50,32,20,0.10)}
.slide .wf-legend .c-down{background:var(--accent)}
.slide .wf-legend .c-up{background:none;border:1.8px solid var(--ink)}
/* ロードマップ: 時間の向きを軸で示し、説明文は本文と同じ濃さで読ませる */
.slide .rm-axis{position:relative;height:2px;background:var(--navy);margin-bottom:20px}
.slide .rm-axis::after{content:"";position:absolute;right:-1px;top:-5px;border-top:6px solid transparent;border-bottom:6px solid transparent;border-left:12px solid var(--navy)}
.slide .phase-copy{color:var(--ink)}
.slide .phase{min-height:auto}
.slide .phase:first-child{padding-left:0}
.slide .phase-out{margin-top:16px;padding-top:12px;border-top:1px solid var(--hairline);font-size:17px;line-height:1.35}
"""


def chips(active=None):
    if active is None:
        return ""
    return ('<div class="chips">'
            + "".join(f'<span class="{"on" if i == active else ""}">{s}</span>'
                      for i, s in enumerate(SECTIONS, 1))
            + "</div>")


def s_head(right):
    return f'  <div class="bar"><div class="logo">{LOGO}</div><div class="date">{right}</div></div>'


def s_foot(page):
    return f'  <div class="foot"><b>{LOGO}</b><span>{page}</span></div>'


def slide_head(right):
    return f'    <div class="hdr"><div class="logo">{LOGO}</div><div class="date">{right}</div></div>'


# ── 表紙 ───────────────────────────────────────────────────────────────
cover = f"""<section class="s cover">
{s_head("2026年9月17日")}
  <div class="big">社内ヘルプデスクの一次対応を<br>どこまで自動化するか</div>
  <div class="rule"></div>
  <div class="sub">情報システム部　運営会議　提出</div>
  <div class="foot"><b>{LOGO}</b><span></span></div>
</section>"""

# ── P.1 全体マップ ─────────────────────────────────────────────────────
map_rows = [
    ("1 現状と対象", "問い合わせの半分は2種類に集まり、そこだけが自動応答に向く", "3〜5"),
    ("2 仕組み", "自動応答は下書きまでを作り、送るのは担当者が確かめる", "6〜8"),
    ("3 効果と案", "工数は月160時間から116時間まで減り、初期費用は3か月で戻る", "9〜10"),
    ("4 進め方と判断", "10月に部内で試験導入し、11月に全社へ開放する", "11〜13"),
]
p1 = f"""<section class="s">
{s_head("全体マップ")}
  <h1>対象の絞り込みと人の確認の残し方が、この資料の論点</h1>
  <div class="c">
    <div class="rows">
      {"".join(f'<div class="r"><div class="l">{a}</div><div>{b}<span class="ref">→ P.{n}</span></div></div>' for a, b, n in map_rows)}
    </div>
    <div class="src">注：架空の事例。数値は問い合わせ管理システムの記録を模した仮置きの値</div>
  </div>
{s_foot(1)}
</section>"""

# ── P.2 エグゼクティブサマリー ─────────────────────────────────────────
p2 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head("要約")}
    <h1 class="title">一次対応は自動応答に置き換え、情報システム部は例外と承認に残る</h1>
    <div class="rule"></div>
    <div class="content">
      <div class="es-grp"><div class="es-lab">現状</div><div class="es-body"><ul>
        <li>問い合わせは月平均800件で、初回の回答を返すまでの一次対応を情報システム部の2名が兼務で受けている</li>
        <li>初回の回答までの平均時間は7月に11.8時間まで伸び、1営業日を超えている</li>
      </ul></div></div>
      <div class="es-grp"><div class="es-lab">遅れの理由</div><div class="es-body"><ul>
        <li>件数の半分はパスワード再発行と経費精算の差し戻しで、どちらも手順が決まっている</li>
        <li><strong>手順が決まっている問い合わせを人が読んで返している間、判断が必要な問い合わせが待たされている</strong></li>
      </ul></div></div>
      <div class="es-grp"><div class="es-lab">打ち手と判断</div><div class="es-body"><ul>
        <li>既存のチャットに自動応答を足し、11月にパスワード再発行、12月以降に経費精算の差し戻しを置き換える</li>
        <li>工数は月160時間から11月に約138時間、12月以降は116時間まで減り、例外処理と承認は情報システム部に残る</li>
        <li>対象の種別、承認の権限、費用枠を今週決める</li>
      </ul></div></div>
    </div>
    <footer class="footer"><span class="source">注：架空の事例。数値は問い合わせ管理システムの記録を模した仮置きの値</span><span>2</span></footer>
  </div>
</section>"""

# ── P.3 初回回答までの時間 ─────────────────────────────────────────────
bars = [("4月", "5.2", 39), ("5月", "6.4", 48), ("6月", "9.1", 68), ("7月", "11.8", 88)]
bar_html = "".join(
    f'<div class="bar-wrap"><div class="bar-value">{v}</div>'
    f'<div class="bar" style="height:{h}%"></div><div class="bar-label">{lab}</div></div>'
    for lab, v, h in bars
)
p3 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head(chips(1))}
    <h1 class="title">初回の回答までの平均時間は7月に11.8時間まで伸び、1営業日を超えている</h1>
    <div class="rule"></div>
    <div class="content"><div class="two-col">
      <div><div class="section-label">初回の回答までの平均時間、時間、2026年</div>
        <div class="bar-chart">{bar_html}<div class="ref-line" style="bottom:215px"><span>1営業日＝8時間</span></div></div>
      </div>
      <div class="insight-panel"><div class="section-label">遅れが出ている理由</div>
        <ul class="bullets">
          <li>一次対応は情報システム部の2名が<br>他の業務と兼務で受けている</li>
          <li>端末の入れ替えが重なる6〜7月の件数は、<br>4〜5月の月平均の1.3倍に増えている</li>
          <li>手順が決まっている問い合わせも、<br>担当者が本文を読んで返している</li>
        </ul>
      </div>
    </div></div>
    <footer class="footer"><span class="source">出典：問い合わせ管理システムの記録（2026年4〜7月）。時間は1日8時間の営業時間で換算。1.3倍は4〜5月と6〜7月の月平均の比。数値は仮置き</span><span>3</span></footer>
  </div>
</section>"""

# ── P.4 種別ごとの件数 ─────────────────────────────────────────────────
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
p4 = f"""<section class="s">
{s_head(chips(1))}
  <h1>問い合わせの半分は、パスワード再発行と経費精算の差し戻しに集まる</h1>
  <div class="c">
    <div class="two" style="grid-template-columns:1.7fr 1fr">
      <div>
        <div class="axh"><span>問い合わせの件数</span><span class="u">件／月、2026年4〜7月の平均</span></div>
        <div class="hbar">{hb}</div>
        <div class="legend left" style="margin-top:4mm"><span><i style="background:var(--accent)"></i>自動応答に置き換える種別</span><span><i style="background:var(--rule)"></i>人が受け続ける種別</span></div>
      </div>
      <div>
        <div class="colh">件数の読み方</div>
        <ul>
          <li>上位2種で月400件を占め、<br>一次対応の工数の半分がここに入る</li>
          <li>3位以下はどれも月100件に届かず、<br>種類だけが多い</li>
          <li>上位2種を減らさないかぎり、<br>待ち時間は縮まらない</li>
        </ul>
      </div>
    </div>
    <div class="src">出典：問い合わせ管理システムの記録（2026年4〜7月の月平均）。経費精算の差し戻しは、差し戻された申請をどう直すかの問い合わせ。数値は仮置き</div>
  </div>
{s_foot(4)}
</section>"""

# ── P.5 対象の選び方（2×2） ────────────────────────────────────────────
p5 = f"""<section class="s">
{s_head(chips(1))}
  <h1>件数が多く手順が定まった種別だけが、自動応答に向く</h1>
  <div class="c">
    <div class="axh"><span>問い合わせ種別の位置づけ</span><span class="u">縦は件／月（横線は120件）、横は手順が決まっている度合い</span></div>
    {dg.quadrant()}
    <div class="src">出典：件数は問い合わせ管理システムの記録（2026年4〜7月の月平均）。横の位置は担当者2名への聞き取りによる。残る6種別は、現物か承認の確認が入るか件数が少ないため対象から外す</div>
  </div>
{s_foot(5)}
</section>"""

# ── P.6 流れ（スイムレーン） ───────────────────────────────────────────
p6 = f"""<section class="s">
{s_head(chips(2))}
  <h1>自動応答は下書きまでを作り、担当者が確かめてから送る</h1>
  <div class="c">
    <div class="axh"><span>自動応答を入れたあとの一次対応の流れ</span><span class="u">パスワード再発行の場合</span></div>
    {dg.swimlane()}
    <div class="src">注：自動応答が回答を確定して送ることはない。対象外と判定した問い合わせは、下書きを作らずに担当者が自分で調べて回答する</div>
  </div>
{s_foot(6)}
</section>"""

# ── P.7 構成（アーキテクチャ） ─────────────────────────────────────────
p7 = f"""<section class="s">
{s_head(chips(2))}
  <h1>新しく作るのは点線の中だけで、チャットは既存のまま使う</h1>
  <div class="c">
    <div class="axh"><span>自動応答の構成</span><span class="u">点線の枠が今回作る範囲</span></div>
    {dg.architecture()}
    <div class="src">注：初期費用80万円は、点線の枠の中（自動応答・確認画面・手順書の索引・記録）の設定と接続にかかる費用で、金額は仮置き</div>
  </div>
{s_foot(7)}
</section>"""

# ── P.8 工数の試算（増減ブリッジ） ─────────────────────────────────────
K = 1.625  # 1時間 = 1.625px
wf = [
    ("現状の一次対応", "160", "base", 160 * K, 0, "t"),
    ("パスワード再発行の自動応答", "−34", "down", 34 * K, 126 * K, "b"),
    ("経費精算の差し戻しの自動応答", "−22", "down", 22 * K, 104 * K, "b"),
    ("例外処理と回答文の整備", "+12", "up", 12 * K, 104 * K, "t"),
    ("自動応答を入れた場合", "116", "total", 116 * K, 0, ""),
]
def _lnk(lk):
    return f'<i class="lnk {lk}"></i>' if lk else ""


wf_html = "".join(
    f'<div class="twf-col"><div class="twf-value">{v}</div>'
    f'<div class="twf-bar {c}" style="height:{h:.0f}px;margin-bottom:{mb:.0f}px">{_lnk(lk)}</div>'
    f'<div class="twf-label">{lab}</div></div>'
    for lab, v, c, h, mb, lk in wf
)
p8 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head(chips(3))}
    <h1 class="title">自動応答を入れた場合、一次対応の工数は月160時間から116時間まで減る</h1>
    <div class="rule"></div>
    <div class="content">
      <div class="chart-unit">一次対応にかかる工数、時間／月、両方の種別を置き換えた場合の試算</div>
      <div class="twf">{wf_html}</div>
      <div class="wf-legend"><span><i class="c-tot"></i>現状と試算後</span><span><i class="c-down"></i>自動応答で減る分</span><span><i class="c-up"></i>新たに増える分</span></div>
    </div>
    <footer class="footer"><span class="source">試算の前提：問い合わせは4〜7月の月平均800件、一次対応は1件あたり12分、自動応答で解決する割合は実測がないため7割と仮置き。116時間は経費精算まで広げた12月以降の姿で、パスワード再発行だけの11月時点は約138時間</span><span>9</span></footer>
  </div>
</section>"""

# ── P.10 案の比較 ──────────────────────────────────────────────────────
cmp_cells = [
    ("head", "評価軸"), ("head", "現行のまま"), ("head", "手順書を書き直す"),
    ("head", "自動応答を足す"), ("head", "示唆"),
    ("row-label", "初期の費用"), ("win", "0円"), ("", "20万円"), ("", "80万円"),
    ("", "<ul><li>削減額は月約40万円、運用費は月15万円。差引き月25万円で、初期80万円は約3か月で戻る</li></ul>"),
    ("row-label", "運用の費用（月額）"), ("win", "0円"), ("win", "0円"), ("", "15万円"),
    ("", "<ul><li>運用の月15万円は自動応答の利用料。手順書は書き直したあとの費用がかからない</li></ul>"),
    ("row-label", "着手から試験導入まで"), ("na", "—"), ("", "3か月"), ("win", "1か月"),
    ("", "<ul><li>自動応答は10月に部内で試せる。全社の工数が減るのは11月から</li><li>手順書の書き直しは、閲覧が伸びなければ件数に効かない</li></ul>"),
    ("row-label", "一次対応の工数"), ("", "160時間のまま"), ("", "140時間まで"), ("win", "116時間まで"),
    ("", "<ul><li>削減幅が最も大きいのは自動応答</li><li>116時間は経費精算まで広げた12月以降の値</li></ul>"),
    ("row-label", "誤回答のリスク"), ("win", "現状のまま"), ("win", "現状のまま"), ("", "回答範囲を絞る前提"),
    ("", "<ul><li>自動応答を選ぶなら、範囲を絞り人が確定する手当てが前提になる</li></ul>"),
]
cmp_html = "".join(
    (f'<div class="{c}">{t}</div>' if c else f'<div>{t}</div>') for c, t in cmp_cells
)
p9 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head(chips(3))}
    <h1 class="title">自動応答は初期費用が最も高いが、工数の削減幅と着手の早さで上回る</h1>
    <div class="rule"></div>
    <div class="content"><div class="comparison">{cmp_html}</div></div>
    <footer class="footer"><span class="source">注：費用と期間は仮置き。自動応答の工数は P.9 の試算、手順書の140時間は実測がないため仮置き。人件費は1時間9千円で換算。回収は月44時間が続く12月以降を起点にした。太字は軸ごとに勝っている案</span><span>10</span></footer>
  </div>
</section>"""

# ── P.10 判定（フローチャート） ────────────────────────────────────────
p10 = f"""<section class="s">
{s_head(chips(2))}
  <h1>対象と判断できない問い合わせは、自動応答が担当者に回す</h1>
  <div class="c">
    <div class="two" style="grid-template-columns:1.35fr 1fr">
      <div>
        <div class="axh"><span>自動応答が答えるかの判定</span><span class="u">問い合わせ1件ごと</span></div>
        {dg.flowchart()}
      </div>
      <div>
        <div class="colh">担当者に回す条件</div>
        <ul>
          <li>対象の種別でない問い合わせは、<br>自動応答が下書きを作らない</li>
          <li>手順書の更新が3か月止まっていれば、<br>その手順を対象から外す</li>
          <li>判定に迷った問い合わせは、<br>担当者に回す側に倒す</li>
        </ul>
      </div>
    </div>
    <div class="src">注：対象の種別は P.4 の上位2種、手順書は最終更新から3か月を境にする。境目の値は10月の試験導入の実績を見て見直す</div>
  </div>
{s_foot(8)}
</section>"""

# ── P.11 リスクと対応 ──────────────────────────────────────────────────
risks = [
    ("自動応答が古い手順を返す",
     ["再問い合わせが週5件を超える", "未解決の申告が2割を超える"],
     ["回答の範囲をパスワード再発行の手順に絞る", "手順が変わった日に回答文を差し替える"],
     "情報システム部"),
    ("回答文に社外秘の情報が入る",
     ["参照先に未公開の資料が1件でも入る"],
     ["参照先を公開済みの手順書だけに限る", "送信前に担当者が本文を確かめる"],
     "情報システム部と法務部"),
    ("手順書の更新が止まる",
     ["手順書の最終更新から3か月が過ぎる"],
     ["四半期ごとに手順書の棚卸しを行う", "更新の止まった手順は自動応答の対象から外す"],
     "情報システム部"),
    ("利用者に定着せず、問い合わせが電話に戻る",
     ["チャット経由の比率が3割を下回る"],
     ["電話の窓口を受付時間の後半に移す", "自動応答で解決した件数を月次で共有する"],
     "情報システム部"),
]


def ul(items):
    if len(items) == 1:
        return items[0]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


risk_rows = "".join(
    f'<tr><td class="rl">{name}</td><td>{ul(sig)}</td><td>{ul(act)}</td><td>{owner}</td></tr>'
    for name, sig, act, owner in risks
)
p11 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head(chips(4))}
    <h1 class="title">並べたリスクはいずれも兆候が先に出るため、基準値を決めて監視する</h1>
    <div class="rule"></div>
    <div class="content"><table class="risk-table">
      <thead><tr><th>起きうること</th><th>先に出る兆候（基準値）</th><th>対応策</th><th>担当部署</th></tr></thead>
      <tbody>{risk_rows}</tbody>
    </table></div>
    <footer class="footer"><span class="source">注：基準値は他社の運用例をもとにした仮置きで、10月の試験導入（情報システム部の20名）の実績を見て見直す</span><span>11</span></footer>
  </div>
</section>"""

# ── P.12 進め方 ────────────────────────────────────────────────────────
phases = [
    ("9月", "対象と承認を決める", "パスワード再発行の手順書を1本にまとめ、回答を確定する担当者を決める",
     "手順書1本と承認の決定"),
    ("10月", "部内で試験導入する", "部内の20名で使い、誤回答の出方と対応にかかった時間を記録する",
     "誤回答の記録と対応時間"),
    ("11月", "全社に開放する", "10月の誤回答が基準値を下回ることを確かめてから、全社の問い合わせを自動応答に回す",
     "自動応答で解決した件数"),
    ("12月以降", "対象を広げる", "経費精算の差し戻しを足し、削減できた工数を運営会議に報告する",
     "工数の実績と対象の判断"),
]
phase_html = "".join(
    f'<div class="phase"><div class="phase-year">{y}</div>'
    f'<div class="phase-title">{t}</div><div class="phase-copy">{c}</div>'
    f'<div class="phase-out">成果物：{o}</div></div>'
    for y, t, c, o in phases
)
p12 = f"""<section class="slide slide--no-title-rule">
  <div class="sinner">
{slide_head(chips(4))}
    <h1 class="title">対象はパスワード再発行から始め、12月以降に経費精算の差し戻しへ広げる</h1>
    <div class="rule"></div>
    <div class="content"><div class="rm-axis"></div><div class="roadmap">{phase_html}</div></div>
    <footer class="footer"><span class="source">注：11月の全社開放は、10月の試験導入で誤回答が P.11 の基準値を下回ることが条件</span><span>12</span></footer>
  </div>
</section>"""

# ── P.13 決めること ────────────────────────────────────────────────────
decide = [
    ("対象の種別", "パスワード再発行から始め、経費精算の差し戻しを12月以降に足す", "情報システム部長",
     ["10月の試験導入が11月以降にずれる", "12月の対象追加が年明けにずれる"]),
    ("承認の権限", "自動応答は下書きまでとし、回答は担当者が確かめて送る", "情報システム部長と経理部長",
     ["誤回答の責任の所在が決まらない", "運用の記録がないまま内部監査で提出を求められる"]),
    ("費用枠", "初期費用に80万円、運用に月15万円までとする", "情報システム部長",
     ["見積を依頼できない", "10月の試験導入を始められない"]),
]
dec_rows = "".join(
    f'<tr><td class="ax">{a}</td><td>{b}</td><td>{c}</td>'
    f'<td><ul class="cb">' + "".join(f"<li>{x}</li>" for x in d) + "</ul></td></tr>"
    for a, b, c, d in decide
)
p13 = f"""<section class="s tight">
{s_head(chips(4))}
  <h1>9月18日までに決めるのは、対象の種別、承認の権限、費用枠</h1>
  <div class="c">
    <table>
      <tr><th class="ax" style="width:40mm">決めること</th><th>提案の内容</th><th style="width:52mm">決める人</th><th style="width:72mm">先送りした場合に起きること</th></tr>
      {dec_rows}
    </table>
    <div class="src">注：費用枠は初期80万円、運用は月15万円を上限とする案で、金額は3社への概算照会を模した仮置き</div>
  </div>
{s_foot(13)}
</section>"""

# ── 裏表紙 ───────────────────────────────────────────────────────────
back = f"""<section class="s cover">
{s_head("2026年9月17日")}
  <div class="big" style="margin-top:60mm;font-size:22pt">A社 情報システム部 業務基盤グループ</div>
  <div class="sub">内線 2431／helpdesk-pj@example.co.jp</div>
  <div class="src" style="position:absolute;left:16mm;bottom:14mm">本資料は consulting-pptx-skill（github.com/carnot-tech/consulting-pptx-skill）と diagram-design（github.com/cathrynlavery/diagram-design）で作成</div>
  <div class="foot"><b>{LOGO}</b><span></span></div>
</section>"""

body = "\n".join([cover, p1, p2, p3, p4, p5, p6, p7, p10, p8, p9, p11, p12, p13, back])
head = head.replace("</style>", EXTRA_CSS + "</style>")
out = head + '<main class="deck skin-warm">\n' + body + "\n</main>\n</body>\n</html>\n"
(HERE / "deck.html").write_text(out, encoding="utf-8")
print("wrote deck.html", len(out))
