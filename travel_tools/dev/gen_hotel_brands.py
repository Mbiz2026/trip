# -*- coding: utf-8 -*-
"""ホテルブランド図鑑(travel_tools/hotel_brands.html)のブランドカードを生成して差し込む。

使い方: このファイルの MARRIOTT / HILTON / HYATT のデータを編集 →
`python3 travel_tools/dev/gen_hotel_brands.py` → HTML内の
<!-- MARRIOTT:BEGIN -->〜<!-- MARRIOTT:END --> などが丸ごと差し替わる(冪等)。

データの出どころ(すべて公式・確認日 2026-08-26):
  ・マリオットの区分/日本語ブランド名 … 公式ブランド紹介ページ marriott.com/ja/brands.mi
  ・マリオットの軒数・室数・品質段階 … Marriott International 2025年12月期 Form 10-K(2026-02-10提出)
  ・ヒルトンの6区分とブランド割り当て … Hilton 投資家向けプレゼン 2026年8月版(ir.hilton.com)
  ・ヒルトンの軒数・室数・展開国数 … Hilton Worldwide Holdings 2025年12月期 Form 10-K(2026-02-11提出)
  ・ヒルトンの新ブランド … 公式ニュースルーム stories.hilton.com の各プレスリリース
  ・ハイアットの5ポートフォリオ・室数・クラス・ブランド説明 … Hyatt Hotels 2025年12月期 Form 10-K(2026-02-13提出)
各社の10-Kは毎年2月ごろ更新されるので、そのタイミングで軒数・室数とブランドの増減を見直すこと。
推測で数字を足さないこと(公式に無い数値は num='' にして本文で説明する)。
"""
import re, sys

HTML = '/home/user/trip/travel_tools/hotel_brands.html'


def b(en, ja='', num='', desc='', chips=()):
    return dict(en=en, ja=ja, num=num, desc=desc, chips=list(chips))


