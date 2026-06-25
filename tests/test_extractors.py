"""抽出ロジックのテスト (LLM 呼び出しなし)。"""

import base64
import io

import pytest

from app import extractors


def test_extract_markdown():
    data = "# 要求\n- ブレーキは100ms以内に応答する".encode("utf-8")
    result = extractors.extract("req.md", data)
    assert result.kind == "text"
    assert "ブレーキ" in result.text


def test_extract_txt_cp932():
    data = "速度を監視する".encode("cp932")
    result = extractors.extract("req.txt", data)
    assert result.kind == "text"
    assert "速度を監視する" in result.text


def test_extract_csv():
    data = b"id,requirement\n1,start engine\n2,stop engine\n"
    result = extractors.extract("req.csv", data)
    assert result.kind == "text"
    assert "start engine" in result.text
    assert "requirement" in result.text


def test_extract_pdf_returns_base64():
    data = b"%PDF-1.4 fake pdf bytes"
    result = extractors.extract("req.pdf", data)
    assert result.kind == "pdf"
    assert base64.standard_b64decode(result.pdf_base64) == data


def test_extract_excel():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"id": [1, 2], "req": ["a", "b"]})
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    result = extractors.extract("req.xlsx", buf.getvalue())
    assert result.kind == "text"
    assert "シート" in result.text


def test_extract_docx():
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_paragraph("システムはイグニッションONを検知する")
    buf = io.BytesIO()
    doc.save(buf)
    result = extractors.extract("req.docx", buf.getvalue())
    assert result.kind == "text"
    assert "イグニッション" in result.text


def test_unsupported_extension():
    with pytest.raises(extractors.UnsupportedFileError):
        extractors.extract("req.exe", b"data")
