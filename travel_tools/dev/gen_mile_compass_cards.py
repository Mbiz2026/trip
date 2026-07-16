# -*- coding: utf-8 -*-
"""マイルコンパス(travel_tools/mile_compass.html)の行き先カード+一覧表を生成して差し込む。

使い方: このファイルの D(行き先データ)や燃油定数を編集 → `python3 travel_tools/dev/gen_mile_compass_cards.py`
→ HTML内の <!-- DESTCARDS:BEGIN -->〜<!-- DESTCARDS:END --> と <!-- LISTROWS:BEGIN -->〜<!-- LISTROWS:END --> が
丸ごと差し替わる(何度実行しても同じ結果になる冪等設計)。
※=公式ページ本文で最終確認できていない参考値(旧チャート・報道・二次情報)。データ確認日 2026-07-16。
燃油サーチャージや「マイル術」「基礎と出典」タブの表はHTML直書きなので、改定時はHTML側も忘れず更新すること。
"""
import re, sys

HTML = '/home/user/trip/travel_tools/mile_compass.html'

# 燃油(往復・2026年7-8月発券分)
KR = '約¥14,800'
EA_J = '約¥33,800'; EA_A = '約¥30,800'
GPV = '約¥45,000'
SEA_J = '約¥70,000'; SEA_A = '約¥67,000'
HII = '約¥80,800'
LNG = '約¥130,000'
ZERO = '<b>なし</b>※(諸税のみ)'
CXYQ = 'あり(HK$建て・要確認)'

# 一覧表・カードサマリ用: id -> (JALマイルで, MR移行で最安, 並べ替えキー)
LISTMETA = {
    'seoul':        ('15,000※', '12,000 <i>ANA(L)</i>', 12000),
    'taipei':       ('20,000※', '17,000 <i>ANA(L)</i>', 17000),
    'hongkong':     ('20,000※', '17,000 <i>ANA(L)</i>', 17000),
    'shanghai':     ('20,000※', '17,000 <i>ANA(L)</i>', 17000),
    'manila':       ('20,000※', '17,000 <i>ANA(L)</i>', 17000),
    'bangkok':      ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'singapore':    ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'kualalumpur':  ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'hanoi':        ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'hochiminh':    ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'jakarta':      ('35,000※', '30,000 <i>ANA(L)</i>', 30000),
    'delhi':        ('要確認', '30,000 <i>ANA(L)</i>', 30000),
    'colombo':      ('距離制※', '—', 10**9),
    'doha':         ('距離制※', '要確認 <i>QR Avios</i>', 10**9),
    'guam':         ('20,000※', '要確認 <i>ANA→UA</i>', 20000),
    'honolulu':     ('40,000※', '35,000 <i>ANA(L)</i>', 35000),
    'nadi':         ('距離制※', '—', 10**9),
    'sydney':       ('36,000※', '37,000 <i>ANA(L)</i>', 36000),
    'melbourne':    ('36,000※', '要確認 <i>カンタス</i>', 36000),
    'london':       ('54,000', '45,000 <i>ANA(L)</i>', 45000),
    'paris':        ('54,000', '45,000 <i>ANA(L)</i>', 45000),
    'helsinki':     ('54,000※', '要確認 <i>Avios</i>', 54000),
    'newyork':      ('54,000', '40,000 <i>ANA(L)</i>', 40000),
    'losangeles':   ('54,000', '40,000 <i>ANA(L)</i>', 40000),
    'sanfrancisco': ('54,000', '40,000 <i>ANA(L)</i>', 40000),
    'vancouver':    ('—', '要確認 <i>ANA→AC</i>', 10**9),
}

def mr(p): return f'<span class="badge mr">MR</span>'
OW = '<span class="badge ow">OW</span>'
STAR = '<span class="badge warn2">スタアラ</span>'
JB = '<span class="badge jalb">JAL便</span>'