# ============================== マリオット ==============================
MARRIOTT = [
    dict(cls='t-lux', en='LUXURY', ja='ラグジュアリー',
         lede='公式ブランド一覧の最上段。3ブランドだけが「ラグジュアリー」と表示される。',
         brands=[
             b('The Ritz-Carlton', 'ザ・リッツ・カールトン', '126軒 / 32,279室',
               'マリオットの看板となる最上級ブランド。米国・カナダ43軒、アジア太平洋24軒、中華圏19軒と地域の偏りが小さい。'),
             b('St. Regis', 'セントレジス', '66軒 / 14,241室',
               '公式は「完璧なサービスと現代の贅沢」を掲げる最上級。中東・アフリカと中華圏に各15軒あり、新興都市の旗艦ホテルに多い。'),
             b('JW Marriott', 'JWマリオット', '130軒 / 50,891室',
               'ラグジュアリー段では最大規模で、1軒あたり約390室。宴会場やスパを備えた大型の都市型・リゾート型が中心。'),
         ]),
    dict(cls='t-lux', en='DISTINCTIVE LUXURY', ja='ディスティンクティブ ラグジュアリー',
         lede='同じ最上段のうち、公式が「個性の強いラグジュアリー」として別に並べているグループ。',
         brands=[
             b('The Ritz-Carlton Reserve', 'ザ・リッツ・カールトン・リザーブ', '10-Kに単独記載なし',
               '世界に数えるほどしかない超小規模リゾート。公式は「日常から隔絶された特別な場所」と説明する。軒数はリッツ・カールトンと分けて公表されていない。',
               ['最小規模']),
             b('The Luxury Collection', 'ラグジュアリーコレクション', '132軒 / 32,724室',
               'その土地を象徴する独立系ホテルを集めた枠。ヨーロッパ45軒が最多。', ['ソフトブランド']),
             b('W Hotels', 'Wホテル', '72軒 / 20,233室',
               '公式が「ラグジュアリーなライフスタイルブランドの代表格」と位置づけるデザイン重視の系統。'),
             b('EDITION', 'エディション', '22軒 / 4,617室',
               '22軒だけの少数精鋭。デザイン・食・エンターテインメントを一体にした新世代ラグジュアリー(公式)。'),
             b('Bvlgari Hotels', 'ブルガリ', '9軒 / 807室',
               '宝飾ブランドとの共同ブランド。10-Kではラグジュアリー段に載るが、公式のブランド紹介ページには出てこない(2026年8月時点)。米国・カナダには無く、ヨーロッパ4軒が最多。',
               ['公式一覧に非掲載']),
         ]),
    dict(cls='t-full', en='PREMIUM', ja='プレミアム',
         lede='上級フルサービス。ラウンジや複数のレストラン、宴会場を持つ大型が中心。',
         brands=[
             b('Marriott Hotels', 'マリオット・ホテル', '619軒 / 218,237室',
               'グループの中核ブランド。どの地域にもまとまった数があり、出張・観光どちらでも選択肢に入りやすい。'),
             b('Sheraton', 'シェラトン', '436軒 / 147,958室',
               '公式が「世界400以上のコミュニティに根付く」と説明する老舗。中華圏103軒はプレミアム段で最多。'),
             b('Westin', 'ウェスティン', '251軒 / 89,984室',
               '睡眠・運動などウェルビーイングを前面に出す。米国・カナダ137軒が中心。'),
             b('Le Méridien', 'ルメリディアン', '122軒 / 31,996室',
               'ヨーロッパ流の「佳き人生」を掲げるブランド(公式)。中東・アフリカ19軒、アジア太平洋36軒と国際色が濃い。'),
             b('Renaissance Hotels', 'ルネッサンス・ホテル', '180軒 / 54,077室',
               '土地ごとの発見を掲げるブランド。米国・カナダ92軒、中華圏34軒。'),
             b('Delta Hotels by Marriott', 'デルタ・ホテル・バイ・マリオット', '137軒 / 30,803室',
               'カナダ発。米国・カナダ91軒とヨーロッパ30軒でほぼ全体を占め、アジア太平洋にはない。'),
             b('Gaylord Hotels', 'ゲイロード・ホテル', '7軒 / 11,820室',
               '巨大アトリウムや屋内ウォーターパークを持つ超大型リゾート。米国7軒のみで、1軒あたり約1,690室。'),
             b('The Marriott Vacation Clubs', 'マリオット・バケーション・クラブ', '95軒 / 22,912室',
               '会員制(タイムシェア)。公式ブランド一覧ではプレミアムに並ぶが、10-Kでは別枠のTimeshareとして集計されている。',
               ['会員制']),
         ]),
    dict(cls='t-sel', en='SELECT', ja='セレクト',
         lede='中級。必要十分な設備で価格を抑えた実用ブランド群。マリオットの軒数の大半はここ。',
         brands=[
             b('Courtyard', 'コートヤード', '1,362軒 / 206,090室',
               'セレクト段の代表格。米国・カナダ1,083軒を軸に、世界各地の郊外・空港近くに広く分布。'),
             b('Four Points', 'フォーポイント', '384軒 / 72,408室',
               'シェラトン系の実用ブランド。中華圏102軒、アジア太平洋57軒とアジアでの存在感が大きい。'),
             b('SpringHill Suites', 'スプリングヒル・スイート', '579軒 / 68,370室',
               '広めのスイート型セレクト。579軒すべてが米国・カナダ。'),
             b('Fairfield by Marriott', 'フェアフィールド・バイ・マリオット', '1,381軒 / 140,748室',
               '軒数はマリオットのブランドで最多。米国・カナダ1,191軒に加え、中華圏94軒・アジア太平洋77軒。'),
             b('AC Hotels', 'ACホテル', '267軒 / 42,828室',
               'スペイン発のミニマル系デザイン。ヨーロッパ88軒と米国・カナダ142軒が中心。'),
             b('citizenM', 'citizenM', '37軒 / 8,789室',
               'オランダ発のコンパクト・ハイテク型。都心立地が中心で、米国16軒・ヨーロッパ19軒。マリオットのブランド一覧に加わったのは最近。'),
             b('Aloft Hotels', 'アロフトホテル', '243軒 / 39,816室',
               '都会的な内装と広いロビーの社交空間が売り。米国・カナダ169軒。'),
             b('Moxy Hotels', 'モクシー・ホテル', '181軒 / 34,042室',
               '小さめの部屋と広いラウンジという構成。ヨーロッパ104軒が最多で、欧州旅行では選択肢に入りやすい。'),
             b('Protea Hotels by Marriott', 'プロテア・ホテル', '65軒 / 7,020室',
               '公式が「アフリカ最大のホテルブランド」と説明。65軒すべてが中東・アフリカ地域。'),
             b('City Express by Marriott', 'シティエクスプレス', '158軒 / 18,910室',
               'メキシコ発。158軒のうち147軒が中南米。', ['10-Kはミッドスケール']),
             b('Four Points Flex by Sheraton', 'フォーポイント フレックス', '54軒 / 7,806室',
               '必需品に絞った低価格版フォーポイント。ヨーロッパ34軒・アジア太平洋16軒で、米国・カナダにはまだない。',
               ['10-Kはミッドスケール']),
             b('Series by Marriott', 'Series by Marriott', '39軒 / 2,761室',
               '地域の既存ホテルブランドが名前を残したままマリオットの予約網に入る枠。39軒中37軒がアジア太平洋。',
               ['ソフトブランド', '10-Kはセレクト+ミッドスケール']),
         ]),
    dict(cls='t-stay', en='LONGER STAYS', ja='長期滞在',
         lede='キッチンや洗濯機がついた「暮らす」タイプ。1週間以上の滞在なら同じ予算でも快適なことが多い。',
         brands=[
             b('Residence Inn', 'レジデンス・イン', '937軒 / 115,333室',
               '長期滞在の代表格。937軒中889軒が米国・カナダ。', ['10-Kはセレクト']),
             b('TownePlace Suites', 'タウンプレース・スイート', '571軒 / 57,577室',
               '価格を抑えた長期滞在型。571軒すべてが米国・カナダ。', ['10-Kはセレクト']),
             b('Element Hotels', 'エレメントホテル', '122軒 / 17,568室',
               'ウェスティン系の長期滞在。健康志向の設計を掲げる。米国・カナダ102軒。', ['10-Kはセレクト']),
             b('StudioRes', 'StudioRes', '4軒 / 496室',
               '立ち上げ期の新しい長期滞在ブランド。2025年末時点で米国に4軒のみ。', ['立ち上げ期']),
             b('Homes &amp; Villas by Marriott Bonvoy', 'ホーム＆ヴィラ・バイ・マリオットボンヴォイ', '2,000軒超(公式)',
               '一棟貸しの民泊型。米国・ヨーロッパ・カリブ海・中南米の100以上の地域で2,000軒超(公式)。10-Kの軒数集計には含まれない。'),
             b('Apartments by Marriott Bonvoy', 'アパートメント・バイ・マリオットボンヴォイ', '5軒 / 656室',
               '寝室と居間が分かれ、キッチンと洗濯乾燥機がつくアパート型。まだ5軒。', ['立ち上げ期']),
             b('Marriott Executive Apartments', 'マリオット・エグゼクティブ・アパートメント', '50軒 / 7,735室',
               '海外赴任者向けの家具付きアパート。中東・アフリカ18軒、アジア太平洋15軒、中華圏12軒で、米国・カナダにはない。'),
         ]),
    dict(cls='t-coll', en='COLLECTIONS', ja='コレクション',
         lede='独立系ホテルが自分の名前を保ったまま参加する「ソフトブランド」。同じ枠でも価格も設備もバラバラ。',
         brands=[
             b('Autograph Collection', 'オートグラフ コレクション', '362軒 / 76,399室',
               'コレクション枠で最大。ブティックからラグジュアリーまで幅があり、ブランド名だけでは格が読めない。'),
             b('Tribute Portfolio', 'トリビュートポートフォリオ', '186軒 / 30,919室',
               '独自の個性を持つ独立系ホテル＆リゾートの集合体(公式)。米国・カナダ102軒、ヨーロッパ36軒。'),
             b('Design Hotels', 'Design Hotels', '223軒 / 15,488室',
               'デザイン重視の独立系。223軒中127軒がヨーロッパで、1軒あたり約70室と小規模が多い。'),
             b('MGM Collection with Marriott Bonvoy', 'MGMコレクション', '12軒 / 26,210室',
               'MGMリゾーツの大型カジノリゾートをボンヴォイで予約できる枠。米国12軒で26,210室と1軒あたりが巨大。'),
             b('Outdoor Collection by Marriott Bonvoy', 'Outdoor Collection', '32軒 / 1,532室',
               '自然の中のキャビンなどを集めた枠。米国32軒。', ['10-Kはプレミアム+セレクト']),
         ]),
]

