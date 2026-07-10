#!/bin/bash
set -uo pipefail

echo "## 実行環境チェック(trip)"

PY_OK=false
if command -v python3 >/dev/null 2>&1; then
  PY_OK=true
  echo "- python3: 利用可能"
else
  echo "- python3: 見つかりません"
fi

CHROME=""
for p in /opt/pw-browsers/chromium /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell; do
  if [ -x "$p" ]; then
    CHROME="$p"
    break
  fi
done
if [ -n "$CHROME" ]; then
  echo "- ヘッドレスブラウザ: 利用可能 ($CHROME)"
else
  echo "- ヘッドレスブラウザ: 見つかりません"
fi

echo ""
if [ -n "$CHROME" ]; then
  echo "→ 生成したHTMLをこのセッション内で表示確認できます(JS有り/無し両方)。新規ツール追加後は必ずスクリーンショットで確認してから納品してください。"
else
  echo "→ ヘッドレスブラウザが無い環境です。生成したHTMLの表示確認はユーザーに依頼してください。"
fi
echo "  ※ このリポジトリのツールは「JavaScriptが無くても主要機能が動く」ことが絶対条件です(詳細はCLAUDE.md)。"

exit 0
