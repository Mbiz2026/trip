#!/usr/bin/env python3
"""特典レーダー(award_radar.html)のPWAアイコンを生成する。

外部の画像生成サービスは使わず、HTML+SVGをヘッドレスブラウザで描画して
PNG化する(CLAUDE.md「アプリ化」の方針どおり)。冪等: 何度実行しても同じ絵が出る。

  python3 travel_tools/dev/gen_radar_icons.py

出力先: travel_tools/pwa/radar-icon-{180,192,512}.png と radar-icon-512-maskable.png
"""
import os
import sys

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pwa')
CHROMIUM = '/opt/pw-browsers/chromium'


def icon_html(radius_pct, inset_pct):
    """radius_pct: 角丸の割合 / inset_pct: 図柄を内側に寄せる割合(マスカブル用)"""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden}}
  .plate{{width:100%;height:100%;border-radius:{radius_pct}%;overflow:hidden;
    background:linear-gradient(145deg,#C0353F 0%,#97282F 45%,#6E1A20 100%);
    display:flex;align-items:center;justify-content:center}}
  svg{{width:{100 - inset_pct * 2}%;height:{100 - inset_pct * 2}%;display:block}}
</style></head><body>
<div class="plate">
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sweep" x1="50" y1="50" x2="92" y2="18" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.42"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <!-- 走査の扇 -->
  <path d="M50 50 L94 24 A50.8 50.8 0 0 1 92 62 Z" fill="url(#sweep)"/>
  <!-- 同心円 -->
  <circle cx="50" cy="50" r="41" fill="none" stroke="#FFFFFF" stroke-opacity="0.30" stroke-width="2.4"/>
  <circle cx="50" cy="50" r="27" fill="none" stroke="#FFFFFF" stroke-opacity="0.24" stroke-width="2.2"/>
  <circle cx="50" cy="50" r="13" fill="none" stroke="#FFFFFF" stroke-opacity="0.20" stroke-width="2"/>
  <!-- 走査線 -->
  <line x1="50" y1="50" x2="94" y2="24" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="2.6" stroke-linecap="round"/>
  <!-- 見つけた席(光点) -->
  <circle cx="69" cy="35" r="8.4" fill="#FFFFFF" fill-opacity="0.20"/>
  <circle cx="69" cy="35" r="4.6" fill="#FFFFFF"/>
  <!-- 中心 -->
  <circle cx="50" cy="50" r="3.4" fill="#FFFFFF" fill-opacity="0.9"/>
</svg>
</div></body></html>"""


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('playwright が必要です: pip install playwright')

    out = os.path.normpath(OUT_DIR)
    os.makedirs(out, exist_ok=True)
    jobs = [
        ('radar-icon-512.png', 512, 22, 12),
        ('radar-icon-192.png', 192, 22, 12),
        ('radar-icon-180.png', 180, 22, 12),
        # maskable: 角丸なしの全面 + 図柄を安全域(中央80%)に収める
        ('radar-icon-512-maskable.png', 512, 0, 21),
    ]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM, args=['--no-sandbox', '--disable-gpu'])
        for name, size, radius, inset in jobs:
            ctx = b.new_context(viewport={'width': size, 'height': size}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.set_content(icon_html(radius, inset), wait_until='load')
            pg.wait_for_timeout(120)
            path = os.path.join(out, name)
            pg.screenshot(path=path, omit_background=True)
            print('wrote', path, size, 'px')
            ctx.close()
        b.close()


if __name__ == '__main__':
    main()