# ============================== ヒルトン ==============================
HILTON = [
    dict(cls='t-lux', en='LUXURY', ja='ラグジュアリー',
         lede='投資家向け資料での最上段。5ブランド。',
         brands=[
             b('Waldorf Astoria Hotels &amp; Resorts', '', '39軒 / 9,688室・21の国と地域',
               'ヒルトンの最上級。各地のランドマークとなるホテルで構成される(公式)。'),
             b('Conrad Hotels &amp; Resorts', '', '50軒 / 17,064室・24の国と地域',
               '公式が「ヒルトンのラグジュアリー群で最大」と説明。大胆なデザインと現代アートを掲げる。'),
             b('LXR Hotels &amp; Resorts', '', '18軒 / 2,943室・9の国と地域',
               '独立系のラグジュアリーを集めるコレクション型。1軒あたり約160室と小規模。', ['ソフトブランド']),
             b('NoMad Hotels', '', '1軒 / 91室',
               '2024年にヒルトンが出資したブランド(10-K)。2025年末時点で運営中は1軒のみ。', ['立ち上げ期']),
             b('Signia by Hilton', '', '5軒 / 3,293室',
               '大型の会議・イベント需要に向けた最上級。5軒で3,293室と1軒あたりが大きい。'),
         ]),
    dict(cls='t-life', en='LIFESTYLE', ja='ライフスタイル',
         lede='デザイン系と、独立系ホテルを集めるコレクションはすべてここ。9ブランドと最も数が多い区分。',
         brands=[
             b('Canopy by Hilton', '', '48軒 / 8,496室・15の国と地域',
               '街の個性に寄せたブティック型(公式)。'),
             b('Curio Collection by Hilton', '', '196軒 / 38,349室・47の国と地域',
               'ヒルトン最大のソフトブランド。個性のある独立系ホテルを集める枠で、格は物件ごとにかなり違う。',
               ['ソフトブランド']),
             b('Tapestry Collection by Hilton', '', '192軒 / 23,864室・25の国と地域',
               '独立系を集めるもう一つのコレクション。1軒あたり約124室で、Curio(約196室)より小ぶりな物件が多い。',
               ['ソフトブランド']),
             b('Graduate by Hilton', '', '35軒 / 5,881室',
               '大学町に特化したデザインホテル。2024年にヒルトンが買収(10-K)。'),
             b('Undergraduate by Hilton', '', '2026年6月発表・未開業',
               'Graduateより手頃な価格帯として発表されたアッパーミッドスケール。1号店は2027年開業予定で、営業中の物件はまだない(公式発表)。',
               ['2026年発表', '未開業']),
             b('Tempo by Hilton', '', '6軒 / 1,424室',
               '生活のリズムを崩さない設計を掲げる新しめのブランド。まだ6軒。', ['立ち上げ期']),
             b('Motto by Hilton', '', '10軒 / 2,261室・5の国と地域',
               '街の中心に小さな部屋で泊まるマイクロホテル型。'),
             b('Outset Collection by Hilton', '', '2軒 / 268室',
               '2025年10月に発表されたヒルトン25番目のブランド。物語性のある独立系を集める枠で、対象は米国・カナダ。60軒以上が開発中。',
               ['2025年発表', 'ソフトブランド']),
             b('Select by Hilton', '', '2026年3月発表',
               '既存の独立ブランドが名前と運営を保ったままヒルトンの予約網とオナーズに参加する枠。第1弾は10か国23軒のYOTELで、2026年後半からヒルトン経由で予約できる予定。',
               ['2026年発表', 'ソフトブランド']),
         ]),
    dict(cls='t-full', en='FULL SERVICE', ja='フルサービス',
         lede='レストラン・宴会場を備えた上級の主力。2ブランドだけだが、軒数・室数はグループの柱。',
         brands=[
             b('Hilton Hotels &amp; Resorts', '', '622軒 / 228,611室・94の国と地域',
               'チェーンの看板ブランド。94の国と地域という展開の広さはヒルトンで最大。'),
             b('DoubleTree by Hilton', '', '715軒 / 160,138室・62の国と地域',
               '上級系では最も軒数が多い中〜上級フルサービス。62の国と地域に展開。'),
         ]),
    dict(cls='t-stay', en='ALL SUITES', ja='オールスイート',
         lede='全室がスイートまたはキッチン付き。ヒルトンの長期滞在系はここにまとまっている。',
         brands=[
             b('Embassy Suites by Hilton', '', '270軒 / 62,316室・8の国と地域',
               '寝室と居間が分かれた2ルーム型の上級ブランド。1軒あたり約231室と大きめ。'),
             b('Homewood Suites by Hilton', '', '559軒 / 64,243室・5の国と地域',
               'キッチン付きの長期滞在型。展開はほぼ北米。'),
             b('Home2 Suites by Hilton', '', '865軒 / 95,347室・3の国と地域',
               '公式が「価値重視の旅行者向け」と位置づける長期滞在型。3の国と地域で865軒と、軒数の伸びが大きい。'),
             b('LivSmart Studios by Hilton', '', '2軒 / 226室',
               '数週間〜数か月の滞在向けスタジオ型。2025年末で2軒と立ち上げ期。', ['立ち上げ期']),
             b('Apartment Collection by Hilton', '', '2026年1月発表',
               'スタジオ〜4ベッドルームの家具付きアパートをヒルトン経由で予約できる新枠。ニューヨーク・ワシントンD.C.・アトランタから2026年前半に予約開始予定(公式発表)。',
               ['2026年発表']),
         ]),
    dict(cls='t-sel', en='FOCUSED SERVICE', ja='フォーカストサービス',
         lede='中級〜手頃。ヒルトンの軒数の大半を占める実用ブランド群。',
         brands=[
             b('Hilton Garden Inn', '', '1,124軒 / 165,782室・65の国と地域',
               '中級の主力。65の国と地域に1,124軒と、世界のどこでも見つけやすい。'),
             b('Hampton by Hilton', '', '3,195軒 / 359,886室・46の国と地域',
               'ヒルトン最大のブランドで、全客室の約27%を占める。46の国と地域に3,195軒。'),
             b('Tru by Hilton', '', '338軒 / 32,937室・7の国と地域',
               '遊び心のある内装で価格を抑えた区分。'),
             b('Spark by Hilton', '', '228軒 / 20,191室・9の国と地域',
               'ヒルトンの中で最も価格を抑えた区分。9の国と地域で228軒。'),
         ]),
    dict(cls='t-club', en='TIMESHARE', ja='タイムシェア(会員制)', n=3,
         lede='部屋の利用権を買う会員制で、通常の宿泊予約とは別枠。3ブランドをまとめて1枚のカードにしている。',
         brands=[
             b('Hilton Club / Hilton Grand Vacations Club / Hilton Vacation Club', '', '合計114軒 / 20,404室・8の国と地域',
               '3つのタイムシェアブランド。Hilton Grand Vacations社が長期ライセンスに基づいて独占的に使用している(10-K)。',
               ['会員制']),
         ]),
]

