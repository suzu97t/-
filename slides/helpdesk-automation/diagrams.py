# -*- coding: utf-8 -*-
"""デッキに載せる図（diagram-design スキルの作法で描く）。

スキン: diagram-design の semantic role に consulting-pptx-skill の暖色トークンを割り当てる。
  paper=#ffffff（スライドの地）／ink=#322014／muted=#8a7b6b／accent=#5a3921
  accent-tint=rgba(90,57,33,0.10)／store=ink@0.05／external=ink@0.03・stroke ink@0.30
規約が食い違うところは slide-rules（正典）を優先する: 箱の角丸は rx=0。
フローチャートの開始記号だけは形が種類を表すので楕円を残す。
座標・寸法・フォントは4の倍数（diagram-design §7）。全幅の図は viewBox 1120×388 で版面（306.67mm × 約107mm）に収まり、
12単位の文字が9.3ptになる（slide-rules §6 の9pt下限）。
"""

PAPER = "#ffffff"
INK = "#322014"
MUTED = "#8a7b6b"
ACCENT = "#5a3921"
TINT = "rgba(90,57,33,0.10)"
STORE = "rgba(50,32,20,0.05)"
EXT_FILL = "rgba(50,32,20,0.03)"
EXT_STROKE = "rgba(50,32,20,0.30)"
HAIR = "rgba(50,32,20,0.12)"


def _defs(pid):
    return (
        f'<defs>'
        f'<marker id="{pid}-arw" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
        f'<polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>'
        f'<marker id="{pid}-arw-ac" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
        f'<polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>'
        f'</defs>'
    )


def _open(pid, w, h, title, desc):
    return (
        f'<svg class="dg" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="{pid}-title {pid}-desc">'
        f'<title id="{pid}-title">{title}</title>'
        f'<desc id="{pid}-desc">{desc}</desc>'
        f'{_defs(pid)}'
        f'<rect width="100%" height="100%" fill="{PAPER}"/>'
    )


def _txt(x, y, s, size=12, fill=INK, weight=600, anchor="middle"):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{s}</text>')


def _node(x, y, w, h, lines, kind="backend", sub=True):
    """ノード。lines は1〜2行。sub=False なら2行目も名前として扱う。kind: backend / focal / store / external"""
    fill, stroke, sw = PAPER, INK, 1
    if kind == "focal":
        fill, stroke, sw = TINT, ACCENT, 1.2
    elif kind == "store":
        fill, stroke = STORE, MUTED
    elif kind == "external":
        fill, stroke = EXT_FILL, EXT_STROKE
    cx, cy = x + w // 2, y + h // 2
    name = ACCENT if kind == "focal" else INK
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>']
    if len(lines) == 1:
        out.append(_txt(cx, cy + 4, lines[0], 12, name, 600))
    else:
        out.append(_txt(cx, cy - 4, lines[0], 12, name, 600))
        out.append(_txt(cx, cy + 12, lines[1], 12, MUTED if sub else name, 400 if sub else 600))
    return "".join(out)


def _alabel(cx, line_y, s, fill=MUTED, gap=8):
    """横線につけるラベル。マスク下端と線の間に gap をあける（diagram-design §6 規則2）。"""
    w = len(s) * 12 + 8
    x0 = cx - w // 2
    y0 = line_y - gap - 16
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="16" fill="{PAPER}"/>'
            + _txt(cx, y0 + 12, s, 12, fill, 500))


def _vlabel(line_x, line_y, s, fill=MUTED, gap=8):
    """縦線につけるラベル。線の右側に gap をあけて置く（縦書きにはしない）。"""
    w = len(s) * 12 + 8
    x0 = line_x + gap
    return (f'<rect x="{x0}" y="{line_y - 8}" width="{w}" height="16" fill="{PAPER}"/>'
            + _txt(x0 + 4, line_y + 4, s, 12, fill, 500, "start"))


