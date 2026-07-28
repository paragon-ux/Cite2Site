// Cite2Site Chrome Extension — Background Service Worker
const NATIVE_HOST = "com.cite2site.cite";
const PROTOCOL_VERSION = "1.0";

// Action-label table for UI rendering
const ACTION_LABELS = {
  "cite":              "Cite with Cite2Site",
  "set_handle":        "Change handle",
  "note":              "Add note",
  "accept_current":    "Accept current evidence",
  "relocate":          "Relocate citation",
  "retract":           "Retract citation",
  "restore":           "Restore citation",
  "open":              "Open citation",
};

chrome.runtime.onInstalled.addListener(() => {
  console.log("Cite2Site: installed, creating context menu");
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "cite2site-cite",
      title: "Cite with Cite2Site",
      contexts: ["selection"],
    });
  });
});

// --- Centralized native-message sending ---
async function sendToNativeHost(payload) {
  console.log("Cite2Site: sending to native host", payload.action);
  try {
    const response = await chrome.runtime.sendNativeMessage(NATIVE_HOST, payload);
    console.log("Cite2Site: native response", response);
    await chrome.storage.local.set({ lastCitation: response });
    return response;
  } catch (error) {
    const message = error?.message || String(error);
    console.error("Cite2Site: native host error", message);
    // Only use E_EXTENSION_HOST for actual host-not-found errors
    const code = message.includes("not found") ? "E_EXTENSION_HOST" : "E_EXTENSION_ERROR";
    const response = { ok: false, protocol_version: PROTOCOL_VERSION, error: { code, message } };
    await chrome.storage.local.set({ lastCitation: response });
    return response;
  }
}

// --- Context menu: cite selection ---
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  console.log("Cite2Site: right-click", { hasSelection: Boolean(info.selectionText), url: tab?.url });
  if (info.menuItemId !== "cite2site-cite") return;

  const selectedText = info.selectionText;
  if (!selectedText) { console.warn("Cite2Site: no text selected"); return; }

  const encoded = new TextEncoder().encode(selectedText);
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  const contentHash = "sha256:" + Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, "0")).join("");

  await sendToNativeHost({
    action: "cite-selection",
    protocol_version: PROTOCOL_VERSION,
    artifact: tab?.url || "web-selection",
    sourceUrl: tab?.url || "", title: tab?.title || "",
    start: 0, end: selectedText.length,
    selectedText, contentHash,
  });
});

// --- Popup bridge: validate sender, route to native host ---
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Only accept messages from our own extension
  if (!sender || sender.id !== chrome.runtime.id) {
    sendResponse({ ok: false, protocol_version: PROTOCOL_VERSION, error: { code: "E_EXTENSION_FORBIDDEN", message: "Sender not authorized." } });
    return false;
  }
  if (!message?.payload || !message.payload.action) {
    sendResponse({ ok: false, protocol_version: PROTOCOL_VERSION, error: { code: "E_EXTENSION_INVALID", message: "Missing native-host payload." } });
    return false;
  }
  sendToNativeHost(message.payload).then(sendResponse);
  return true;
});