def L_JAL(dest='JAL便'):  return f'<b>JALマイル</b> <span class="small">→{dest}</span> {OW}'
def L_ANA():  return f'<b>ANAマイル</b><span class="badge mr">MR 1:1</span> <span class="small">→ANA便</span> {STAR}'
def L_AVIOS(dest='JAL便'): return f'<b>Avios</b><span class="badge mr">MR 0.8</span> <span class="small">→{dest}</span> {OW}'
def L_ASIA(): return f'<b>アジアマイル</b><span class="badge mr">MR 0.8</span> <span class="small">→キャセイ便</span> {OW}'
def L_VS():   return f'<b>ヴァージン</b><span class="badge mr">MR 0.8</span> <span class="small">→ANA便</span>'
def L_ANAP(dest): return f'<b>ANAマイル</b><span class="badge mr">MR 1:1</span> <span class="small">→{dest}(提携特典)</span> {STAR}'

def ana_lrh(l, r, h=None):
    s = f'L <b>{l:,}</b> / R {r:,}'
    s += f' / H {h:,}' if h else ' / H 要確認'
    return s

D = [
# ---------------- 東アジア ----------------
dict(id='seoul', flag='🇰🇷', city='ソウル', country='韓国', rg='easia', rgl='東アジア',
     time='約2時間', t='t1', b='b1', yq1=True, dk=None, dt='JAL(羽田-金浦ほか)・ANA',
     data=dict(jal=15000, avios=25000, ana=12000),
     minv='12,000', minprog='ANA(L)', minmark=False, yqlist=KR, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>15,000</b>〜 ※', KR, '基本マイル・空席次第で増える変動制(片道7,500〜)'),
       (L_ANA(), ana_lrh(12000,15000,24000), KR, 'MRから1:1移行(要ANAコース)。往復Cは H 50,000'),
       (L_AVIOS('JAL便(羽田-金浦)'), '<b>25,000</b><span class="small">(MR 31,250P)</span>', KR, '片道12,500×2。2025年12月改定後・二次情報'),
     ],
     notes=['燃油が全方面最安+マイルも最少。「はじめての特典航空券」に最適。'], warns=[]),
dict(id='taipei', flag='🇹🇼', city='台北', country='台湾', rg='easia', rgl='東アジア',
     time='約3時間', t='t1', b='b2', yq1=True, dk='JAL(桃園)※二次', dt='JAL(羽田-松山/成田-桃園)・ANA',
     data=dict(jal=20000, avios=25000, ana=17000),
     minv='17,000', minprog='ANA(L)', minmark=False, yqlist=EA_J, kx='○JAL※', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>20,000</b>〜 ※', EA_J, '基本マイル・変動制'),
       (L_ANA(), ana_lrh(17000,20000,30000), EA_A, 'ANAは羽田・成田発'),
       (L_AVIOS('JAL便(関空-台北も)'), '<b>25,000</b><span class="small">(MR 31,250P)</span>', EA_J, '片道12,500×2・二次情報'),
     ],
     notes=['関空直行(JAL)にAviosが使える好相性の行き先。'], warns=[]),
dict(id='hongkong', flag='🇭🇰', city='香港', country='', rg='easia', rgl='東アジア',
     time='約4時間', t='t1', b='b2', yq1=True, dk='キャセイ(毎日複数便)', dt='JAL・キャセイ',
     data=dict(jal=20000, asia=26000, ana=17000),
     minv='17,000', minprog='ANA(L)', minmark=False, yqlist=EA_J, kx='○CX', tk='○JAL/CX',
     rows=[
       (L_JAL(), '<b>20,000</b>〜 ※', EA_J, '基本マイル・変動制'),
       (L_ASIA(), '<b>26,000</b><span class="small">(MR 32,500P)</span>', CXYQ, '片道13,000×2(Standard=席少なめ)。往復C 66,000'),
       (L_ANA(), ana_lrh(17000,20000,30000), EA_A, 'ANAは羽田・成田発'),
     ],
     notes=['関空-香港はキャセイが毎日複数便。香港経由で東南アジアへ伸ばすのも距離制のアジアマイルが得意(要確認)。'], warns=[]),
dict(id='shanghai', flag='🇨🇳', city='上海', country='中国', rg='easia', rgl='東アジア',
     time='約2.5時間', t='t1', b='b2', yq1=True, dk='JAL(浦東)※二次・ANA(浦東)', dt='JAL(羽田-虹橋ほか)・ANA',
     data=dict(jal=20000, ana=17000),
     minv='17,000', minprog='ANA(L)', minmark=False, yqlist=EA_J, kx='○JAL※/ANA', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>20,000</b>〜 ※', EA_J, '基本マイル・変動制'),
       (L_ANA(), ana_lrh(17000,20000,30000), EA_A, '関空-上海はANAも運航(数少ない関空ANA国際線)'),
     ],
     notes=['MR→ANAで関空発着が組める貴重な行き先。'], warns=[]),