def _legend(y, items, width=1120):
    """凡例は図の下の横一列（diagram-design §6）。items: [(種類, ラベル)]"""
    out = [f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{HAIR}" stroke-width="0.8"/>',
           _txt(0, y + 24, "凡例", 12, MUTED, 500, "start")]
    x, cy = 64, y + 20
    for kind, label in items:
        if kind == "accent":
            out.append(f'<rect x="{x}" y="{cy - 8}" width="16" height="16" fill="{TINT}" stroke="{ACCENT}" stroke-width="1.2"/>')
        elif kind == "white":
            out.append(f'<rect x="{x}" y="{cy - 8}" width="16" height="16" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
        elif kind == "store":
            out.append(f'<rect x="{x}" y="{cy - 8}" width="16" height="16" fill="{STORE}" stroke="{MUTED}" stroke-width="1"/>')
        elif kind == "external":
            out.append(f'<rect x="{x}" y="{cy - 8}" width="16" height="16" fill="{EXT_FILL}" stroke="{EXT_STROKE}" stroke-width="1"/>')
        elif kind == "dot-accent":
            out.append(f'<circle cx="{x + 8}" cy="{cy}" r="8" fill="{ACCENT}"/>')
        elif kind == "dot-muted":
            out.append(f'<circle cx="{x + 8}" cy="{cy}" r="8" fill="{MUTED}"/>')
        elif kind == "dash":
            out.append(f'<line x1="{x}" y1="{cy}" x2="{x + 24}" y2="{cy}" stroke="{MUTED}" '
                       f'stroke-width="1" stroke-dasharray="4,3"/>')
        w = 24 if kind == "dash" else 16
        out.append(_txt(x + w + 8, cy + 4, label, 12, INK, 400, "start"))
        x += w + 8 + len(label) * 12 + 40
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────
# 図1: 2×2（対象の選び方）— 位置に意味がある標準クアドラント
# ─────────────────────────────────────────────────────────────────────────
def quadrant():
    pid = "qd"
    o = [_open(pid, 1120, 388,
               "自動応答に向く問い合わせ種別の位置づけ",
               "縦軸は月あたりの件数、横軸は手順の定まり。右上にパスワード再発行と経費精算の差し戻しが位置し、"
               "ほかの6種別は手順の定まりが弱いか件数が少ない。")]
    o.append(f'<line x1="560" y1="328" x2="560" y2="48" stroke="{INK}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="160" y1="184" x2="1000" y2="184" stroke="{INK}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(_txt(560, 32, "件数", 12, INK, 500))
    o.append(_txt(1008, 188, "手順の定まり", 12, INK, 500, "start"))
    o.append(_txt(972, 56, "自動応答に向く", 12, MUTED, 500, "end"))
    items = [
        (880, 84, "パスワード再発行", "start", True),
        (768, 132, "経費精算の差し戻し", "start", True),
        (712, 232, "会議室と備品の貸出", "start", False),
        (456, 228, "権限の申請", "start", False),
        (352, 264, "端末の不調", "start", False),
        (516, 288, "経費規程の確認", "end", False),
        (296, 308, "ソフトウェアの導入依頼", "start", False),
        (232, 324, "その他", "start", False),
    ]
    for x, y, label, anchor, focal in items:
        o.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{ACCENT if focal else MUTED}"/>')
        lx = x + 16 if anchor == "start" else x - 16
        o.append(_txt(lx, y + 4, label, 12, INK if focal else MUTED, 600 if focal else 400, anchor))
    o.append(_legend(348, [("dot-accent", "自動応答に置き換える種別"), ("dot-muted", "人が受け続ける種別")]))
    o.append("</svg>")
    return "".join(o)


# ─────────────────────────────────────────────────────────────────────────
# 図2: スイムレーン（自動応答を入れたあとの流れ）
# ─────────────────────────────────────────────────────────────────────────
def swimlane():
    pid = "sw"
    o = [_open(pid, 1120, 388,
               "自動応答を入れたあとの一次対応の流れ",
               "利用者・自動応答・担当者の3レーン。利用者の依頼を自動応答が判定して下書きを作り、"
               "担当者が確かめて送る。対象外の問い合わせは自動応答から担当者へ引き継ぐ。")]
    for y in (32, 120, 208, 296):
        o.append(f'<line x1="0" y1="{y}" x2="1120" y2="{y}" stroke="rgba(50,32,20,0.20)" stroke-width="0.8"/>')
    for name, cy in (("利用者", 76), ("自動応答", 164), ("担当者", 252)):
        o.append(_txt(0, cy + 4, name, 12, MUTED, 500, "start"))
    # 矢印を先に描いて箱の下に回す
    o.append(f'<path d="M 320,76 H 424 Q 432,76 432,84 V 140" fill="none" stroke="{MUTED}" '
             f'stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="512" y1="164" x2="544" y2="164" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<path d="M 704,164 H 808 Q 816,164 816,172 V 228" fill="none" stroke="{ACCENT}" '
             f'stroke-width="1.2" marker-end="url(#{pid}-arw-ac)"/>')
    o.append(f'<path d="M 896,252 H 1000 Q 1008,252 1008,244 V 100" fill="none" stroke="{MUTED}" '
             f'stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<path d="M 432,188 V 244 Q 432,252 440,252 H 736" fill="none" stroke="{MUTED}" '
             f'stroke-width="1" stroke-dasharray="4,3" marker-end="url(#{pid}-arw)"/>')
    o.append(_alabel(376, 76, "依頼"))
    o.append(_alabel(756, 164, "下書き", ACCENT))
    o.append(_alabel(584, 252, "対象外は担当者へ"))
    o.append(_node(160, 52, 160, 48, ["チャットで依頼"]))
    o.append(_node(352, 140, 160, 48, ["対象の種別か調べる"]))
    o.append(_node(544, 140, 160, 48, ["手順書から", "下書きを作る"], sub=False))
    o.append(_node(736, 228, 160, 48, ["確かめて送る"], "focal"))
    o.append(_node(928, 52, 160, 48, ["回答を受け取る"]))
    o.append(_legend(348, [("accent", "担当者が確定する工程"), ("dash", "対象外の引き継ぎ")]))
    o.append("</svg>")
    return "".join(o)


# ─────────────────────────────────────────────────────────────────────────
# 図3: アーキテクチャ（つくる範囲）
# ─────────────────────────────────────────────────────────────────────────
def architecture():
    pid = "ar"
    o = [_open(pid, 1120, 388,
               "自動応答の構成とつくる範囲",
               "既存のチャットに自動応答をつなぎ、自動応答は公開済みの手順書の索引を参照して下書きを作る。"
               "担当者は確認画面で内容を確かめて送り、やり取りは記録に残る。")]
    # ゾーン（背景→ゾーン→矢印→ラベル→ノードの順）
    o.append(f'<rect x="304" y="64" width="480" height="224" fill="rgba(50,32,20,0.02)" '
             f'stroke="{HAIR}" stroke-width="0.8" stroke-dasharray="4,4"/>')
    o.append(f'<rect x="320" y="68" width="96" height="16" fill="{PAPER}"/>')
    o.append(_txt(320, 80, "今回つくる範囲", 12, MUTED, 500, "start"))
    # 矢印
    o.append(f'<line x1="232" y1="128" x2="336" y2="128" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="536" y1="128" x2="568" y2="128" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="768" y1="128" x2="832" y2="128" stroke="{ACCENT}" stroke-width="1.2" marker-end="url(#{pid}-arw-ac)"/>')
    o.append(f'<line x1="436" y1="160" x2="436" y2="216" stroke="{MUTED}" stroke-width="1" '
             f'stroke-dasharray="4,3" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="668" y1="160" x2="668" y2="216" stroke="{MUTED}" stroke-width="1" '
             f'stroke-dasharray="4,3" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<path d="M 932,160 V 308 Q 932,316 924,316 H 140 Q 132,316 132,308 V 160" fill="none" '
             f'stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    # 矢印ラベル
    o.append(_alabel(284, 128, "問い合わせ"))
    o.append(_alabel(800, 128, "下書き", ACCENT))
    o.append(_vlabel(436, 192, "参照"))
    o.append(_vlabel(668, 192, "記録"))
    o.append(_alabel(532, 316, "確定した回答"))
    # ノード
    o.append(_node(32, 96, 200, 64, ["既存のチャット", "利用者の窓口"]))
    o.append(_node(336, 96, 200, 64, ["自動応答", "下書きを作る"], "focal"))
    o.append(_node(568, 96, 200, 64, ["担当者の確認画面", "直して送る"]))
    o.append(_node(336, 216, 200, 56, ["手順書の索引", "公開済みだけ"], "store"))
    o.append(_node(568, 216, 200, 56, ["やり取りの記録", "監査で見る"], "store"))
    # 担当者は人なので単色アイコン＋ラベルで表す（slide-rules §4.32）
    o.append(f'<rect x="832" y="96" width="200" height="64" fill="{PAPER}"/>')
    o.append(f'<rect x="832" y="96" width="200" height="64" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<circle cx="864" cy="116" r="8" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    o.append(f'<path d="M 852,140 a 12,12 0 0,1 24,0" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    o.append(_txt(888, 124, "担当者", 12, INK, 600, "start"))
    o.append(_txt(888, 140, "内容を確かめる", 12, MUTED, 400, "start"))
    o.append(_legend(348, [("accent", "つくる自動応答"), ("white", "人が使う画面と担当者"),
                           ("store", "参照と保管")]))
    o.append("</svg>")
    return "".join(o)


# ─────────────────────────────────────────────────────────────────────────
# 図4: フローチャート（担当者に回す判定）— 左カラム用に幅 640
# ─────────────────────────────────────────────────────────────────────────
def flowchart():
    pid = "fc"
    w = 640
    o = [_open(pid, w, 400,
               "自動応答が答えるか担当者に回すかの判定",
               "問い合わせが届いたら、対象の種別かを判定し、手順書が最新かを判定する。"
               "どちらかが否なら担当者が自分で調べて回答し、両方が是なら自動応答が下書きを作って担当者が送る。")]
    # 矢印
    o.append(f'<line x1="200" y1="40" x2="200" y2="60" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="200" y1="148" x2="200" y2="180" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<line x1="200" y1="268" x2="200" y2="296" stroke="{ACCENT}" stroke-width="1.2" marker-end="url(#{pid}-arw-ac)"/>')
    o.append(f'<path d="M 288,104 H 352 Q 360,104 360,112 V 172 Q 360,180 368,180" fill="none" '
             f'stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    o.append(f'<path d="M 288,224 H 480 Q 488,224 488,216 V 208" fill="none" '
             f'stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{pid}-arw)"/>')
    # 矢印ラベル
    o.append(_vlabel(200, 164, "はい"))
    o.append(_vlabel(200, 280, "はい", ACCENT))
    o.append(_alabel(320, 104, "いいえ"))
    o.append(_alabel(330, 224, "いいえ"))
    # 開始（形が種類を表す記号なので楕円のまま）
    o.append(f'<rect x="112" y="0" width="176" height="40" rx="20" fill="{EXT_FILL}" stroke="{EXT_STROKE}" stroke-width="1"/>')
    o.append(_txt(200, 24, "問い合わせが届く", 12, INK, 600))
    # 判定（ダイヤ）
    for cy, l1, l2 in [(104, "対象の種別か", None), (224, "手順書が", "最新か")]:
        o.append(f'<polygon points="200,{cy - 44} 288,{cy} 200,{cy + 44} 112,{cy}" fill="{PAPER}" '
                 f'stroke="{INK}" stroke-width="1"/>')
        if l2:
            o.append(_txt(200, cy - 4, l1, 12, INK, 600))
            o.append(_txt(200, cy + 12, l2, 12, INK, 600))
        else:
            o.append(_txt(200, cy + 4, l1, 12, INK, 600))
    # 工程
    o.append(_node(112, 296, 176, 48, ["下書きを作り", "担当者が送る"], "focal", sub=False))
    o.append(_node(368, 152, 240, 56, ["担当者が自分で", "調べて回答する"], sub=False))
    o.append(_legend(360, [("accent", "自動応答が下書きを作る経路"), ("white", "担当者が受ける経路")], w))
    o.append("</svg>")
    return "".join(o)
