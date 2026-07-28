// Cite2Site Chrome Extension — Background Service Worker
const NATIVE_HOST = "com.cite2site.cite";

// --- Context Menu ---
chrome.runtime.onInstalled.addListener(() => {
  console.log("Cite2Site: installed, creating context menu");
  chrome.contextMenus.create({
    id: "cite2site-cite",
    title: "Cite with Cite2Site",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  console.log("Cite2Site: right-click", { hasSelection: !!info.selectionText, url: tab?.url });
  if (info.menuItemId !== "cite2site-cite") return;

  const selectedText = info.selectionText;
  if (!selectedText) { console.log("Cite2Site: no text selected"); return; }
  console.log("Cite2Site: selected", selectedText.length, "chars");

  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(selectedText));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const contentHash = "sha256:" + hashArray.map(b => b.toString(16).padStart(2, "0")).join("");

  const message = {
    action: "cite-selection",
    artifact: tab?.url || "web-selection",
    start: 0, end: selectedText.length,
    selectedText, contentHash,
    title: tab?.title || "", sourceUrl: tab?.url || "",
  };
  console.log("Cite2Site: sending to native host...");

  try {
    const response = await chrome.runtime.sendNativeMessage(NATIVE_HOST, message);
    console.log("Cite2Site: response", response);
    await chrome.storage.local.set({ lastCitation: response });
  } catch (err) {
    console.error("Cite2Site: host error", err.message || err);
    await chrome.storage.local.set({
      lastCitation: { ok: false, error: { code: "E_EXTENSION_HOST", message: "Cite2Site not found." } }
    });
  }
});

// --- Popup bridge ---
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  console.log("Cite2Site: popup message", message.action);
  chrome.runtime.sendNativeMessage(NATIVE_HOST, message.payload)
    .then(response => { console.log("Cite2Site: popup response", response); sendResponse(response); })
    .catch(err => { console.error("Cite2Site: popup error", err.message); sendResponse({
      ok: false, error: { code: "E_EXTENSION_HOST", message: "Cite2Site not found." }
    }); });
  return true;
});
