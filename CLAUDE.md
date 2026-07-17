# 海外旅行ツール (trip)

ユーザーはコードを書けない。すべての操作はClaudeが代行し、結果だけを平易な日本語で報告すること。

## このリポジトリについて

海外旅行者向けの実用ツールを作る。今のところ4つ:

1. `travel_tools/kaigai_travel_kit.html` — 入国手続き・航空券の探し方・両替とチップ・指さし会話・持ち物・緊急連絡先をまとめた、オフラインで動くスマホ用Webアプリ(1ファイル)。ホーム画面に追加すると独立したアプリとして起動する(PWA化済み。詳細は末尾「ホーム画面アプリ化」参照)
2. `/tabi-shiori` コマンド(`.claude/commands/tabi-shiori.md`) — 行き先と日程を伝えると、その渡航専用の「旅のしおり」HTMLを調査つきで生成する
3. `travel_tools/flight_finder.html` — 「航空券サーチ司令塔」。条件を1回入れると横断検索サイト+就航LCC公式への条件入りリンクを一括生成するオンライン前提アプリ(1ファイル)。周辺空港・片道×片道・LCC図鑑(大手サイト掲載状況つき)・手荷物ルール早見・実質総額計算機・セールカレンダー・追跡メモ入り。ユーザーの出発空港の優先順は 伊丹→関空→神戸→羽田(国際線の実質拠点は関空)
4. `/flight-mihari` コマンド(`.claude/commands/flight-mihari.md`) — 航空券の7日間価格追跡/期間セール監視をRoutine(毎日1回)で代行し、基準額を下回ったら通知。取得失敗は正直に報告するベストエフォート設計
5. `travel_tools/mile_compass.html` — 「マイルコンパス」。JALマイル×アメックスMR(メンバーシップ・リワード)特化の行き先さがしアプリ(1ファイル・オフライン動作)。5タブ構成: 🧭さがす(条件チップで26都市を絞り込み・CSSの`:has`のみで動作)/📊一覧表(JAL列とMR列を併記した段組み)/💳マイル術(MR移行先・燃油早見・燃油回避ワザ)/🎓取り方道場(特典航空券の取り方の基礎と裏技を6章のアコーディオンで解説。JAL便PLUS・JAL提携・ANA・MR系外資・空席道具箱・家族実務)/📖基礎と出典。保有マイル射程判定・MR移行シミュレータ・マイル価値計算機はJS時のみ。数字はすべて確認日付き、公式未確認値は※表記・経験則は二次情報と明記。行き先カードと一覧表は `travel_tools/dev/gen_mile_compass_cards.py` で生成(冪等。データ編集→再実行で差し替わる)。GitHub Pagesでは `/mile.html` として配信(pages.ymlが自動デプロイ)
6. `/mile-mihari` コマンド(`.claude/commands/mile-mihari.md`) — マイルコンパスのデータ点検・更新手順。**毎月18日 朝9時(JST)のRoutineが新規セッションでこれを実行**し、燃油サーチャージ改定(2ヶ月ごと・偶数月中旬発表)やチャート改定を調査→公式+独立報道で裏どりできた確定情報だけをmainに反映する(未確定は報告のみ・推測での更新は禁止)

## 絶対に守ること

1. **JavaScriptが無くても主要機能が動くこと。** iPhoneの「ファイル」アプリ等のプレビュー表示はJavaScriptを実行しない。タブ切り替え・情報の閲覧は必ずCSSだけ(ラジオボタン+`:checked`等)で動く構造にする。JavaScriptは計算機・検索・チェックの保存など「あれば便利」機能だけに使い、無くても情報は全部読めるようにする。**`<select>`の`<option>`や、初期表示テキストをJSで書き込む要素(`<p id="...">実行時に文字を入れる想定の空要素`など)は特に見落としやすい。** 新しい入力・選択UIを追加したら、必ずHTMLに静的な初期状態(optionの実体、フォールバック文言)を用意してからJSで上書きする設計にする
2. **外部リソースを読み込まない。** CDN・Webフォント・外部画像は禁止。1ファイルで完結させ、オフラインで開けること
3. **事実は日付付きの公式ソースのみ。** 政府・大使館・航空会社等の公式サイトを優先し、記載には確認日を付ける。ブログ等の二次情報を使うときは二次情報だと明記し断定を避ける。ニセ代行サイトへの誘導は絶対にしない(公式リンクのみ案内する)
4. **ライト/ダークテーマ両対応。** 生成物は必ず両方で見た目を確認する
5. **生成後は表示確認をする。** ヘッドレスブラウザで(JS有り/無しの両方)スクリーンショットを撮ってから納品する。無い環境ではユーザーに確認を依頼する
6. **迷ったら止まってユーザーに聞く。** 情報の鮮度・法規制が絡む分野(渡航制度・料金など)は特に慎重に。断定できないことは「要確認」と明記する

## 表示確認のやり方(セッション開始時のフックが利用可否を教えてくれる)

```bash
<ヘッドレスブラウザのパス> --no-sandbox --disable-gpu --window-size=390,1300 --screenshot=out.png file:///絶対パス/foo.html
```

