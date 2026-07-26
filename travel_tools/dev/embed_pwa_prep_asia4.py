"""
準備チェックリストHTMLをPWA化する(CLAUDE.md パターンA: 単体HTMLにdata URIで全部埋め込み)。
- アイコンは外部ツールを使わず、HTML(グラデーション角丸+絵文字)をヘッドレスで撮ってPNG化
- manifestはbase64のdata URIで埋め込む
冪等: 何度実行しても同じ結果になる(既存のPWAタグを一度剥がしてから入れ直す)
"""
import base64, json, re, pathlib
from playwright.sync_api import sync_playwright

TARGET = pathlib.Path("/home/user/trip/travel_tools/prep_asia4_20260808.html")
OUT = pathlib.Path("/tmp/claude-0/-home-user-trip/b8c3e40a-5ffa-56b0-a757-0e066d2aa706/scratchpad")

# 角丸・透過なしのフルスクエア。iOS/Androidが自前でマスクをかけるため、
# 角丸を焼き込むと縁に黒い隙間が出ることがある。
TPL = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;width:512px;height:512px}
.icon{width:512px;height:512px;position:relative;overflow:hidden;
  background:radial-gradient(120% 120% at 18% 12%, #0D6B65 0%, #14504F 42%, #1B3350 74%, #14243C 100%);
  display:flex;align-items:center;justify-content:center}
.icon::after{content:"";position:absolute;inset:0;
  box-shadow:inset 0 -40px 90px rgba(0,0,0,.24)}
.g{font-size:292px;line-height:1;transform:rotate(-6deg);
  filter:drop-shadow(0 16px 26px rgba(0,0,0,.42))}
</style></head><body><div class="icon"><div class="g">&#9989;</div></div></body></html>"""

SIZES = [512, 192, 180, 32]


def render_icons():
    pngs = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        for s in SIZES:
            # 512pxで描いてから deviceScaleFactor で縮小すると、絵文字が滑らかに落ちる
            c = b.new_context(viewport={"width": 512, "height": 512}, device_scale_factor=s / 512)
            p = c.new_page()
            p.set_content(TPL)
            p.wait_for_timeout(350)
            data = p.screenshot(omit_background=False)
            (OUT / f"icon_{s}.png").write_bytes(data)
            pngs[s] = data
            c.close()
        b.close()
    return pngs


def datauri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def build_manifest(pngs) -> str:
    man = {
        "id": "/",
        "name": "4カ国周遊 準備チェックリスト 2026年8月",
        "short_name": "8月の準備",
        "description": "関空→ハノイ→クアラルンプール→シンガポール→ソウルの準備チェックリスト(オフライン)",
        "start_url": ".",
        "scope": ".",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#F3F5F4",
        "theme_color": "#0D6B65",
        "lang": "ja",
        "icons": [
            {"src": datauri(pngs[512]), "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    raw = json.dumps(man, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "data:application/manifest+json;base64," + base64.b64encode(raw).decode("ascii")


def main():
    pngs = render_icons()
    html = TARGET.read_text(encoding="utf-8")

    # --- 既存のPWA関連タグを一度剥がす(冪等にするため) ---
    html = re.sub(r'\n?\s*<link rel="manifest"[^>]*>', "", html)
    html = re.sub(r'\n?\s*<link rel="apple-touch-icon"[^>]*>', "", html)
    html = re.sub(r'\n?\s*<link rel="icon"[^>]*>', "", html)
    html = re.sub(r'\n?\s*<meta name="(mobile-web-app-capable|apple-mobile-web-app-capable|'
                  r'apple-mobile-web-app-status-bar-style|apple-mobile-web-app-title|color-scheme)"[^>]*>', "", html)

    block = (
        '\n<meta name="color-scheme" content="light dark">'
        f'\n<link rel="manifest" href="{build_manifest(pngs)}">'
        '\n<meta name="mobile-web-app-capable" content="yes">'
        '\n<meta name="apple-mobile-web-app-capable" content="yes">'
        '\n<meta name="apple-mobile-web-app-status-bar-style" content="default">'
        '\n<meta name="apple-mobile-web-app-title" content="8月の準備">'
        f'\n<link rel="apple-touch-icon" href="{datauri(pngs[180])}">'
        f'\n<link rel="apple-touch-icon" sizes="192x192" href="{datauri(pngs[192])}">'
        f'\n<link rel="icon" type="image/png" sizes="32x32" href="{datauri(pngs[32])}">'
    )

    # theme-color の直前に差し込む
    anchor = '<meta name="theme-color" content="#F3F5F4" media="(prefers-color-scheme: light)">'
    assert anchor in html, "theme-color タグが見つからない"
    html = html.replace(anchor, block.strip("\n") + "\n" + anchor, 1)

    TARGET.write_text(html, encoding="utf-8")

    print("埋め込んだアイコン:")
    for s in SIZES:
        print(f"  {s}x{s}: {len(pngs[s]):,} バイト")
    print(f"HTML: {len(html):,} バイト")


main()
