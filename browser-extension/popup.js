const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const viewer = document.getElementById("viewer");
const content = document.getElementById("content");
const toolbar = document.getElementById("toolbar");
const citeBtn = document.getElementById("citeBtn");
const lookupBtn = document.getElementById("lookupBtn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const hint = document.getElementById("hint");

const INTEGRATION_SCHEMA = "c2s.integration.replacement.v1";
let currentFileName = null;
let currentFileContent = null;
let selectionStart = 0;
let selectionEnd = 0;

(async () => {
  const stored = await chrome.storage.local.get("lastCitation");
  const citation = stored.lastCitation;
  if (citation) {
    hint.style.display = "none";
    showResult(citation);
    await chrome.storage.local.remove("lastCitation");
    return;
  }
  dropZone.classList.remove("hidden");
})();

dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", event => {
  event.preventDefault();
  dropZone.style.borderColor = "#1976d2";
});
dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "";
});
dropZone.addEventListener("drop", event => {
  event.preventDefault();
  dropZone.style.borderColor = "";
  const file = event.dataTransfer.files[0];
  if (file) loadFile(file);
});
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) loadFile(file);
});

async function loadFile(file) {
  if (file.size > 10 * 1024 * 1024) {
    statusEl.textContent = "File too large (max 10 MB).";
    return;
  }
  let text;
  try {
    text = await file.text();
  } catch (_error) {
    statusEl.textContent = "Could not read file.";
    return;
  }
  currentFileName = file.name;
  currentFileContent = text;
  content.textContent = text;
  viewer.style.display = "block";
  toolbar.classList.add("visible");
  hint.style.display = "none";
  resultEl.className = "result";
  resultEl.style.display = "none";
  dropZone.classList.add("has-file");
  dropZone.querySelector("strong").textContent = file.name;
  dropZone.querySelector("small").textContent = "Selected: 0 chars";
  citeBtn.disabled = true;
  lookupBtn.disabled = false;
  statusEl.textContent = "";
}

document.addEventListener("selectionchange", () => {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount || selection.isCollapsed) {
    citeBtn.disabled = true;
    dropZone.querySelector("small").textContent = "Selected: 0 chars";
    return;
  }
  const range = selection.getRangeAt(0);
  if (!content.contains(range.commonAncestorContainer)) {
    citeBtn.disabled = true;
    return;
  }
  const preRange = document.createRange();
  preRange.setStart(content, 0);
  preRange.setEnd(range.startContainer, range.startOffset);
  selectionStart = preRange.toString().length;
  selectionEnd = selectionStart + range.toString().length;
  const length = selectionEnd - selectionStart;
  citeBtn.disabled = length <= 0;
  dropZone.querySelector("small").textContent = length > 0 ? `Selected: ${length} chars` : "Select text below";
  statusEl.textContent = length > 0 ? `${length} chars` : "";
});

citeBtn.addEventListener("click", async () => {
  if (!currentFileContent || selectionStart >= selectionEnd) return;
  const selectedText = currentFileContent.slice(selectionStart, selectionEnd);
  if (!selectedText) return;
  statusEl.textContent = "Citing...";
  const response = await chrome.runtime.sendMessage({
    payload: {
      schema_version: INTEGRATION_SCHEMA,
      action: "citation.create",
      repository: "",
      idempotency_key: crypto.randomUUID(),
      payload: {
        artifact: currentFileName,
        start: selectionStart,
        end: selectionEnd,
        selected_text: selectedText,
        handle_name: "Inbox"
      }
    }
  });
  showResult(response);
});

lookupBtn.addEventListener("click", async () => {
  if (!currentFileContent) return;
  statusEl.textContent = "Looking up...";
  const response = await chrome.runtime.sendMessage({
    payload: {
      schema_version: INTEGRATION_SCHEMA,
      action: "lookup-actions",
      repository: "",
      payload: {
        artifact: currentFileName,
        start: selectionStart || 0,
        end: selectionEnd || selectionStart || 0
      }
    }
  });
  showResult(response);
});

function showResult(resp) {
  resultEl.style.display = "block";
  if (resp && resp.ok) {
    resultEl.className = "result ok";
    resultEl.textContent = resp.citation_id
      ? `Cited: ${resp.citation_id.slice(0, 24)}...`
      : resp.matches
        ? `${resp.matches.length} citation(s) found`
        : "OK";
  } else {
    resultEl.className = "result err";
    const err = (resp && resp.error) || {};
    resultEl.textContent = `${err.code || "Error"}: ${err.message || "Unknown error"}`;
  }
  statusEl.textContent = "Done.";
}