# ---------------- 東南アジア ----------------
dict(id='manila', flag='🇵🇭', city='マニラ', country='フィリピン', rg='seasia', rgl='東南アジア',
     time='約4.5時間', t='t1', b='b2', yq1=False, dk=None, dt='JAL(成田)・ANA',
     data=dict(jal=20000, ana=17000),
     minv='17,000', minprog='ANA(L)', minmark=False, yqlist=GPV, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>20,000</b>〜 ※(旧チャート値)', GPV, '2025年6月改定後の値は要確認'),
       (L_ANA(), ana_lrh(17000,20000,30000), GPV, 'マニラは「アジア1」扱いで東南アジアより安い'),
     ],
     notes=['フィリピン航空がワンワールド加盟予定(2027年ごろ見込み)。実現すればセブ等へも特典が広がるかも。'], warns=[]),
dict(id='bangkok', flag='🇹🇭', city='バンコク', country='タイ', rg='seasia', rgl='東南アジア',
     time='約6時間', t='t2', b='b3', yq1=False, dk='JAL(毎日)', dt='JAL・ANA',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=SEA_J, kx='○JAL', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※二次', SEA_J, '片道17,500〜。関空発直行あり'),
       (L_ANA(), ana_lrh(30000,35000), SEA_A, 'H期の改定後値は要確認'),
     ],
     notes=[], warns=['燃油が往復7万円級。急ぎでなければ9月以降の燃油改定(8月中旬発表)を見てから発券する手も。']),
dict(id='singapore', flag='🇸🇬', city='シンガポール', country='', rg='seasia', rgl='東南アジア',
     time='約7時間', t='t2', b='b3', yq1=False, dk=None, dt='JAL・ANA',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=SEA_J, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※(旧チャート値)', SEA_J, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(30000,35000), SEA_A, 'シンガポール航空(MR移行可・スタアラ)という選択肢も'),
     ],
     notes=[], warns=[]),
dict(id='kualalumpur', flag='🇲🇾', city='クアラルンプール', country='マレーシア', rg='seasia', rgl='東南アジア',
     time='約7時間', t='t2', b='b3', yq1=False, dk='マレーシア航空(週5)', dt='JAL(成田)・MH(毎日)',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=SEA_J, kx='○MH', tk='○JAL/MH',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※(旧チャート値)', SEA_J, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(30000,35000), SEA_A, ''),
       (L_JAL('マレーシア航空便(提携特典)'), '距離制・要確認', 'あり※', '関空-KL直行。MHは2024年12月から燃油徴収に変更(二次)'),
     ],
     notes=[], warns=[]),
dict(id='hanoi', flag='🇻🇳', city='ハノイ', country='ベトナム', rg='seasia', rgl='東南アジア',
     time='約5時間', t='t2', b='b3', yq1=False, dk=None, dt='JAL(成田)・ANA(羽田)',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=GPV, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※(旧チャート値)', GPV, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(30000,35000), GPV, ''),
     ],
     notes=['ベトナムは燃油帯がタイより1段安い(往復約4.5万円)。'], warns=[]),
dict(id='hochiminh', flag='🇻🇳', city='ホーチミン', country='ベトナム', rg='seasia', rgl='東南アジア',
     time='約5.5時間', t='t2', b='b3', yq1=False, dk=None, dt='JAL(成田)・ANA',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=GPV, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※(旧チャート値)', GPV, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(30000,35000), GPV, ''),
     ],
     notes=['ベトナムは燃油帯がタイより1段安い(往復約4.5万円)。'], warns=[]),
dict(id='jakarta', flag='🇮🇩', city='ジャカルタ', country='インドネシア', rg='seasia', rgl='東南アジア',
     time='約7.5時間', t='t2', b='b3', yq1=False, dk=None, dt='JAL(成田)・ANA',
     data=dict(jal=35000, ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=HII, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>35,000</b>〜 ※(旧チャート値)', HII, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(30000,35000), HII, ''),
     ],
     notes=[], warns=['インドネシアの燃油はハワイと同じ帯(往復約8万円)。バリ島行きも同様。']),
