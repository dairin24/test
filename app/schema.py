"""要件定義のデータモデル。

ASPICE (SYS.2 / SWE.1 を意識) および ISO 26262 を踏まえた構造化要件を表現する。
構造化出力 (output_config.format) では数値制約・文字列長制約が使えないため、
enum と必須項目を中心に定義している。
"""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field

RequirementType = Literal[
    "functional",      # 機能要件
    "non_functional",  # 非機能要件 (性能・信頼性など)
    "safety",          # 安全要件 (ISO 26262)
    "interface",       # インタフェース要件
    "constraint",      # 制約条件
]

# ISO 26262 ASIL 等級。判断できない場合は QM。
Asil = Literal["QM", "A", "B", "C", "D"]

Priority = Literal["high", "medium", "low"]

# 検証方法 (ASPICE の検証戦略を意識)
VerificationMethod = Literal["test", "analysis", "review", "inspection"]


class Requirement(BaseModel):
    """個々の要件。"""

    id: str = Field(description="一意な要件ID。例: SYS-REQ-001")
    title: str = Field(description="要件の短い見出し")
    description: str = Field(description="要件の内容。検証可能な形で記述する")
    type: RequirementType = Field(description="要件の種別")
    asil: Asil = Field(description="ISO 26262 ASIL 等級。不明確なら QM")
    priority: Priority = Field(description="優先度")
    rationale: str = Field(description="この要件を導出した根拠")
    source: str = Field(description="元の要求文への参照 (トレーサビリティ)")
    verification_method: VerificationMethod = Field(description="検証方法")
    acceptance_criteria: List[str] = Field(
        description="受入基準。各項目は検証可能な条件",
    )


class RequirementsSpec(BaseModel):
    """要件定義書全体。"""

    project_overview: str = Field(description="プロジェクト/対象システムの概要")
    requirements: List[Requirement] = Field(description="抽出・整理した要件の一覧")
    open_issues: List[str] = Field(
        description="要求が曖昧・不足している箇所や、確認が必要な事項",
    )
