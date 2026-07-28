// Cite2Site Chrome Extension — Popup UI
//
// Drag a file, view its content, select text, and cite it.

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const viewer = document.getElementById("viewer");
const content = document.getElementById("content");
const toolbar = document.getElementById("toolbar");
const citeBtn = document.getElementById("citeBtn");
const lookupBtn = document.getElementById("lookupBtn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

let currentFile = null;
let selectionStart = 0;
let selectionEnd = 0;

// --- File drop / click ---
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) loadFile(file);
});
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) loadFile(file);
});

async function loadFile(file) {
  currentFile = file;
  const text = await file.text();
  content.textContent = text;
  viewer.style.display = "block";
  toolbar.classList.add("visible");
  dropZone.classList.add("has-file");
  dropZone.querySelector("strong").textContent = file.name;
  dropZone.querySelector("small").textContent = `${text.length} chars — select text below, then cite`;
  citeBtn.disabled = true;
  lookupBtn.disabled = false;
  resultEl.className = "";
  resultEl.style.display = "none";
}

// --- Selection tracking ---
document.addEventListener("selectionchange", () => {
  const sel = window.getSelection();
  if (!sel.rangeCount || sel.isCollapsed) {
    citeBtn.disabled = true;
    statusEl.textContent = "";
    return;
  }
  // Get offsets relative to #content text node
  const range = sel.getRangeAt(0);
  if (!content.contains(range.commonAncestorContainer)) {
    citeBtn.disabled = true;
    return;
  }
  // Walk text nodes to compute offset
  const pre = range.startContainer === content
    ? range.startOffset
    : range.startContainer.parentElement === content
      ? range.startOffset
      : 0;
  const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
  let offset = 0;
  let foundStart = false;
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (node === range.startContainer || (!foundStart && node.parentElement === range.startContainer)) {
      selectionStart = offset + (range.startContainer === node ? range.startOffset : 0);
      foundStart = true;
    }
    if (node === range.endContainer || (foundStart && node.parentElement === range.endContainer)) {
      selectionEnd = offset + (range.endContainer === node ? range.endOffset : node.textContent.length);
      break;
    }
    offset += node.textContent.length;
  }
  if (!foundStart) { selectionStart = 0; selectionEnd = 0; }
  const selectedLength = selectionEnd - selectionStart;
  citeBtn.disabled = selectedLength <= 0;
  statusEl.textContent = selectedLength > 0 ? `Selected: ${selectedLength} chars` : "";
});

// --- Cite button ---
citeBtn.addEventListener("click", async () => {
  const selectedText = content.textContent.slice(selectionStart, selectionEnd);
  if (!selectedText) return;

  const encoder = new TextEncoder();
  const data = encoder.encode(selectedText);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const contentHash = "sha256:" + hashArray.map(b => b.toString(16).padStart(2, "0")).join("");

  const payload = {
    action: "cite-selection",
    artifact: currentFile.name,
    start: selectionStart,
    end: selectionEnd,
    selectedText: selectedText,
    contentHash: contentHash,
  };

  statusEl.textContent = "Citing...";
  const response = await chrome.runtime.sendMessage({ action: "cite-selection", payload });
  showResult(response);
});

// --- Lookup button ---
lookupBtn.addEventListener("click", async () => {
  const sel = window.getSelection();
  let pos = 0;
  if (sel && sel.rangeCount && !sel.isCollapsed) {
    pos = selectionStart;
  } else {
    // Use midpoint of viewer scroll position as approximate cursor
    pos = Math.floor(content.textContent.length / 2);
  }

  const payload = {
    action: "lookup-actions",
    artifact: currentFile.name,
    start: pos,
    end: pos,
  };

  statusEl.textContent = "Looking up...";
  const response = await chrome.runtime.sendMessage({ action: "lookup-actions", payload });
  showResult(response);
});

function showResult(resp) {
  resultEl.style.display = "block";
  if (resp && resp.ok) {
    resultEl.className = "ok";
    resultEl.textContent = `[OK] ${resp.citation_id ? 'Cited: ' + resp.citation_id.slice(0, 16) + '...' : ''} ${resp.matches ? resp.matches.length + ' citations found' : ''}`;
    statusEl.textContent = "Done.";
  } else {
    resultEl.className = "err";
    const err = (resp && resp.error) || {};
    resultEl.textContent = `[ERR] ${err.code || 'UNKNOWN'}: ${err.message || JSON.stringify(resp)}`;
    statusEl.textContent = "Failed.";
  }
}
