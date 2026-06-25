# 車載ソフトウェア 要件定義 自動生成アプリ

要求ファイル（Markdown / テキスト / Excel / CSV / Word / PDF）をアップロードすると、
Claude API が解析して **ASPICE・ISO 26262 を踏まえた構造化された要件定義** を自動生成し、
ブラウザ上で確認・編集・ダウンロード（Markdown / Excel）できる Web アプリです。

## 特徴

- 複数の要求ファイル形式に対応（Markdown / テキスト / CSV / Excel / Word / PDF）
- 要件を機能 / 非機能 / 安全 / インタフェース / 制約に分類
- 各要件に 要件ID・ASIL等級・優先度・導出根拠・トレーサビリティ（出典）・検証方法・受入基準 を付与
- 曖昧・不足している点は「オープンイシュー」として列挙（創作で埋めない）
- ブラウザ上で表を編集し、Markdown / Excel(.xlsx) でダウンロード

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env を編集し ANTHROPIC_API_KEY を設定
```

## 起動

```bash
uvicorn app.main:app --reload
```

ブラウザで <http://localhost:8000> を開きます。

## 使い方

1. 要求ファイルを選択して「要件定義を生成」をクリック
2. 生成された要件テーブルを必要に応じて編集（行の追加・削除も可能）
3. 「Markdown でダウンロード」または「Excel でダウンロード」で出力

## テスト

抽出・エクスポート処理は LLM を呼ばずにテストできます。

```bash
pytest
```

## ディレクトリ構成

```
app/
  main.py        FastAPI エンドポイント + 静的配信
  extractors.py  ファイル形式別の抽出 (PDF は base64 で Claude へ)
  generator.py   Claude API 呼び出し (構造化出力)
  exporters.py   Markdown / Excel エクスポート
  schema.py      要件定義の Pydantic モデル
static/          フロントエンド (HTML / JS / CSS)
tests/           ユニットテスト
```

## 注意

- 生成結果は LLM による推定を含みます。**ASIL 等級や安全要件は必ず人手でレビュー**してください。
- API キーは `.env`（gitignore 済み）に保存し、コミットしないでください。