# ============================== ハイアット ==============================
HYATT = [
    dict(cls='t-lux', en='LUXURY PORTFOLIO', ja='ラグジュアリー',
         lede='ハイアットの最上段。5ブランド。',
         brands=[
             b('Park Hyatt', '', '9,376室', 'ハイアットの最上位ブランド。「静かなラグジュアリー」を掲げ、文化・金融の中心都市と隠れ家的な保養地に構える(公式)。',
               ['Luxury']),
             b('Alila', '', '1,947室', '自然と一体化したデザインの隠れ家型リゾート(公式)。', ['Luxury']),
             b('Miraval', '', '383室', '大人限定のウェルネス専門リゾート。全体で383室と小規模。', ['Luxury・ウェルネス']),
             b('Impression by Secrets', '', '323室', '大人限定の最上級オールインクルーシブ。', ['Luxury・オールインクルーシブ']),
             b('The Unbound Collection by Hyatt', '', '9,278室',
               '物語性のある独立系ホテルを集めたコレクション(公式)。', ['Luxury', 'ソフトブランド']),
         ]),
    dict(cls='t-life', en='LIFESTYLE PORTFOLIO', ja='ライフスタイル',
         lede='デザイン・社交寄りの9ブランド。クラス表記はLuxuryからUpscaleまで幅がある。',
         brands=[
             b('Andaz', '', '7,970室', 'ヒンディー語で「自分らしいスタイル」。土地の文化を取り込んだ都市型(公式)。', ['Luxury']),
             b('Thompson Hotels', '', '3,854室', '定番を洗練させた作りのデザイン系(公式)。', ['Luxury']),
             b('The Standard', '', '1,966室', '飲食とイベントで街の話題をつくるタイプ。25年以上の歴史があるブランド(公式)。', ['Upper Upscale']),
             b('The StandardX', '', '187室', 'The Standardの小型版。これから伸びる地区に小さく出す位置づけ(公式)。', ['Upper Upscale', '立ち上げ期']),
             b('Dream Hotels', '', '986室', '社交空間を前面に出した都市型(公式)。', ['Upper Upscale']),
             b('Breathless Resorts &amp; Spas', '', '2,311室', '大人限定・社交的なビーチリゾート。', ['Luxury・オールインクルーシブ']),
             b('JdV by Hyatt', '', '8,336室', '「joie de vivre(生きる喜び)」が名前の由来。街の個性を映す独立系の集合体(公式)。',
               ['Upper Upscale', 'ソフトブランド']),
             b('Bunkhouse Hotels', '', '498室', '地域に根ざしたデザインホテル群(公式)。', ['Upper Upscale']),
             b('Me and All Hotels', '', '1,364室', '都市の社交型。全室がフランチャイズ運営。', ['Upscale']),
         ]),
    dict(cls='t-ai', en='INCLUSIVE COLLECTION', ja='オールインクルーシブ',
         lede='食事・ドリンク込みのリゾート専門群。10-Kによると中心はメキシコとカリブ海。3社の中でハイアットだけが専用ブランドを持つ。',
         brands=[
             b('Zoëtry Wellness &amp; Spa Resorts', '', '543室', '小規模で親密なウェルネス型。', ['Luxury AI']),
             b('Hyatt Ziva', '', '2,578室', '家族向けのオールインクルーシブ。', ['Luxury AI']),
             b('Hyatt Zilara', '', '1,320室', '大人限定のオールインクルーシブ。', ['Luxury AI']),
             b('Secrets Resorts &amp; Spas', '', '10,697室', '大人・カップル向け。この区分では2番目の規模。', ['Luxury AI']),
             b('Dreams Resorts &amp; Spas', '', '14,712室', '家族向けで、この区分では最大規模。', ['Luxury AI']),
             b('Hyatt Vivid Hotels &amp; Resorts', '', '924室', '若い世代向けのカジュアルなオールインクルーシブ。', ['Upper Upscale AI']),
             b('Bahia Principe Hotels &amp; Resorts', '', '11,648室', '大型で価値重視のオールインクルーシブ。ハイアット側の合弁が保有するブランド(10-K)。',
               ['Upper Upscale AI']),
             b('Alua Hotels &amp; Resorts', '', '8,705室', '手頃な価格帯の海辺リゾート。', ['Upscale AI']),
             b('Sunscape Resorts &amp; Spas', '', '4,147室', '予算重視の家族向け。キッズクラブやウォーターパークが基本(公式)。', ['Upper Upscale AI']),
         ]),
    dict(cls='t-full', en='CLASSICS PORTFOLIO', ja='クラシックス',
         lede='昔からの主力。宴会場や会議室を備えた大型が中心で、ハイアットの室数の大半はここ。',
         brands=[
             b('Grand Hyatt', '', '34,467室', '都市のランドマークとなる大型旗艦。この区分では2番目の規模。', ['Luxury']),
             b('Hyatt Regency', '', '99,105室', 'ハイアット最大のブランド。会議・イベント対応の大型ホテルが中心。', ['Upper Upscale']),
             b('Destination by Hyatt', '', '6,806室', '土地の個性を映す一点もののホテル・リゾートを集めた枠(公式)。',
               ['Luxury', 'ソフトブランド']),
             b('Hyatt Centric', '', '14,961室', '街の中心に構える現代的なフルサービス(公式)。', ['Upper Upscale']),
             b('Hyatt', '', '3,473室', '「Hyatt」の名前だけを使う小型のフルサービス(公式)。', ['Upper Upscale']),
             b('Hyatt Vacation Club', '', '室数の公表なし', 'ポイント制の会員制(タイムシェア)。滞在をWorld of Hyattのボーナスポイントに替えることもできる(公式)。',
               ['会員制']),
         ]),
    dict(cls='t-sel', en='ESSENTIALS PORTFOLIO', ja='エッセンシャルズ',
         lede='実用重視。価格を抑えた中級〜中位で、フランチャイズ運営の比率が高い。',
         brands=[
             b('Caption by Hyatt', '', '1,000室', '社交空間を重視した軽めのライフスタイル型(公式)。', ['Upscale']),
             b('Unscripted by Hyatt', '', '1,854室', '独立系ホテルが最小限の変更でハイアットに参加できる枠(公式)。',
               ['Upscale', 'ソフトブランド']),
             b('Hyatt Place', '', '67,416室', 'エッセンシャルズの主力。必要なものだけを備えたセレクトサービス型で、室数の7割超がフランチャイズ運営。',
               ['Upscale']),
             b('Hyatt House', '', '20,396室', 'キッチン付きスイートの長期滞在型(公式)。', ['Upscale・長期滞在']),
             b('Hyatt Studios', '', '242室', '新しい中価格帯の長期滞在ブランド。2025年末で242室と立ち上げ期。',
               ['Upper Midscale', '立ち上げ期']),
             b('Hyatt Select', '', '203室', '朝食込み・24時間セルフマーケットなど基本を押さえた新しい中価格帯ブランド(公式)。立ち上げ期。',
               ['Upper Midscale', '立ち上げ期']),
             b('UrCove', '', '10,147室', '中国本土の中価格帯向けに作られたブランド(公式)。合弁が保有し、全室がフランチャイズ運営。',
               ['Upper Midscale']),
         ]),
]