# ---------------- 南アジア・中東 ----------------
dict(id='delhi', flag='🇮🇳', city='デリー', country='インド', rg='sasia', rgl='南アジア・中東',
     time='約10時間', t='t3', b='b3', yq1=False, dk=None, dt='JAL(羽田・成田)・ANA',
     data=dict(ana=30000),
     minv='30,000', minprog='ANA(L)', minmark=False, yqlist=HII, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '路線別・要確認', HII, '2026年1月に成田-デリー線が新規就航し便数増'),
       (L_ANA(), ana_lrh(30000,35000), HII, '「アジア2」扱い'),
     ],
     notes=[], warns=[]),
dict(id='colombo', flag='🇱🇰', city='コロンボ', country='スリランカ', rg='sasia', rgl='南アジア・中東',
     time='約9.5時間', t='t3', b='b4', yq1=True, dk=None, dt='スリランカ航空(成田)',
     data=dict(),
     minv=None, minprog='JAL提携(距離制)', minmark=True, yqlist='ゼロ可※', kx='—', tk='○UL',
     rows=[
       (L_JAL('スリランカ航空便(提携特典)'), '距離制・公式早見表で要確認', ZERO, '成田-コロンボ直行'),
     ],
     notes=['燃油ゼロ組。モルディブ方面への乗継拠点にも。'], warns=[]),
dict(id='doha', flag='🇶🇦', city='ドーハ', country='カタール', rg='sasia', rgl='南アジア・中東',
     time='約12時間', t='t3', b='b4', yq1=True, dk='カタール航空(週5)', dt='カタール(成田2便・羽田)',
     data=dict(),
     minv=None, minprog='JAL提携(距離制)', minmark=True, yqlist='ゼロ可※', kx='○QR', tk='○QR',
     rows=[
       (L_JAL('カタール航空便(提携特典)'), '距離制・要確認(ワンワールド特典は25,000〜)', ZERO, '関空-ドーハ直行!欧州・アフリカへの乗継にも'),
       (f'<b>カタールAvios</b><span class="badge mr">MR 0.8</span> <span class="small">→カタール便</span> {OW}', 'QR独自価格・要確認', 'Qsuite課金あり※', 'ビジネス「Qsuite」が名物'),
     ],
     notes=[], warns=['JALの羽田-ドーハ便は2026年9月1日まで運休中(中東情勢)。カタール航空側は運航中。']),
# ---------------- ビーチ・島 ----------------
dict(id='guam', flag='🇬🇺', city='グアム', country='アメリカ領', rg='beach', rgl='ビーチ・島',
     time='約3.5時間', t='t1', b='b2', yq1=False, dk=None, dt='JAL(成田・毎日)',
     data=dict(jal=20000),
     minv='20,000', minprog='JAL(旧値)', minmark=True, yqlist=GPV, kx='—', tk='○JAL',
     rows=[
       (L_JAL(), '<b>20,000</b>〜 ※(旧チャート値)', GPV, '成田発のみ'),
       (L_ANAP('ユナイテッド便'), '提携チャート・要確認', ZERO, '関空-グアム直行のUA便をANAマイルで発券する迂回ルート(二次)'),
     ],
     notes=[], warns=['関西からの直行はユナイテッドのみで、JALマイルでは乗れない。']),
dict(id='honolulu', flag='🌺', city='ホノルル', country='ハワイ', rg='beach', rgl='ビーチ・島',
     time='約7.5時間', t='t2', b='b3', yq1=False, dk='JAL(週5〜)', dt='JAL・ANA',
     data=dict(jal=40000, ana=35000),
     minv='35,000', minprog='ANA(L)', minmark=False, yqlist=HII, kx='○JAL', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>40,000</b>〜 ※(改定後は路線別・要確認)', HII, '関空直行あり。Fは片道90,000〜'),
       (L_ANA(), ana_lrh(35000,40000,65000), HII, '往復C 80,000/85,000/135,000。A380フライングホヌ'),
     ],
     notes=['ハワイアン航空が2026年4月にワンワールド加盟(アラスカ航空に統合)。JALマイルの選択肢が広がる可能性(要確認)。'], warns=[]),
