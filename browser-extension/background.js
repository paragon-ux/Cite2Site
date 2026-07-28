// Cite2Site Chrome Extension — Background Service Worker
//
// Two paths to cite:
// 1. Right-click selected text on any webpage → "Cite with Cite2Site"
// 2. Drag a file into the popup, select text, click "Cite selection"
//
// Both go through the native messaging host to the c2s CLI.

const NATIVE_HOST = "com.cite2site.cite";

// --- Context Menu (right-click to cite) ---
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "cite2site-cite",
    title: "Cite with Cite2Site",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "cite2site-cite") return;
  const selectedText = info.selectionText;
  if (!selectedText) return;

  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(selectedText));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const contentHash = "sha256:" + hashArray.map(b => b.toString(16).padStart(2, "0")).join("");

  try {
    const response = await chrome.runtime.sendNativeMessage(NATIVE_HOST, {
      action: "cite-selection",
      artifact: tab?.url || "web-selection",
      start: 0,
      end: selectedText.length,
      selectedText,
      contentHash,
      title: tab?.title || "",
      sourceUrl: tab?.url || "",
    });
    await chrome.storage.local.set({ lastCitation: response });
  } catch (err) {
    await chrome.storage.local.set({
      lastCitation: { ok: false, error: { code: "E_EXTENSION_HOST", message: "Cite2Site not found. Run: c2s install-native-host" } }
    });
  }
});

// --- Popup bridge (file drag-and-drop path) ---
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  chrome.runtime.sendNativeMessage(NATIVE_HOST, message.payload)
    .then(sendResponse)
    .catch(err => sendResponse({
      ok: false,
      error: { code: "E_EXTENSION_HOST", message: "Cite2Site not found. Run: c2s install-native-host" }
    }));
  return true; // async
});