既知の落とし穴:
- 直接起動はウィンドウ幅が最小500pxに切り上げられ、390px指定だと**画像の右端が切れて写る**(実際のはみ出しではない)
- `--blink-settings=scriptEnabled=false` はこのサンドボックス環境で `--screenshot`/`--dump-dom` とも無出力で失敗することがある(実績あり)。確実なのは `pip install playwright` して Python から `executable_path='/opt/pw-browsers/chromium'` で起動する方法。`viewport=390x844` が正しく効き、`color_scheme='dark'`(ダーク確認)や `java_script_enabled=False`(JSオフ確認)も指定できる。実装例: 過去セッションの `shoot.py`(scratchpad)
- Playwrightが使えない場合の次善策: HTMLの `<script>...</script>` を正規表現で丸ごと除去したコピーを作ってスクリーンショットを撮る(タブ切り替え・静的コンテンツの検証はこれで十分)。**ただし `<noscript>` の描画確認だけはこの代替策では不可能**(scriptタグが無いだけの状態と、エンジンがJS機能自体を無効化した状態は別物で、`<noscript>`は後者でしか展開されない)。`<noscript>`の中身は書いたら信頼し、機能的な検証は「JSが実際に無い状態で選択・入力しても壊れないか」に絞る
- `--virtual-time-budget`付きの`--dump-dom`は初期表示のHTMLを見るだけで、入力・選択などの「操作した結果」は検証できない。入力に応じて表示が変わる要素(検索・計算機・セレクトなど)を追加/修正したときは、対象HTMLの`</body>`直前に検証用の`<script>`(値を書き換えて`input`/`change`イベントを`dispatchEvent`し、結果を`<pre id="TEST_RESULTS">`に書き出す)を差し込んだコピーを作り、`--dump-dom`で結果を回収して確認する

## ワークフロー: 旅のしおり生成 (`/tabi-shiori`)

詳細は `.claude/commands/tabi-shiori.md` を参照。行き先・時期をWeb調査し、`travel_tools/kaigai_travel_kit.html` とデザインの統一感を保った、1ファイルのしおりHTMLを作る。

## アプリ化(PWA化)の2パターン

このリポジトリには「ホーム画面に追加すると独立アプリとして起動する」仕立てが2通りある。ツールの配布方法(単体ファイルか、Pages常設ホスティングか)に応じて使い分ける。

### パターンA: 単体HTMLファイルに埋め込み(`kaigai_travel_kit.html`)

manifest・アイコン・Apple系メタタグを全部`<head>`にdata URIで埋め込み、ファイル1つだけで完結させる方式。ユーザーにファイルを直接送る/AirDropする配布に向く。

- `<link rel="manifest" href="data:application/manifest+json;base64,...">` — name/short_name/display:standalone/icons等をJSONで書き、**base64エンコードしたdata URI**で埋め込む(生JSON+パーセントエンコードだと`"`等のエスケープが面倒なのでbase64が安全)
- `<meta name="apple-mobile-web-app-capable" content="yes">` などApple系メタタグ一式(iOSはmanifestよりこちら優先で長年対応してきた経緯があるので必ず両方入れる)
- `<link rel="apple-touch-icon" href="data:image/png;base64,...">` — アイコンはヘッドレスブラウザで512x512のHTML(角丸div+絵文字等)をスクリーンショットしてPNG化→base64化して作る(外部画像生成ツールは使わない)
- Service Workerは入れていない: ローカルファイルは`file://`オリジンのためSW登録不可(仕様上の制約)で、そもそもローカルファイルは常にオフライン。Claude Artifactとして公開する経路はhead部を自分で書けない制約があるため、PWA化は「配布するHTMLファイル自身」に対して行う
- ユーザーへの案内が無いと意味が無い機能なので、納品時は必ず「Safariの共有→ホーム画面に追加」の手順を日本語で添える(Quick Look等のプレビューから追加すると正しく動かないことがあるため、一度Safariのタブとして開いてから追加するよう案内する)

### パターンB: GitHub Pages常設ホスティング(`flight_finder.html` / `mile_compass.html`)

`.github/workflows/pages.yml` が push のたびに対象HTML(→index.html等)+ `travel_tools/pwa/`(manifest・sw.js・アイコン)を自動デプロイし、真のService Workerによるオフラインキャッシュを持つ。常にURLでアクセスする使い方(ブックマーク・ホーム画面リンク)に向く。

- **本体HTMLを更新したら `travel_tools/pwa/sw.js` の `VERSION` を上げること**(利用者側のキャッシュが確実に更新される)
- 前提: GitHub PagesはリポジトリがPublicか有料プランでのみ動く。デプロイ失敗時はまずここを疑う
- `kaigai_travel_kit.html` を将来こちらへ移行する場合は、`travel_tools/pwa/`を共有するか専用のmanifest/アイコンを追加し、pages.ymlのpathsとdistコピー処理を拡張する

## 開発のお作法

- 新しいツールを追加するときも1と2のルールは例外なく適用する
- 破壊的なgit操作(force push、reset --hard等)は `.claude/settings.json` で拒否済み。それでも必要な場合はユーザーに確認する
