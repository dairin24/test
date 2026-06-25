"""Claude API を用いて要求から要件定義を生成する。"""

from __future__ import annotations

import os
from typing import Optional

import anthropic
from dotenv import load_dotenv

from .extractors import ExtractResult
from .schema import RequirementsSpec

load_dotenv()

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000

SYSTEM_PROMPT = """\
あなたは車載ソフトウェア開発の要件アナリストです。
入力された「要求 (requirements / 要求仕様)」を分析し、開発で使える構造化された
「要件定義」へ落とし込みます。ASPICE (SYS.2 / SWE.1) と ISO 26262 を念頭に置きます。

守るべきこと:
- 要求を機能要件・非機能要件・安全要件・インタフェース要件・制約条件に分類する。
- 各要件に一意なID (SYS-REQ-001 形式の連番) を付与する。
- 各要件は検証可能な形 (曖昧語を避ける) で記述する。
- ISO 26262 の ASIL 等級を推定する。判断材料が不足する場合は QM とし、
  その旨を open_issues に記載する。創作で等級を断定しない。
- 各要件に導出根拠 (rationale)、元の要求文への参照 (source / トレーサビリティ)、
  検証方法、受入基準を付ける。
- 入力に書かれていない事項を勝手に要件化しない。曖昧・不足している点は
  open_issues に列挙する。
- 出力は日本語で記述する。
"""

USER_INSTRUCTION = """\
以下の要求ファイルの内容を読み取り、要件定義を生成してください。
"""


def _client() -> anthropic.Anthropic:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "環境変数 ANTHROPIC_API_KEY が設定されていません。"
            ".env に設定してください。"
        )
    return anthropic.Anthropic()


def _build_user_content(extracted: ExtractResult, filename: str) -> list:
    """抽出結果から user メッセージの content ブロックを組み立てる。"""
    if extracted.kind == "pdf":
        return [
            {"type": "text", "text": f"{USER_INSTRUCTION}\nファイル名: {filename}"},
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": extracted.pdf_base64,
                },
            },
        ]

    text = extracted.text or ""
    return [
        {
            "type": "text",
            "text": (
                f"{USER_INSTRUCTION}\nファイル名: {filename}\n\n"
                f"--- 要求ファイルの内容 ---\n{text}"
            ),
        }
    ]


def generate(extracted: ExtractResult, filename: str,
             client: Optional[anthropic.Anthropic] = None) -> RequirementsSpec:
    """抽出済みの要求から ``RequirementsSpec`` を生成する。"""
    client = client or _client()

    # messages.parse() は内部で output_config.format にスキーマを設定するため、
    # ここで output_config を渡すと競合しうる。effort はデフォルト high のため省略。
    response = client.messages.parse(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_content(extracted, filename)}],
        output_format=RequirementsSpec,
    )

    if response.parsed_output is None:
        raise RuntimeError(
            "要件定義の生成に失敗しました "
            f"(stop_reason={response.stop_reason})。"
        )
    return response.parsed_output
