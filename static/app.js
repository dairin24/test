"use strict";

// 要件テーブルの列定義 (キー, 入力タイプ, 選択肢)
const FIELDS = [
  { key: "id", type: "text" },
  { key: "title", type: "text" },
  { key: "type", type: "select",
    options: ["functional", "non_functional", "safety", "interface", "constraint"] },
  { key: "asil", type: "select", options: ["QM", "A", "B", "C", "D"] },
  { key: "priority", type: "select", options: ["high", "medium", "low"] },
  { key: "description", type: "area" },
  { key: "rationale", type: "area" },
  { key: "source", type: "text" },
  { key: "verification_method", type: "select",
    options: ["test", "analysis", "review", "inspection"] },
  { key: "acceptance_criteria", type: "area" }, // 改行区切りで保持
];

const $ = (id) => document.getElementById(id);

function setStatus(msg, isError = false) {
  const el = $("status");
  el.textContent = msg;
  el.classList.toggle("error", isError);
}

function makeCell(field, value) {
  const td = document.createElement("td");
  if (field.type === "select") {
    const sel = document.createElement("select");
    for (const opt of field.options) {
      const o = document.createElement("option");
      o.value = opt;
      o.textContent = opt;
      if (opt === value) o.selected = true;
      sel.appendChild(o);
    }
    td.appendChild(sel);
  } else {
    const ta = document.createElement("textarea");
    ta.rows = field.type === "area" ? 3 : 1;
    ta.value = value != null ? value : "";
    td.appendChild(ta);
  }
  td.dataset.key = field.key;
  return td;
}

function addRow(req) {
  req = req || {};
  const tbody = $("reqTable").querySelector("tbody");
  const tr = document.createElement("tr");

  for (const field of FIELDS) {
    let value = req[field.key];
    if (field.key === "acceptance_criteria" && Array.isArray(value)) {
      value = value.join("\n");
    }
    tr.appendChild(makeCell(field, value));
  }

  const delTd = document.createElement("td");
  const delBtn = document.createElement("button");
  delBtn.textContent = "削除";
  delBtn.className = "del-btn";
  delBtn.onclick = () => tr.remove();
  delTd.appendChild(delBtn);
  tr.appendChild(delTd);

  tbody.appendChild(tr);
}

function renderSpec(spec) {
  $("overview").value = spec.project_overview || "";
  const tbody = $("reqTable").querySelector("tbody");
  tbody.innerHTML = "";
  (spec.requirements || []).forEach(addRow);
  $("openIssues").value = (spec.open_issues || []).join("\n");
  $("result").classList.remove("hidden");
}

function collectSpec() {
  const requirements = [];
  const rows = $("reqTable").querySelectorAll("tbody tr");
  rows.forEach((tr) => {
    const req = {};
    tr.querySelectorAll("td[data-key]").forEach((td) => {
      const key = td.dataset.key;
      const input = td.querySelector("select, textarea");
      let value = input ? input.value : "";
      if (key === "acceptance_criteria") {
        value = value.split("\n").map((s) => s.trim()).filter(Boolean);
      }
      req[key] = value;
    });
    requirements.push(req);
  });

  return {
    project_overview: $("overview").value,
    requirements,
    open_issues: $("openIssues").value
      .split("\n").map((s) => s.trim()).filter(Boolean),
  };
}

async function generate() {
  const fileInput = $("fileInput");
  if (!fileInput.files.length) {
    setStatus("ファイルを選択してください。", true);
    return;
  }
  const form = new FormData();
  form.append("file", fileInput.files[0]);

  $("generateBtn").disabled = true;
  setStatus("生成中… (数十秒かかる場合があります)");

  try {
    const res = await fetch("/api/generate", { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const spec = await res.json();
    renderSpec(spec);
    setStatus(`生成完了: ${spec.requirements.length} 件の要件`);
  } catch (e) {
    setStatus("エラー: " + e.message, true);
  } finally {
    $("generateBtn").disabled = false;
  }
}

async function exportSpec(format) {
  const spec = collectSpec();
  try {
    const res = await fetch(`/api/export?format=${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(spec),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = format === "excel" ? "requirements.xlsx" : "requirements.md";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    setStatus("エクスポート失敗: " + e.message, true);
  }
}

$("generateBtn").onclick = generate;
$("addRowBtn").onclick = () => addRow();
$("exportMdBtn").onclick = () => exportSpec("markdown");
$("exportXlsxBtn").onclick = () => exportSpec("excel");
