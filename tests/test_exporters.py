"""エクスポートロジックのテスト (LLM 呼び出しなし)。"""

import io

import pytest

from app import exporters
from app.schema import Requirement, RequirementsSpec


def _sample_spec() -> RequirementsSpec:
    return RequirementsSpec(
        project_overview="ブレーキ制御システム",
        requirements=[
            Requirement(
                id="SYS-REQ-001",
                title="ブレーキ応答時間",
                description="ブレーキ指令を100ms以内に処理する",
                type="safety",
                asil="D",
                priority="high",
                rationale="安全上クリティカルなため",
                source="要求書 1.2 節",
                verification_method="test",
                acceptance_criteria=["応答時間 <= 100ms", "全速度域で成立"],
            )
        ],
        open_issues=["温度条件が未定義"],
    )


def test_to_markdown_contains_key_fields():
    md = exporters.to_markdown(_sample_spec())
    assert "# 要件定義書" in md
    assert "SYS-REQ-001" in md
    assert "ブレーキ応答時間" in md
    assert "温度条件が未定義" in md
    # 受入基準が <br> 区切りで埋め込まれている
    assert "応答時間 <= 100ms<br>全速度域で成立" in md


def test_to_markdown_escapes_pipes():
    spec = _sample_spec()
    spec.requirements[0].description = "a|b を含む"
    md = exporters.to_markdown(spec)
    assert "a\\|b" in md


def test_to_excel_produces_valid_workbook():
    openpyxl = pytest.importorskip("openpyxl")
    data = exporters.to_excel(_sample_spec())
    wb = openpyxl.load_workbook(io.BytesIO(data))
    assert "要件一覧" in wb.sheetnames
    assert "概要" in wb.sheetnames
    ws = wb["要件一覧"]
    values = [cell.value for cell in ws[1]]
    assert "ID" in values
    # データ行が存在する
    assert ws.cell(row=2, column=1).value == "SYS-REQ-001"
