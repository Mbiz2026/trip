#!/usr/bin/env python3
"""単体HTMLアプリから Artifact 公開用のHTMLを生成する。

Artifact は publish 時に `<!doctype html><head>…</head><body>` を自分で被せる仕様なので、
こちらは <title> と本文だけを渡す必要がある。手で2つのファイルを維持すると必ずズレるので、
リポジトリの単体HTMLを唯一の正とし、そこから機械的に変換する。

やっていること:
  1. <title> と <body> の中身、<head> 内の <style> を取り出す
  2. PWA用のmanifest/アイコン(data URI・約250KB)を落とす — Artifactでは<head>を書けないので不要
  3. Webフォント(Archivo)の @import を差し込む — Artifact は Google Fonts だけ読み込める
     (単体HTML側は「外部リソースを読み込まない」ルールがあるので入れられない)

使い方:
    python3 travel_tools/dev/build_artifact.py travel_tools/mile_factory.html <出力先.html>
"""
import re
import sys
from pathlib import Path

FONT_IMPORT = (
    '@import url("https://fonts.googleapis.com/css2'
    '?family=Archivo:wght@500;600;700&display=swap");\n'
)


def build(src: Path) -> str:
    html = src.read_text(encoding="utf-8")

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    if not title:
        raise SystemExit(f"{src}: <title> が見つかりません")

    style = re.search(r"<style>(.*?)</style>", html, re.S)
    if not style:
        raise SystemExit(f"{src}: <style> が見つかりません")

    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    if not body:
        raise SystemExit(f"{src}: <body> が見つかりません")

    css = FONT_IMPORT + style.group(1).strip()

    return (
        f"<title>{title.group(1)}</title>\n"
        f"<style>\n{css}\n</style>\n"
        f"{body.group(1).strip()}\n"
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    out = build(src)
    dest.write_text(out, encoding="utf-8")
    print(f"{src} ({src.stat().st_size:,} bytes) -> {dest} ({len(out.encode('utf-8')):,} bytes)")


if __name__ == "__main__":
    main()