dict(id='nadi', flag='🇫🇯', city='ナンディ(フィジー)', country='', rg='beach', rgl='ビーチ・島',
     time='約9時間', t='t3', b='b4', yq1=False, dk=None, dt='フィジー・エアウェイズ(成田)※二次',
     data=dict(),
     minv=None, minprog='JAL提携(距離制)', minmark=True, yqlist='要確認', kx='—', tk='○FJ※',
     rows=[
       (L_JAL('フィジー・エアウェイズ便(提携特典)'), '距離制・要確認', '要確認', '2025年4月にワンワールド正式加盟'),
     ],
     notes=['南太平洋の楽園へワンワールドで行ける時代に。空席・マイル数は公式で要確認。'], warns=[]),
# ---------------- オセアニア ----------------
dict(id='sydney', flag='🇦🇺', city='シドニー', country='オーストラリア', rg='oceania', rgl='オセアニア',
     time='約9.5時間', t='t3', b='b3', yq1=False, dk=None, dt='JAL(羽田)・カンタス(羽田2便)・ANA',
     data=dict(jal=36000, ana=37000),
     minv='36,000', minprog='JAL(旧値)', minmark=True, yqlist=LNG, kx='—', tk='○JAL/QF/ANA',
     rows=[
       (L_JAL(), '<b>36,000</b>〜 ※(旧チャート値)', LNG, '改定後の値は要確認'),
       (L_ANA(), ana_lrh(37000,45000), LNG, 'H期の改定後値は要確認'),
       (L_JAL('カンタス便(提携特典)'), '距離制・要確認', 'あり・要確認', '羽田発1日2便'),
     ],
     notes=[], warns=['燃油が欧米と同じ最高帯(往復約13万円)。']),
dict(id='melbourne', flag='🇦🇺', city='メルボルン', country='オーストラリア', rg='oceania', rgl='オセアニア',
     time='約10.5時間', t='t3', b='b3', yq1=False, dk=None, dt='JAL(成田・10/25〜毎日)・カンタス(成田)',
     data=dict(jal=36000),
     minv='36,000', minprog='JAL(旧値)', minmark=True, yqlist=LNG, kx='—', tk='○JAL/QF',
     rows=[
       (L_JAL(), '<b>36,000</b>〜 ※(旧チャート値)', LNG, '改定後の値は要確認'),
       (L_JAL('カンタス便(提携特典)'), '距離制・要確認', 'あり・要確認', '2026年12月から週11便に増便'),
     ],
     notes=[], warns=['燃油が欧米と同じ最高帯(往復約13万円)。']),
# ---------------- ヨーロッパ ----------------
dict(id='london', flag='🇬🇧', city='ロンドン', country='イギリス', rg='europe', rgl='ヨーロッパ',
     time='約14.5時間', t='t3', b='b4', yq1=False, dk=None, dt='JAL(羽田)・BA(羽田2便)・ANA',
     data=dict(jal=54000, ana=45000, vsy=65000),
     minv='45,000', minprog='ANA(L)', minmark=False, yqlist=LNG, kx='—', tk='○JAL/BA/ANA',
     rows=[
       (L_JAL(), '<b>54,000</b><span class="small">(C 114,000)</span>', LNG, '2025年6月改定後の確認値'),
       (L_ANA(), ana_lrh(45000,55000), LNG, '往復CはH期180,000(L/R要確認)'),
       (L_VS(), 'Y <b>65,000</b> / C 120,000<span class="small">(MR 81,250P〜)</span>', LNG, '電話発券のみ・二次情報。ANAの燃油が転嫁される'),
     ],
     notes=['Avios(BA便・JAL便)も使えるが長距離の現行値は非公開(BAサイトで要確認)。'], warns=[]),
dict(id='paris', flag='🇫🇷', city='パリ', country='フランス', rg='europe', rgl='ヨーロッパ',
     time='約14.5時間', t='t3', b='b4', yq1=False, dk=None, dt='JAL(羽田)・ANA',
     data=dict(jal=54000, ana=45000),
     minv='45,000', minprog='ANA(L)', minmark=False, yqlist=LNG, kx='—', tk='○JAL/ANA',
     rows=[
       (L_JAL(), '<b>54,000</b><span class="small">(C 114,000)</span>', LNG, '2025年6月改定後の確認値'),
       (L_ANA(), ana_lrh(45000,55000), LNG, '往復CはH期180,000(L/R要確認)'),
     ],
     notes=[], warns=[]),
