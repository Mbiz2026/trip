# 海外旅行ツール (trip)

ユーザーはコードを書けない。すべての操作はClaudeが代行し、結果だけを平易な日本語で報告すること。専門用語を使うときは一言で言い換えを添える。

## リポジトリ構成

```
travel_tools/
  kaigai_travel_kit.html   海外旅行おまもりキット(1ファイル完結・PWA自己完結型)
  flight_finder.html       航空券サーチ司令塔(Pages配信・PWA)
  mile_compass.html        マイルコンパス(Pages配信)
  dev/
    gen_mile_compass_cards.py   マイルコンパスの行き先カード+一覧表ジェネレータ(冪等)
  pwa/                     Pages配信用のPWA資材(manifest・sw.js・アイコン4枚)
.claude/
  commands/tabi-shiori.md      /tabi-shiori   旅のしおり生成
  commands/flight-mihari.md    /flight-mihari 航空券の価格・セール見張り(Routine)
  commands/mile-mihari.md      /mile-mihari   マイルコンパスの月次データ点検(Routine)
  hooks/session-start.sh       起動時にpython3とヘッドレスブラウザの有無を報告
  settings.json                権限(破壊的git操作を拒否)+ SessionStartフック登録
.github/workflows/pages.yml    3つのHTMLをGitHub Pagesへ自動配信
```

## 成果物6つ

### アプリ(HTML・各1ファイル)

1. **`travel_tools/kaigai_travel_kit.html` — 海外旅行おまもりキット**
   タブ: 🛂手続き / ✈️航空券 / 💱お金 / 🗣会話 / 🧳持ち物 / 🆘緊急。入国手続き・航空券の探し方・両替とチップ・指さし会話・持ち物チェック・緊急連絡先。オフライン動作。manifestとアイコンをdata URIで内蔵しており、**ファイル単体でホーム画面アプリになる**(下記パターンA)。JSは通貨計算機・チップ計算機・持ち物チェックの保存(localStorageキー接頭辞 `omamori:`)など。情報確認日 2026-07-10。

2. **`travel_tools/flight_finder.html` — 航空券サーチ司令塔**
   タブ: 🔍検索 / 🛩LCC図鑑 / 🧳手荷物 / 🧭裏ワザ / 🏷セール / 🔔見張り番。条件を1回入れると横断検索サイト+就航LCC公式への条件入りリンクを一括生成する**オンライン前提**アプリ。周辺空港・片道×片道・LCC図鑑(大手サイト掲載状況つき)・手荷物ルール早見・実質総額計算機・セールカレンダー・追跡メモ入り。ユーザーの出発空港の優先順は **伊丹→関空→神戸→羽田**(国際線の実質拠点は関空)。情報確認日 2026-07-11。

3. **`travel_tools/mile_compass.html` — マイルコンパス**
   タブ: 🧭さがす / 📊一覧表 / 💳マイル術 / 🎓取り方道場 / 📖基礎と出典。JALマイル×アメックスMR(メンバーシップ・リワード)特化の行き先さがし。26都市。**さがすタブの絞り込みはCSSの`:has()`だけで動く**(JS不要)。一覧表はJAL列とMR列を併記。取り方道場は6章のアコーディオン(JAL便PLUS・JAL提携・ANA・MR系外資・空席道具箱・家族実務)。保有マイル射程判定・MR移行シミュレータ・マイル価値計算機はJS時のみの追加機能。数字はすべて確認日付き、公式未確認値は**※**表記、経験則は二次情報と明記。情報確認日 2026-07-16。

### スラッシュコマンド(Claudeが動かす部分)

4. **`/tabi-shiori`** — 行き先と日程を伝えると、その渡航専用の「旅のしおり」HTMLを調査つきで生成(`travel_tools/shiori_<地名>_<YYYYMMDD>.html`)。
5. **`/flight-mihari`** — 航空券の7日間価格追跡/期間セール監視をRoutine(毎日1回・UTC22:00=JST朝7時)で代行し、基準額を下回ったら通知。取得失敗は正直に報告するベストエフォート設計。
6. **`/mile-mihari`** — マイルコンパスのデータ点検・更新手順。**毎月18日 朝9時(JST)のRoutineが新規セッションでこれを実行**し、燃油サーチャージ改定(2ヶ月ごと・偶数月中旬発表)やチャート改定を調査 → 公式+独立報道で裏どりできた確定情報だけをmainに反映(未確定は報告のみ・推測での更新は禁止)。

