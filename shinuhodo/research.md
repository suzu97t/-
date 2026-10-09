# research.md —「死ぬほど疲れた」を本気で検証する

## 0. 決定事項

| 項目 | 決定 |
|---|---|
| 本筋 | **A：エネルギー破産** ＋ **B：持続可能な代謝の上限** |
| つかみ | **F：マラトンの伝令の伝説** |
| 不採用 | C（運動中の急性死）、D（断眠）、E（過労死ライン） |
| モデル人物 | 体重65kg、30代（35歳）男性、会社員、体脂肪率20%。身長170cmは仮置き（致死BMIの換算とMifflin式の照合にだけ使う） |

---

## 1. 解釈の候補（Step 1 の記録）

| # | 解釈 | 検証可能性 | 面白さ | 採否 |
|---|---|---|---|---|
| A | エネルギー破産：食べずに動き続け、体脂肪を使い切る | ◎ 体組成、METs、断食・飢餓の報告がそろう | ◎「体の貯金の○%」というオチにしやすい | **採用** |
| B | 持続可能な代謝の上限：基礎代謝の約2.5倍（Thurber 2019） | ◎ 査読論文。数値が明快 | ○〜◎「体はまだ黒字」というオチ | **採用** |
| C | 運動中の急性死（熱中症・横紋筋融解症・低ナトリウム血症） | △ 運動量で決まる閾値がない | △ 真似すると危険な領域 | 不採用 |
| D | 断眠の限界（ガードナー264時間、ラット11〜32日） | ○ ヒトの致死ラインは不明 | ◎ ただし「眠い」の話になる | 不採用 |
| E | 過労死ライン（月80時間・100時間） | ◎ 公的基準 | ○ 笑いにすると炎上リスクがある | 不採用 |
| F | マラトンの伝令（「死んだ伝令」は後世の創作） | ✕ 計算の土台にはならない | ◎ つかみ | **つかみに採用** |

### 採用理由
- A＋Bは、一次情報で「ライン」を引ける。
- 数字がすべてkcal（またはその比）という同じ単位にそろう。
- Fは史実性が低いので、数値の土台には使わない。「もしあなたが同じ距離を走ったら」という換算にだけ使う。

---

## 2. 数値と出典の一覧

### 確認状況の凡例
- **確認済**：出典本文、または出典を直接引用した記述で数値を確認した
- **二次確認**：教科書・解説・引用論文の記述で確認した。一次資料の本文は未確認
- **要照合**：版やコード番号が一次資料と完全には照合できていない。公開前に確認が必要
- **推定**：出典がない。推定の根拠を記載

> **調査環境の制約**：この作業環境からは、厚労省、PMC、pacompendium.com など多くの一次資料サイトに直接アクセスできなかった（ネットワークポリシーで拒否）。数値は、検索エンジン経由で取得できた本文の抜粋・要約で確認している。**動画公開前に「要照合」「二次確認」の行を一次資料で確認することを推奨します。**

### 2-1. モデル人物の代謝

| 値 | 数値 | 条件 | 出典 | 確認状況 |
|---|---|---|---|---|
| 基礎代謝基準値 | 22.5 kcal/kg/日 | 日本人男性 30〜49歳 | 厚生労働省「日本人の食事摂取基準（2025年版）」 https://www.mhlw.go.jp/content/10904750/001316480.pdf | 二次確認（2020年版の表に22.3と読める記載もあり、要照合） |
| 基礎代謝量 | 1,462 kcal/日 | 上記 × 65 kg | 計算 | — |
| 身体活動レベル | 1.50 / 1.75 / 2.00 | 低い / ふつう / 高い。成人 | 同上 | 二次確認 |
| METs → kcal の換算式 | kcal = 1.05 × METs × 時間 × 体重 | 成人 | 厚生労働省「健康づくりのための身体活動基準2013」 | 二次確認 |
| 食事誘発性熱産生 | 総消費の約10% | 通常の混合食 | Westerterp KR. Diet induced thermogenesis. *Nutr Metab* 2004;1:5 | 二次確認（教科書的な値） |
| 照合用：Mifflin-St Jeor 式 | 10W + 6.25H − 5A + 5 | 男性 | Mifflin MD et al. *Am J Clin Nutr* 1990 | 広く使われる式 |

