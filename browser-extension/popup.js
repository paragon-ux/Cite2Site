// Show the last citation result when popup opens
(async () => {
  const el = document.getElementById("result");
  const stored = await chrome.storage.local.get("lastCitation");
  const citation = stored.lastCitation;

  if (!citation) {
    return; // keep default message
  }

  if (citation.ok) {
    el.className = "result ok";
    if (citation.citation_id) {
      el.innerHTML = "";
      el.appendChild(document.createTextNode("Citation created. "));
      const code = document.createElement("code");
      code.textContent = citation.citation_id.slice(0, 20) + "...";
      el.appendChild(document.createElement("br"));
      el.appendChild(code);
    } else {
      el.textContent = "Citation created.";
    }
  } else {
    el.className = "result err";
    const err = citation.error || {};
    el.textContent = `${err.code || "Error"}: ${err.message || "Unknown error"}`;
  }

  // Clear after showing
  await chrome.storage.local.remove("lastCitation");
})();