## 絶対に守ること

1. **JavaScriptが無くても主要機能が動くこと。** iPhoneの「ファイル」アプリ等のプレビュー表示はJavaScriptを実行しない。タブ切り替え・情報の閲覧は必ずCSSだけ(ラジオボタン+`:checked`、絞り込みは`:has()`)で動く構造にする。JavaScriptは計算機・検索・保存など「あれば便利」機能だけに使い、無くても情報は全部読めるようにする。**`<select>`の`<option>`や、初期表示テキストをJSで書き込む要素(`<p id="...">実行時に文字を入れる想定の空要素`など)は特に見落としやすい。** 新しい入力・選択UIを追加したら、必ずHTMLに静的な初期状態(optionの実体、フォールバック文言)を用意してからJSで上書きする設計にする。JS前提のボタンには`<noscript>`で「この開き方では動きません」と出す(3ファイルとも実装済み・文言を流用してよい)
2. **外部リソースを読み込まない。** CDN・Webフォント・外部画像は禁止。1ファイルで完結させ、オフラインで開けること(Pages配信分のmanifest/アイコン/sw.jsだけは例外で同一オリジンの別ファイル)
3. **事実は日付付きの公式ソースのみ。** 政府・大使館・航空会社等の公式サイトを優先し、記載には確認日を付ける。ブログ等の二次情報を使うときは二次情報だと明記し断定を避ける。ニセ代行サイトへの誘導は絶対にしない(公式リンクのみ案内する)。未確認値は`※`、判断できないものは「要確認」
4. **ライト/ダークテーマ両対応。** 生成物は必ず両方で見た目を確認する
5. **生成後は表示確認をする。** ヘッドレスブラウザで(JS有り/無しの両方)スクリーンショットを撮ってから納品する。無い環境ではユーザーに確認を依頼する
6. **迷ったら止まってユーザーに聞く。** 情報の鮮度・法規制が絡む分野(渡航制度・料金など)は特に慎重に。断定できないことは「要確認」と明記する

## 3アプリ共通のコード規約

新しいツールを足すときも、既存3ファイルの作りをそのまま踏襲する。

- **デザイントークン**: `<body>`直下の`<style>`で`:root`にCSS変数を定義 → `@media (prefers-color-scheme: dark)`で上書き → 念のため`:root[data-theme="light"]` / `:root[data-theme="dark"]`も定義。変数名は3ファイル共通(`--bg` `--surface` `--surface2` `--ink` `--muted` `--line` `--navy` `--accent` `--accent-soft` `--on-accent` `--warn` `--danger` `--ok` ほか)。ライトのアクセントは`#0D6B65`、ダーク背景は`#0F1726`(`theme-color`メタタグと一致させる)
- **フォント**: `--font-body`(ヒラギノ→游ゴシック→Noto Sans JP→system-ui)/ `--font-disp` / `--font-mono`。Webフォントは読まない
- **タブ**: `<input type="radio" name="tab" id="t-xxx" class="tabradio">`を`<nav>`の**前**に並べ、`<label class="tab" for="t-xxx">`と`#t-xxx:checked ~ ...`の兄弟セレクタで表示を切り替える。`:focus-visible`のスタイルも必ず付ける(キーボード操作)
- **JSは末尾の`<script>`1本だけ**。保存はlocalStorage、必ず`try/catch`で囲む(プライベートモード対策)。キーは`omamori:`のように接頭辞を付ける
- **ヘッダーに「情報確認日 YYYY-MM-DD」、フッターに「渡航前に公式サイトで再確認」の免責**を入れる。中身を更新したら確認日も更新する(逆に、中身を見ずに日付だけ進める「空更新」は禁止)

### マイルコンパスの生成部分(手で書き換えない)

行き先カードと一覧表は `travel_tools/dev/gen_mile_compass_cards.py` が生成する。HTML内の
`<!-- DESTCARDS:BEGIN -->`〜`<!-- DESTCARDS:END -->` と `<!-- LISTROWS:BEGIN -->`〜`<!-- LISTROWS:END -->` の間は
スクリプトが丸ごと差し替えるので直接編集しない。