NEWCHIPS = ('2026年発表', '2025年発表', '未開業', '立ち上げ期')


def render_brand(br):
    ja = f'<span class="bja">{br["ja"]}</span>' if br['ja'] else ''
    num = f'<span class="bnum">{br["num"]}</span>' if br['num'] else ''
    chips = ''
    if br['chips']:
        items = ''.join(
            f'<span class="chip{" new" if c in NEWCHIPS else " tone"}">{c}</span>' for c in br['chips'])
        chips = f'<div class="btags">{items}</div>'
    return (f'<div class="brand"><div class="btop"><span class="bname">{br["en"]}</span>{ja}{num}</div>'
            f'<p class="bdesc">{br["desc"]}</p>{chips}</div>')


def render_tier(t, tid):
    brands = '\n'.join('  ' + render_brand(br) for br in t['brands'])
    return (f'<div class="tier {t["cls"]}" id="{tid}">\n'
            f'  <div class="thead"><span class="ten">{t["en"]}</span><h3>{t["ja"]}</h3></div>\n'
            f'  <p class="tlede">{t["lede"]}</p>\n{brands}\n</div>')


def block(name, tiers):
    pre = name[:3].lower()
    ids = [f'{pre}-t{i + 1}' for i in range(len(tiers))]
    toc = '<div class="tocrow">' + ''.join(
        f'<a class="tchip" href="#{i}">{t["ja"]} <span class="small">{t.get("n", len(t["brands"]))}</span></a>'
        for i, t in zip(ids, tiers)) + '</div>'
    body = '\n'.join(render_tier(t, i) for t, i in zip(tiers, ids))
    n = sum(t.get('n', len(t['brands'])) for t in tiers)
    return (f'<!-- {name}:BEGIN (生成: travel_tools/dev/gen_hotel_brands.py・確認日2026-08-26・{n}ブランド) -->\n'
            f'{toc}\n{body}\n<!-- {name}:END -->')


def swap(text, name, new):
    pat = re.compile('<!-- ' + name + ':BEGIN.*?<!-- ' + name + ':END -->', re.S)
    if len(pat.findall(text)) != 1:
        sys.exit(f'marker {name}: expected exactly 1, found {len(pat.findall(text))}')
    return pat.sub(lambda m: new, text)


with open(HTML, encoding='utf-8') as f:
    src = f.read()

for name, data in (('MARRIOTT', MARRIOTT), ('HILTON', HILTON), ('HYATT', HYATT)):
    src = swap(src, name, block(name, data))

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(src)

total = sum(sum(len(t['brands']) for t in d) for d in (MARRIOTT, HILTON, HYATT))
print(f'OK: {total} brands injected '
      f'(marriott {sum(len(t["brands"]) for t in MARRIOTT)} / '
      f'hilton {sum(len(t["brands"]) for t in HILTON)} / '
      f'hyatt {sum(len(t["brands"]) for t in HYATT)}), file size {len(src):,} bytes')
