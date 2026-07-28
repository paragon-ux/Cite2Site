// Cite2Site Chrome Extension — Popup UI
//
// Two modes:
// 1. Drop a file → view content, select text, cite/lookup
// 2. After right-click → show last citation result

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

let currentFileName = null, currentFileContent = null;
let selectionStart = 0, selectionEnd = 0;

// --- Init: show either file drop UI or last right-click result ---
(async () => {
  const stored = await chrome.storage.local.get("lastCitation");
  const citation = stored.lastCitation;
  if (citation) {
    hint.style.display = "none";
    if (citation.ok) {
      resultEl.className = "result ok";
      resultEl.innerHTML = "";
      resultEl.appendChild(document.createTextNode("Citation created. "));
      const code = document.createElement("code");
      code.textContent = (citation.citation_id || "").slice(0, 20) + "...";
      resultEl.appendChild(document.createElement("br"));
      resultEl.appendChild(code);
    } else {
      resultEl.className = "result err";
      const err = citation.error || {};
      resultEl.textContent = `${err.code || "Error"}: ${err.message || "Unknown error"}`;
    }
    await chrome.storage.local.remove("lastCitation");
    return;
  }
  // Show file drop UI
  dropZone.classList.remove("hidden");
})();

// --- File drop / click ---
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.style.borderColor = "#1976d2"; });
dropZone.addEventListener("dragleave", () => { dropZone.style.borderColor = ""; });
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.style.borderColor = "";
  const file = e.dataTransfer.files[0];
  if (file) loadFile(file);
});
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) loadFile(file);
});

async function loadFile(file) {
  if (file.size > 10 * 1024 * 1024) { statusEl.textContent = "File too large (max 10 MB)."; return; }
  let text;
  try {
    text = await file.text();
  } catch (e) {
    statusEl.textContent = "Could not read file (binary or encoding error).";
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
  dropZone.querySelector("small").textContent = `Selected: 0 chars`;
  citeBtn.disabled = true;
  lookupBtn.disabled = false;
  statusEl.textContent = "";
}

// --- Selection tracking ---
document.addEventListener("selectionchange", () => {
  const sel = window.getSelection();
  if (!sel || !sel.rangeCount || sel.isCollapsed) {
    citeBtn.disabled = true;
    dropZone.querySelector("small").textContent = `Selected: 0 chars`;
    return;
  }
  const range = sel.getRangeAt(0);
  if (!content.contains(range.commonAncestorContainer)) {
    citeBtn.disabled = true;
    return;
  }
  // Compute character offsets from text content
  const fullText = content.textContent;
  const preRange = document.createRange();
  preRange.setStart(content, 0);
  preRange.setEnd(range.startContainer, range.startOffset);
  selectionStart = preRange.toString().length;
  selectionEnd = selectionStart + range.toString().length;
  const len = selectionEnd - selectionStart;
  citeBtn.disabled = len <= 0;
  dropZone.querySelector("small").textContent = len > 0 ? `Selected: ${len} chars` : "Select text below";
  statusEl.textContent = len > 0 ? `${len} chars` : "";
});

// --- Cite button ---
citeBtn.addEventListener("click", async () => {
  if (!currentFileContent || selectionStart >= selectionEnd) return;
  const selectedText = currentFileContent.slice(selectionStart, selectionEnd);
  if (!selectedText) return;

  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(selectedText));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const contentHash = "sha256:" + hashArray.map(b => b.toString(16).padStart(2, "0")).join("");

  statusEl.textContent = "Citing...";
  const response = await chrome.runtime.sendMessage({
    action: "cite-file-selection",
    payload: {
      action: "cite-file-selection",
      file: { name: currentFileName, content: currentFileContent },
      selection: { start: selectionStart, end: selectionEnd, selectedText, contentHash }
    }
  });
  showResult(response);
});

// --- Lookup button ---
lookupBtn.addEventListener("click", async () => {
  if (!currentFileContent) return;
  const pos = selectionStart || 0;
  statusEl.textContent = "Looking up...";
  const response = await chrome.runtime.sendMessage({
    action: "lookup-actions",
    payload: {
      action: "lookup-file-selection",
      file: { name: currentFileName, content: currentFileContent },
      start: pos, end: pos
    }
  });
  showResult(response);
});

function showResult(resp) {
  resultEl.style.display = "block";
  if (resp && resp.ok) {
    resultEl.className = "result ok";
    resultEl.textContent = resp.citation_id
      ? `Cited: ${resp.citation_id.slice(0, 20)}...`
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