```bash
# データ(スクリプト冒頭の燃油定数 KR/EA_J/… と D/LISTMETA)を編集してから
python3 travel_tools/dev/gen_mile_compass_cards.py   # 何度実行しても同じ結果(冪等)
```

一方で**「マイル術」タブの燃油早見表・MR移行表、「基礎と出典」タブのチャート表はHTML直書き**。燃油改定時は
ジェネレータとHTML直書きの両方を直す(片方だけ直すのがいちばんよくある事故)。

## 表示確認のやり方(セッション開始時のフックが利用可否とパスを教えてくれる)

```bash
<ヘッドレスブラウザのパス> --no-sandbox --disable-gpu --window-size=390,1300 --screenshot=out.png file:///絶対パス/foo.html
```

確認する組み合わせは **JSあり/なし × ライト/ダーク の4通り**。

既知の落とし穴:
- 直接起動はウィンドウ幅が最小500pxに切り上げられ、390px指定だと**画像の右端が切れて写る**(実際のはみ出しではない)
- `--blink-settings=scriptEnabled=false` はこのサンドボックス環境で `--screenshot`/`--dump-dom` とも無出力で失敗することがある(実績あり)。確実なのは `pip install playwright` して Python から `executable_path='/opt/pw-browsers/chromium'` で起動する方法。`viewport=390x844` が正しく効き、`color_scheme='dark'`(ダーク確認)や `java_script_enabled=False`(JSオフ確認)も指定できる
- Playwrightが使えない場合の次善策: HTMLの `<script>...</script>` を正規表現で丸ごと除去したコピーを作ってスクリーンショットを撮る(タブ切り替え・静的コンテンツの検証はこれで十分)。**ただし `<noscript>` の描画確認だけはこの代替策では不可能**(scriptタグが無いだけの状態と、エンジンがJS機能自体を無効化した状態は別物で、`<noscript>`は後者でしか展開されない)。`<noscript>`の中身は書いたら信頼し、機能的な検証は「JSが実際に無い状態で選択・入力しても壊れないか」に絞る
- `--virtual-time-budget`付きの`--dump-dom`は初期表示のHTMLを見るだけで、入力・選択などの「操作した結果」は検証できない。入力に応じて表示が変わる要素(検索・計算機・セレクトなど)を追加/修正したときは、対象HTMLの`</body>`直前に検証用の`<script>`(値を書き換えて`input`/`change`イベントを`dispatchEvent`し、結果を`<pre id="TEST_RESULTS">`に書き出す)を差し込んだコピーを作り、`--dump-dom`で結果を回収して確認する

## ワークフロー: 旅のしおり生成 (`/tabi-shiori`)

詳細は `.claude/commands/tabi-shiori.md` を参照。行き先・時期をWeb調査し、`travel_tools/kaigai_travel_kit.html` のデザイントークンとタブ構造を流用した、1ファイルのしおりHTMLを作る。

## 配信とアプリ化(PWA化)の2パターン

このリポジトリには「ホーム画面に追加すると独立アプリとして起動する」仕立てが2通りある。配布方法(単体ファイルか、Pages常設ホスティングか)に応じて使い分ける。

### パターンA: 単体HTMLファイルに埋め込み(`kaigai_travel_kit.html`)

manifest・アイコン・Apple系メタタグを全部`<head>`にdata URIで埋め込み、ファイル1つだけで完結させる方式。ユーザーにファイルを直接送る/AirDropする配布に向く。

