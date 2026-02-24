# CSSセレクタ特定

## やること
html_analysis.md の調査結果をもとに、具体的なCSSセレクタを確定する。

## 確定するセレクタ

### 一覧ページ用
| 用途 | セレクタ | 備考 |
|------|---------|------|
| 物件リンク | | 物件詳細ページへのリンク |
| 次ページ | | ページネーション「次へ」ボタン |
| 総件数 | | 「全N件」の表示（あれば） |

### 詳細ページ用
| 用途 | セレクタ | 備考 |
|------|---------|------|
| タイトル | | 物件名 |
| 価格 | | 販売価格 |
| 情報テーブル | | メイン物件情報テーブル |
| テーブルラベル | | th or dt |
| テーブル値 | | td or dd |
| 会社名 | | 掲載元会社 |
| 会社電話番号 | | （取得する場合） |
| 物件ID | | URL or ページ内要素から |

## 検証方法
```python
# BeautifulSoupで検証
from bs4 import BeautifulSoup

with open("/tmp/{site}_{page_type}.html") as f:
    soup = BeautifulSoup(f, "html.parser")

# セレクタが正しく要素を取得できるか確認
elements = soup.select("セレクタ")
print(f"取得要素数: {len(elements)}")
for el in elements[:3]:
    print(el.text.strip()[:100])
```

## 出力
確定したセレクタを `selectors.py` の形式で記録：
```python
SELECTORS = {
    "listing": {
        "property_link": "セレクタ",
        "next_page": ["セレクタ1", "セレクタ2"],  # フォールバック
        "total_count": "セレクタ",
    },
    "detail": {
        "title": "セレクタ",
        "price": "セレクタ",
        "info_table": "セレクタ",
        "table_label": "セレクタ",
        "table_value": "セレクタ",
        "company_name": "セレクタ",
        "company_phone": "セレクタ",
        "listing_id": "セレクタ or URL正規表現",
    },
}
```

## 完了条件
- [ ] 一覧ページのセレクタが確定した
- [ ] 詳細ページのセレクタが確定した
- [ ] 各セレクタでサンプルHTMLから正しく要素が取得できた
- [ ] フォールバックセレクタを検討した（構造変更耐性）

## 次の工程
→ pagination.md