dict(id='helsinki', flag='🇫🇮', city='ヘルシンキ', country='フィンランド', rg='europe', rgl='ヨーロッパ',
     time='約13時間', t='t3', b='b4', yq1=False, dk='フィンエアー(週10)', dt='JAL(羽田)・フィンエアー(羽田・成田)',
     data=dict(jal=54000),
     minv='54,000', minprog='JAL(推定)', minmark=True, yqlist=LNG, kx='○AY', tk='○JAL/AY',
     rows=[
       (L_JAL(), '<b>54,000</b> ※(欧州同水準と推定・路線別要確認)', LNG, '羽田発'),
       (L_JAL('フィンエアー便(提携特典)'), '距離制・要確認', 'あり・要確認', '関空直行が週10便。欧州乗継の入口'),
     ],
     notes=['関空から欧州へ一番行きやすいワンワールド路線。MR→フィンエアー移行は2024年に終了済みなので注意。'], warns=[]),
# ---------------- 北米 ----------------
dict(id='newyork', flag='🗽', city='ニューヨーク', country='アメリカ', rg='namerica', rgl='北米',
     time='約13時間', t='t3', b='b3', yq1=False, dk=None, dt='JAL(羽田)・ANA・AA(羽田)',
     data=dict(jal=54000, ana=40000),
     minv='40,000', minprog='ANA(L)', minmark=False, yqlist=LNG, kx='—', tk='○JAL/ANA/AA',
     rows=[
       (L_JAL(), '<b>54,000</b><span class="small">(C 110,000)</span>', LNG, '2025年6月改定後の確認値'),
       (L_ANA(), ana_lrh(40000,50000,72000), LNG, '<b>Lなら40,000=MR年間上限ぴったり</b>。往復C 100,000〜165,000'),
       (L_JAL('アメリカン便(提携特典)'), '距離制・要確認', ZERO, '羽田-NY直行のAA便なら燃油ゼロ(二次)'),
     ],
     notes=['ヴァージン×ANA便(電話発券)は往復C 120,000相当・二次情報。'], warns=[]),
dict(id='losangeles', flag='🌴', city='ロサンゼルス', country='アメリカ', rg='namerica', rgl='北米',
     time='約10時間', t='t3', b='b3', yq1=False, dk='JAL(週5〜毎日)', dt='JAL・ANA・AA(羽田)',
     data=dict(jal=54000, ana=40000),
     minv='40,000', minprog='ANA(L)', minmark=False, yqlist=LNG, kx='○JAL', tk='○JAL/ANA/AA',
     rows=[
       (L_JAL(), '<b>54,000</b><span class="small">(C 110,000)</span>', LNG, '<b>関空-LA直行(JL60/69)</b>。2025年6月改定後の確認値'),
       (L_ANA(), ana_lrh(40000,50000,72000), LNG, 'Lなら40,000=MR年間上限内'),
       (L_JAL('アメリカン便(提携特典)'), '距離制・要確認', ZERO, '羽田-LA直行のAA便なら燃油ゼロ(二次)'),
     ],
     notes=['関西から直行でアメリカ本土に行ける唯一のJAL路線。'], warns=[]),
dict(id='sanfrancisco', flag='🌉', city='サンフランシスコ', country='アメリカ', rg='namerica', rgl='北米',
     time='約9.5時間', t='t3', b='b3', yq1=False, dk=None, dt='JAL(羽田)※・ANA',
     data=dict(jal=54000, ana=40000),
     minv='40,000', minprog='ANA(L)', minmark=False, yqlist=LNG, kx='—', tk='○JAL※/ANA',
     rows=[
       (L_JAL(), '<b>54,000</b><span class="small">(C 110,000)</span>', LNG, '2025年6月改定後の確認値'),
       (L_ANA(), ana_lrh(40000,50000,72000), LNG, 'Lなら40,000=MR年間上限内'),
     ],
     notes=[], warns=[]),
dict(id='vancouver', flag='🇨🇦', city='バンクーバー', country='カナダ', rg='namerica', rgl='北米',
     time='約9時間', t='t3', b='b4', yq1=True, dk=None, dt='エアカナダ(羽田・成田)※二次',
     data=dict(),
     minv=None, minprog='ANA提携(要確認)', minmark=True, yqlist='ゼロ可※', kx='—', tk='○AC※',
     rows=[
       (L_ANAP('エアカナダ便'), '提携チャート・要確認', ZERO, '直行AC便をANAマイルで発券(二次)'),
     ],
     notes=[], warns=['ワンワールドの直行便なし。ZIPAIR(成田直行・JAL系LCC)はここで扱うマイルの対象外。']),
]

