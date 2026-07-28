const NATIVE_HOST = "com.cite2site.cite";
const INTEGRATION_SCHEMA = "c2s.integration.replacement.v1";

async function sendToNativeHost(payload) {
  try {
    const response = await chrome.runtime.sendNativeMessage(NATIVE_HOST, payload);
    await chrome.storage.local.set({ lastCitation: response });
    return response;
  } catch (error) {
    const message = error?.message || String(error);
    const code = message.includes("not found") ? "E_EXTENSION_HOST" : "E_EXTENSION_ERROR";
    const response = { ok: false, error: { code, message } };
    await chrome.storage.local.set({ lastCitation: response });
    return response;
  }
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "cite2site-cite",
      title: "Cite with Cite2Site",
      contexts: ["selection"],
    });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "cite2site-cite") return;
  const selectedText = info.selectionText || "";
  if (!selectedText) return;
  await sendToNativeHost({
    schema_version: INTEGRATION_SCHEMA,
    action: "citation.create",
    repository: "",
    idempotency_key: crypto.randomUUID(),
    payload: {
      artifact: tab?.url || "web-selection",
      start: 0,
      end: selectedText.length,
      selected_text: selectedText,
      source_title: tab?.title || "",
      handle_name: "Inbox",
    },
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!sender || sender.id !== chrome.runtime.id) {
    sendResponse({ ok: false, error: { code: "E_EXTENSION_FORBIDDEN", message: "Sender not authorized." } });
    return false;
  }
  if (!message?.payload || !message.payload.action) {
    sendResponse({ ok: false, error: { code: "E_EXTENSION_INVALID", message: "Missing native-host payload." } });
    return false;
  }
  sendToNativeHost(message.payload).then(sendResponse);
  return true;
});