- `<link rel="manifest" href="data:application/manifest+json;base64,...">` — name/short_name/display:standalone/icons等をJSONで書き、**base64エンコードしたdata URI**で埋め込む(生JSON+パーセントエンコードだと`"`等のエスケープが面倒なのでbase64が安全)
- `<meta name="apple-mobile-web-app-capable" content="yes">` などApple系メタタグ一式(iOSはmanifestよりこちら優先で長年対応してきた経緯があるので必ず両方入れる)
- `<link rel="apple-touch-icon" href="data:image/png;base64,...">` — アイコンはヘッドレスブラウザで512x512のHTML(角丸div+絵文字等)をスクリーンショットしてPNG化→base64化して作る(外部画像生成ツールは使わない)
- Service Workerは入れていない: ローカルファイルは`file://`オリジンのためSW登録不可(仕様上の制約)で、そもそもローカルファイルは常にオフライン
- ユーザーへの案内が無いと意味が無い機能なので、納品時は必ず「Safariの共有→ホーム画面に追加」の手順を日本語で添える(Quick Look等のプレビューから追加すると正しく動かないことがあるため、一度Safariのタブとして開いてから追加するよう案内する)

### パターンB: GitHub Pages常設ホスティング(`.github/workflows/pages.yml`)

`main`(および `claude/flight-search-app-55ozq4`)へのpushで、対象HTMLと`travel_tools/pwa/`をdistに集めて自動デプロイする。URLでアクセスする使い方(ブックマーク・ホーム画面リンク)に向く。

| 公開URL | 中身 |
|---|---|
| `/`(index.html) | `flight_finder.html` — manifest+sw.js登録あり(真のPWA) |
| `/mile.html` | `mile_compass.html` |
| `/omamori.html` | `kaigai_travel_kit.html`(manifest自己完結なので`pwa/`は使わない) |

- **本体HTMLを更新したら `travel_tools/pwa/sw.js` の `VERSION` を上げること**(現在 `trip-tools-v2`)。上げないと利用者側のキャッシュが更新されない
- `sw.js`の方針: ナビゲーションはネット優先→圏外時キャッシュ(リクエスト単位で保存。`'./'`固定にすると mile.html を開いたとき司令塔のキャッシュを上書きしてしまう)、静的ファイルはキャッシュ優先、外部オリジンは素通し
- SW登録は`flight_finder.html`の末尾だけが行い、`github.io`/`localhost`/`127.0.0.1`のときに限る(`file://`で開いたときにエラーを出さないため)。**`mile_compass.html`自身はmanifestもSW登録も持たない**ので、`/mile.html`のオフライン起動は「一度`/`を開いてSWが有効になっている」ことに依存する。mile.html単体をインストール可能にしたいなら、専用manifestとSW登録の追加が必要
- 前提: GitHub PagesはリポジトリがPublicか有料プランでのみ動く。デプロイ失敗時はまずここを疑う
- **新しいツールを追加したら `pages.yml` の `paths:` とdistコピー処理の両方に足す**(pathsに足し忘れると、そのファイルを更新してもデプロイが走らない)

## 稼働中のRoutine(定期実行)

このリポジトリ向けに、アカウント側で次の定期実行が登録されている(`list_triggers`で確認・`delete_trigger`で停止)。

| 名前 | cron(UTC) | 日本時間 | 中身 |
|---|---|---|---|
| mile-mihari | `0 0 18 * *` | 毎月18日 9:00 | 新規セッションで `/mile-mihari` の手順を実行 |
| 航空券セール見張り番 | `0 0 * * 1` | 毎週月曜 9:00 | 日本発国際線セールの週次レポート(コード変更はしない) |

`/flight-mihari` で作る見張りはこれとは別で、依頼のたびに7日間限定のRoutineを作り、期間終了時に自分で削除する。

## 開発のお作法

- 新しいツールを追加するときも「絶対に守ること」の1と2は例外なく適用する
- **作業ブランチ**は `claude/<内容>-<ランダム>` 形式。コミットメッセージは日本語で「何を・なぜ」を1行で(例: `通貨セレクトの選択肢が出ない不具合を修正、他の同種箇所も総点検`)。プルリクエストはユーザーに頼まれたときだけ作る
- `/mile-mihari` の数値・日付の差し替えだけは、裏どり基準を満たした場合に限り**mainへ直接コミット可**(ユーザー承認済み: 2026-07-16)。構造変更はブランチ+PRで相談する
- **破壊的なgit操作**(`rm -rf`・`git push --force`・`git reset --hard`・`git checkout -- `)は `.claude/settings.json` で拒否済み。それでも必要な場合はユーザーに確認する
- ツールの構成・タブ・ワークフローを変えたら、このCLAUDE.mdも同じコミットで更新する
