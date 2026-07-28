// Cite2Site Chrome Extension — Background Service Worker
const NATIVE_HOST = "com.cite2site.cite";

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
    const response = {
      ok: false,
      error: {
        code: "E_EXTENSION_HOST",
        message,
      },
    };
    await chrome.storage.local.set({ lastCitation: response });
    return response;
  }
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  console.log("Cite2Site: right-click", {
    hasSelection: Boolean(info.selectionText),
    url: tab?.url,
  });

  if (info.menuItemId !== "cite2site-cite") return;

  const selectedText = info.selectionText;
  if (!selectedText) {
    console.warn("Cite2Site: no text selected");
    return;
  }

  const encoded = new TextEncoder().encode(selectedText);
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  const contentHash =
    "sha256:" +
    Array.from(new Uint8Array(digest), (byte) =>
      byte.toString(16).padStart(2, "0")
    ).join("");

  await sendToNativeHost({
    action: "cite-selection",
    artifact: tab?.url || "web-selection",
    sourceUrl: tab?.url || "",
    title: tab?.title || "",
    start: 0,
    end: selectedText.length,
    selectedText,
    contentHash,
  });
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message?.payload) {
    sendResponse({
      ok: false,
      error: { code: "E_EXTENSION_INVALID", message: "Missing native-host payload." },
    });
    return false;
  }

  sendToNativeHost(message.payload).then(sendResponse);
  return true;
});
