#!/usr/bin/env python3
"""しおりHTMLの機械チェック。納品前に必ず通す。

使い方:
    python3 travel_tools/dev/verify_shiori.py travel_tools/shiori_xxx_20260923.html

検査項目(CLAUDE.md の絶対ルールと .claude/commands/tabi-shiori.md の検証条件に対応):
  1. 外部リソースを読み込んでいないか(CDN・画像URL・Webフォント) ← 絶対ルール2
  2. タブのラジオ数 == ラベル数 == パネル数        ← 絶対ルール1(CSSだけでタブが動く)
  3. JSで初期表示を作っている空要素が無いか        ← 絶対ルール1の見落ちやすい箇所
  4. select要素のoptionが静的に存在するか          ← 同上
  5. タグの対応が取れているか
  6. 情報確認日・免責・出典タブがあるか            ← しおり固有の要件
  7. PWAのmanifestとアイコンが埋め込まれているか

ブラウザでの表示確認(JS無し/ダーク)は別途Playwrightで行う。これは静的検査のみ。
終了コード: 0=合格 / 1=不合格
"""
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"{tag} の閉じタグが余っている (行 {self.getpos()[0]})")
        elif self.stack[-1][0] != tag:
            self.errors.append(
                f"行 {self.getpos()[0]}: </{tag}> だが直前に開いているのは "
                f"<{self.stack[-1][0]}> (行 {self.stack[-1][1]})")
            self.stack.pop()
        else:
            self.stack.pop()


def strip_comments(html: str) -> str:
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def check(path: str) -> bool:
    raw = open(path, "rb").read()
    html = raw.decode("utf-8")
    body = strip_comments(html)
    ok, results = True, []

    def add(passed, label, detail=""):
        nonlocal ok
        if not passed:
            ok = False
        results.append(("PASS" if passed else "FAIL", label, detail))

    # 1. 外部リソース
    external = []
    for m in re.finditer(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', body, re.I):
        url = m.group(1).strip()
        if re.match(r"^(https?:)?//", url, re.I):
            external.append(url)
    for m in re.finditer(r"url\(\s*['\"]?((?:https?:)?//[^)'\"]+)", body, re.I):
        external.append(m.group(1))
    add(not external, "外部リソースを読み込んでいない",
        "" if not external else f"{len(external)}件: " + ", ".join(external[:5]))

    # 2. タブの三点一致
    radio_tags = re.findall(r"<input\b[^>]*type=[\"']radio[\"'][^>]*>", body, re.I)
    radio_ids = []
    for tag in radio_tags:
        if not re.search(r'name=["\']tab', tag, re.I) and "tabradio" not in tag.lower():
            continue
        m = re.search(r'id=["\']([^"\']+)', tag, re.I)
        if m:
            radio_ids.append(m.group(1))
    # ラベルは for がラジオの id を指しているものだけ数える(対応そのものを検査する)
    label_fors = re.findall(r'<label\b[^>]*for=["\']([^"\']+)', body, re.I)
    linked = [f for f in label_fors if f in radio_ids]
    panes = re.findall(r'class="[^"]*\bpane\b[^"]*"', body, re.I)
    counts = (len(radio_ids), len(linked), len(panes))
    orphan = sorted(set(radio_ids) - set(label_fors))
    detail = f"ラジオ{counts[0]} / 対応するラベル{counts[1]} / パネル{counts[2]}"
    if orphan:
        detail += "  ラベルが無いラジオ: " + ", ".join(orphan[:5])
    add(len(set(counts)) == 1 and counts[0] > 0,
        "タブのラジオ数 == ラベル数 == パネル数", detail)

    # 3. JSで中身を入れる想定の空要素
    empties = re.findall(r'<(p|span|div|td)\b[^>]*\bid="([^"]+)"[^>]*>\s*</\1>', body, re.I)
    add(not empties, "JSで初期表示を作る空要素が無い",
        "" if not empties else "id=" + ", ".join(e[1] for e in empties[:8]))

    # 4. selectのoptionが静的にあるか
    bad_selects = [s for s in re.findall(r"<select\b.*?</select>", body, re.I | re.S)
                   if "<option" not in s.lower()]
    add(not bad_selects, "select要素のoptionが静的に存在する",
        "" if not bad_selects else f"option が無いselectが{len(bad_selects)}件")

    # 5. タグの対応
    tb = TagBalance()
    tb.feed(html)
    leftover = [f"<{t}> (行 {ln})" for t, ln in tb.stack]
    add(not tb.errors and not leftover, "タグの対応が取れている",
        "; ".join((tb.errors + leftover)[:5]))

    # 6. しおり固有の必須要素
    add("情報確認日" in body, "ヘッダーに情報確認日がある")
    add(bool(re.search(r"再確認|公式サイトで|渡航前", body)), "フッターに免責がある")
    add(bool(re.search(r"出典", body)), "出典タブ/セクションがある")

    # 7. PWA
    add('rel="manifest"' in body.lower(), "manifestが埋め込まれている")
    add("apple-touch-icon" in body.lower(), "apple-touch-iconが埋め込まれている")
    add("apple-mobile-web-app-capable" in body.lower(), "Apple系メタタグがある")

    def disp_width(t):
        import unicodedata
        return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in t)

    width = max(disp_width(r[1]) for r in results) + 2
    print(f"\n検査対象: {path}  ({len(raw):,} バイト / {len(html):,} 文字)\n")
    for status, label, detail in results:
        mark = "  OK  " if status == "PASS" else " NG   "
        pad = " " * max(1, width - disp_width(label))
        print(f"[{mark}] {label}{pad}{detail}")
    print()
    print("=> 合格。ブラウザでの表示確認(JS無し / ダーク / light)に進む。" if ok
          else "=> 不合格。上の NG を直してから再実行する。")
    return ok


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"使い方: python3 {sys.argv[0]} <しおりHTMLのパス>")
    sys.exit(0 if check(sys.argv[1]) else 1)
