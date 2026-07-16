# 海外旅行ツール (trip)

ユーザーはコードを書けない。すべての操作はClaudeが代行し、結果だけを平易な日本語で報告すること。

## このリポジトリについて

海外旅行者向けの実用ツールを作る。今のところ4つ:

1. `travel_tools/kaigai_travel_kit.html` — 入国手続き・航空券の探し方・両替とチップ・指さし会話・持ち物・緊急連絡先をまとめた、オフラインで動くスマホ用Webアプリ(1ファイル)
2. `/tabi-shiori` コマンド(`.claude/commands/tabi-shiori.md`) — 行き先と日程を伝えると、その渡航専用の「旅のしおり」HTMLを調査つきで生成する
3. `travel_tools/flight_finder.html` — 「航空券サーチ司令塔」。条件を1回入れると横断検索サイト+就航LCC公式への条件入りリンクを一括生成するオンライン前提アプリ(1ファイル)。周辺空港・片道×片道・LCC図鑑(大手サイト掲載状況つき)・手荷物ルール早見・実質総額計算機・セールカレンダー・追跡メモ入り。ユーザーの出発空港の優先順は 伊丹→関空→神戸→羽田(国際線の実質拠点は関空)
4. `/flight-mihari` コマンド(`.claude/commands/flight-mihari.md`) — 航空券の7日間価格追跡/期間セール監視をRoutine(毎日1回)で代行し、基準額を下回ったら通知。取得失敗は正直に報告するベストエフォート設計
5. `travel_tools/mile_compass.html` — 「マイルコンパス」。JALマイル×アメックスMR(メンバーシップ・リワード)特化の行き先さがしアプリ(1ファイル・オフライン動作)。条件チップで行き先26都市を絞り込み(CSSの`:has`のみで動作)→カードで「どのマイルで・何マイルで・燃油いくらで」行けるかを早見。ワンワールド/MR移行可否バッジ、燃油回避ワザ、保有マイル射程判定・MR移行シミュレータ・マイル価値計算機(いずれもJS時のみ)入り。数字はすべて確認日付き、公式未確認値は※表記。行き先カードは `scratchpad/gen_cards.py`(セッション限り)で生成した静的HTML。**燃油サーチャージは2ヶ月ごと(奇数月中旬に翌期発表)に改定される**ため、「マイルコンパスを最新化して」と頼まれたら燃油・チャート改定を再調査してこのファイルを更新する。GitHub Pagesでは `/mile.html` として配信(pages.ymlが自動デプロイ)

## 絶対に守ること

1. **JavaScriptが無くても主要機能が動くこと。** iPhoneの「ファイル」アプリ等のプレビュー表示はJavaScriptを実行しない。タブ切り替え・情報の閲覧は必ずCSSだけ(ラジオボタン+`:checked`等)で動く構造にする。JavaScriptは計算機・検索・チェックの保存など「あれば便利」機能だけに使い、無くても情報は全部読めるようにする
2. **外部リソースを読み込まない。** CDN・Webフォント・外部画像は禁止。1ファイルで完結させ、オフラインで開けること
3. **事実は日付付きの公式ソースのみ。** 政府・大使館・航空会社等の公式サイトを優先し、記載には確認日を付ける。ブログ等の二次情報を使うときは二次情報だと明記し断定を避ける。ニセ代行サイトへの誘導は絶対にしない(公式リンクのみ案内する)
4. **ライト/ダークテーマ両対応。** 生成物は必ず両方で見た目を確認する
5. **生成後は表示確認をする。** ヘッドレスブラウザで(JS有り/無しの両方)スクリーンショットを撮ってから納品する。無い環境ではユーザーに確認を依頼する
6. **迷ったら止まってユーザーに聞く。** 情報の鮮度・法規制が絡む分野(渡航制度・料金など)は特に慎重に。断定できないことは「要確認」と明記する

## 表示確認のやり方(セッション開始時のフックが利用可否を教えてくれる)

```bash
<ヘッドレスブラウザのパス> --no-sandbox --disable-gpu --window-size=390,1300 --screenshot=out.png file:///絶対パス/foo.html
# JSを外した状態(iOSファイルアプリ相当)も必ず確認する
<同上> --blink-settings=scriptEnabled=false --no-sandbox --disable-gpu --window-size=390,1300 --screenshot=out_nojs.png file:///絶対パス/foo.html
```

注意(2026-07-11に判明):
- 上記の直接起動はウィンドウ幅が最小500pxに切り上げられ、390px指定だと**画像の右端が切れて写る**(実際のはみ出しではない)。`--blink-settings=scriptEnabled=false` も新しいheadlessでは失敗することがある
- 確実なのは `pip install playwright` して Python から `executable_path='/opt/pw-browsers/chromium'` で起動する方法。`viewport=390x844` が正しく効き、`color_scheme='dark'`(ダーク確認)や `java_script_enabled=False`(JSオフ確認)も指定できる。実装例: 過去セッションの `shoot.py`(scratchpad)

## ワークフロー: 旅のしおり生成 (`/tabi-shiori`)

詳細は `.claude/commands/tabi-shiori.md` を参照。行き先・時期をWeb調査し、`travel_tools/kaigai_travel_kit.html` とデザインの統一感を保った、1ファイルのしおりHTMLを作る。

## 航空券サーチ司令塔のWeb版(PWA)

`flight_finder.html` はGitHub Pagesで「普通のアプリ」として配信している(ホーム画面インストール・オフライン起動対応)。

- 配信の仕組み: `.github/workflows/pages.yml` が push のたびに `flight_finder.html`(→index.html)+ `travel_tools/pwa/`(manifest・sw.js・アイコン)を自動デプロイ
- **本体HTMLを更新したら `travel_tools/pwa/sw.js` の `VERSION` を上げること**(利用者側のキャッシュが確実に更新される)
- 前提: GitHub PagesはリポジトリがPublicか有料プランでのみ動く。デプロイ失敗時はまずここを疑う

## 開発のお作法

- 新しいツールを追加するときも1と2のルールは例外なく適用する
- 破壊的なgit操作(force push、reset --hard等)は `.claude/settings.json` で拒否済み。それでも必要な場合はユーザーに確認する