def card(d):
    cls = f"dest rg-{d['rg']} {d['t']} {d['b']}"
    if d.get('dk'): cls += ' dk'
    if d.get('dt'): cls += ' dt'
    if d.get('yq1'): cls += ' yq1'
    attrs = ''.join(f' data-{k}="{v}"' for k, v in d.get('data', {}).items())
    jd, md, _key = LISTMETA[d['id']]
    csub = (f"{d['rgl']}・✈ {d['time']}<br>"
            f"JAL <span class=\"num\">{jd}</span> / MR <span class=\"num\">{md}</span> / 燃油 <span class=\"num\">{d['yqlist']}</span>")
    country = f'<span class="small"> {d["country"]}</span>' if d['country'] else ''
    rows = ''.join(
        f'<tr><td>{r[0]}</td><td>{r[1]}</td><td class="num">{r[2]}</td><td>{r[3]}</td></tr>'
        for r in d['rows'])
    notes = ''.join(f'<p class="dnote">💡 {n}</p>' for n in d['notes'])
    warns = ''.join(f'<p class="dwarn">⚠ {w}</p>' for w in d['warns'])
    return f'''<details class="{cls}"{attrs}>
  <summary><span class="flag">{d['flag']}</span><span style="flex:1;min-width:0"><span class="cname">{d['city']}{country}</span><span class="csub">{csub}</span></span><span class="spacer"><span class="badge okb reach">★射程内</span><span class="chev">▶</span></span></summary>
  <div class="dbody">
    <p class="small" style="margin:2px 0 6px">🛫 関西から: {d.get('dk') or '直行なし'} / 東京から: {d.get('dt') or '直行なし'}</p>
    <div class="tbl"><table><thead><tr><th>使うマイル</th><th>往復エコノミー</th><th>燃油(往復)</th><th>メモ</th></tr></thead><tbody>{rows}</tbody></table></div>
    {notes}{warns}
  </div>
</details>'''

def listrow(d):
    jd, md, key = LISTMETA[d['id']]
    country = f'<span class="lco">{d["country"]}</span>' if d['country'] else ''
    dirs = f"直行: 関 {'○' if d.get('dk') else '—'}・東 {'○' if d.get('dt') else '—'}"
    return key, (
        f'<div class="lrow"><div class="lrow-top"><span class="lflag">{d["flag"]}</span>'
        f'<b>{d["city"]}</b>{country}<span class="ldir">{dirs}</span></div>'
        f'<div class="lnums">'
        f'<span class="lnum"><small>JALマイルで</small><b>{jd}</b></span>'
        f'<span class="lnum"><small>MR移行で最安</small><b>{md}</b></span>'
        f'<span class="lnum"><small>燃油(往復)</small><b>{d["yqlist"]}</b></span>'
        f'</div></div>')

cards_html = '<!-- DESTCARDS:BEGIN (生成: travel_tools/dev/gen_mile_compass_cards.py・データ確認日2026-07-16) -->\n' \
    + '\n'.join(card(d) for d in D) + '\n<!-- DESTCARDS:END -->'
rows_sorted = sorted((listrow(d) for d in D), key=lambda x: x[0])
list_html = '<!-- LISTROWS:BEGIN -->\n' + '\n'.join(r[1] for r in rows_sorted) + '\n<!-- LISTROWS:END -->'

with open(HTML, encoding='utf-8') as f:
    src = f.read()

def _swap(text, name, block):
    pat = re.compile('<!-- ' + name + ':BEGIN.*?<!-- ' + name + ':END -->', re.S)
    hits = pat.findall(text)
    if len(hits) != 1:
        sys.exit(f'marker {name}: expected exactly 1, found {len(hits)}')
    return pat.sub(lambda m: block, text)

src = _swap(src, 'DESTCARDS', cards_html)
src = _swap(src, 'LISTROWS', list_html)
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(src)
print(f'OK: {len(D)} destinations injected, file size {len(src):,} bytes')