### 2-2. 活動のMETs（Compendium of Physical Activities）

出典：Ainsworth BE et al. 2011 Compendium of Physical Activities. *Med Sci Sports Exerc* 2011;43:1575–81。2024年版は Herrmann SD et al. *J Sport Health Sci* 2024;13:6–12（https://pubmed.ncbi.nlm.nih.gov/38242596/ 、一覧は https://pacompendium.com）。

2024年版では176項目の値が改訂されている。**以下は2011年版のコードと値**である。2024年版での値は要照合。

| 活動 | METs | コード（2011） | 確認状況 |
|---|---|---|---|
| 睡眠 | 0.95 | 07030 sleeping | 確認済（Compendium表の引用） |
| 静かに座る（帰宅後の放心） | 1.3 | 07021 sitting quietly, general | 二次確認 |
| 静かに立つ（満員電車） | 1.3 | 07040 standing quietly | 二次確認。2024年版準拠をうたう第三者表では「standing in a line」が2.0 → 感度分析で振った |
| デスクワーク | 1.5 | 11580 sitting tasks, light effort (office work) | 確認済（引用あり） |
| 通勤の徒歩 | 3.5 | 17200 walking 2.8–3.2 mph, level, moderate | 確認済（2011年版） |
| 社内移動 | 2.8 | 17152 walking 2.0 mph, slow | 要照合 |
| 駅の階段 | 4.0 | 17130 stair climbing, slow pace | 要照合 |
| 身支度 | 2.5 | 13020 dressing, undressing | 要照合 |
| 食事 | 1.5 | 13030 eating, sitting | 要照合 |
| シャワー | 2.0 | — | **推定**（身の回り動作の低強度値で代用。0.25時間なので影響は約±10 kcal） |
| 引越し作業 | 5.8 | 05120 moving household items, carrying boxes | 要照合 |

### 2-3. 体のエネルギー貯蔵（A）

| 値 | 数値 | 条件 | 出典 | 確認状況 |
|---|---|---|---|---|
| 体脂肪のエネルギー密度 | 39.5 MJ/kg（≒9,441 kcal/kg） | 体重変化モデルの定数 | Hall KD ら（Lancet 2011 補遺 https://www.niddk.nih.gov/-/media/Files/BWP/Hall_Lancet_Web_Appendix.pdf 、Chow & Hall 2008 https://pmc.ncbi.nlm.nih.gov/articles/PMC2376744 ） | 確認済（補遺の記述を引用で確認） |
| 除脂肪組織のエネルギー密度 | 7.6 MJ/kg（≒1,816 kcal/kg） | 同上 | 同上 | 確認済 |
| 脂肪と除脂肪組織への分配 | p = C/(C+F)、C = 10.4 kg × ρL/ρF | Forbes型 | 同上 | 確認済 |
| 「1kg = 7,700 kcal」則 | 7,700 kcal/kg | 脂肪組織（脂質87%）の換算 | Hall KD. *Int J Obes* 2008;32:573 https://pubmed.ncbi.nlm.nih.gov/17848938/ | 確認済（感度分析で使用） |
| 必須脂肪 | 体重の約3%（男性） | 成人男性 | 運動生理学の教科書（Behnke のモデルに由来） https://us.humankinetics.com/blogs/excerpt/normal-ranges-of-body-weight-and-body-fat | 二次確認 |
| グリコーゲン | 肝臓 約100 g、筋 約400 g | 成人、摂食時 | Lippincott Illustrated Reviews: Biochemistry（抜粋） | 二次確認。kcal換算（約4 kcal/g → 約2,000 kcal）は計算 |
| 飢餓死と脂肪 | 死亡は脂肪の蓄えが尽きかけた時点と重なる | 1981年アイルランドのハンスト報道の分析 | Leiter LA, Marliss EB. *JAMA* 1982;248:2306–7 | 二次確認（抄録レベル） |
| 飢餓の致死ライン | 男性で **BMI 約13** | 飢餓の報告の総説 | ENN Field Exchange 15「The limits of human starvation」 https://ennonline.net/fex/15/limits | 二次確認 |
| 同上（別の言い方） | 体重の40〜50%減で生命の危険 | 一般向け解説 | BBC Science Focus https://www.sciencefocus.com/the-human-body/who-would-die-first-of-starvation-a-fat-or-a-thin-person/ | 二次確認（照合用） |
| ハンストの死亡例 | ボビー・サンズ：絶食66日目に死亡（1981年） | 水分は摂取 | Britannica https://britannica.com/biography/Bobby-Sands 、Irish Post | 確認済（照合用） |

