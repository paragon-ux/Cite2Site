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
    el.textContent = "Citation created.";
    // Show the citation ID truncated
    if (citation.citation_id) {
      el.innerHTML = `Citation created.<br><code>${citation.citation_id.slice(0, 20)}...</code>`;
    }
  } else {
    el.className = "result err";
    const err = citation.error || {};
    el.textContent = `${err.code || "Error"}: ${err.message || "Unknown error"}`;
  }

  // Clear after showing
  await chrome.storage.local.remove("lastCitation");
})();