### 2-4. 持続可能な上限（B）

| 値 | 数値 | 条件 | 出典 | 確認状況 |
|---|---|---|---|---|
| 消化吸収による上限 | 基礎代謝の **約2.5倍** | 長期（数週間以上）。耐久イベントと過食研究を統合 | Thurber C et al. *Sci Adv* 2019;5:eaaw0341 https://dukespace.lib.duke.edu/items/c8cfa63c-8ba3-44e9-986f-3bb4e4d11c6f/full | 確認済（抄録） |
| 持続可能な代謝倍率の推移 | 期間が長いほど下がり、3倍未満で頭打ち | 0.5日〜250日超のイベント | 同上 | 確認済（抄録） |
| 大陸横断レース走者の総消費 | 22.39〜25.95 MJ/日（≒5,350〜6,200 kcal） | 2015 Race Across the USA、約140日、二重標識水法 | Thurber C. 修士論文（CUNY Hunter, 2016） https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1065&context=hc_sas_etds | 二次確認（2019年論文の値とは一致しない可能性あり） |

### 2-5. 伝令（F）

| 値 | 数値 | 出典 | 確認状況 |
|---|---|---|---|
| ペイディッピデスはアテネを発った翌日にスパルタへ着いた | — | ヘロドトス『歴史』6.105–106 https://lexundria.com/hdt/6.106/mcly | 確認済 |
| アテネ→スパルタの距離 | 約240 km（現代の推定。ヘロドトスは距離を書いていない。スパルタスロンは246 km） | Wikipedia ほか | 二次確認 |
| 「マラトンから走って勝利を告げ、死んだ」話 | 2世紀のルキアノスが最初。プルタルコスは伝令名をエウクレスなどとする | https://penelope.uchicago.edu/Thayer/E/Journals/CW/24/19/Marathon_Runner*.html | 確認済 |
| ランニングの正味エネルギーコスト | 約1 kcal/kg/km（速度によらない） | Margaria R et al. *J Appl Physiol* 1963;18:367 https://pubmed.ncbi.nlm.nih.gov/13932993/ 。後続研究では0.86〜0.97 | 二次確認 |
| マラトン→アテネの距離 | 約40 km（概数） | 一般的な記述 | 推定（概数） |

### 2-6. 比較用

| 値 | 数値 | 出典 | 確認状況 |
|---|---|---|---|
| バナナ | 93 kcal / 可食部100 g | 文部科学省「日本食品標準成分表（八訂）」 | 要照合（1本の可食部を約100 gとみなすのは推定） |

---

## 3. 参照したが本筋では使わなかった出典（C・D・E）

- ACSM Expert Consensus Statement on Exertional Heat Illness (2023)
- Exertional Rhabdomyolysis in Athletes: Systematic Review (2023) https://pubmed.ncbi.nlm.nih.gov/36877581/
- NPR「Lessons from sleeplessness」(2024) https://www.npr.org/2024/01/28/1227217274/sleep-deprivation-record
- 厚生労働省 脳・心臓疾患の労災認定基準（2021年改正）
