const backendStatusEl = document.getElementById("backend-status");
const backendUrl = "https://tradingtool-2.onrender.com";

async function updateBackendStatus() {
  if (!backendStatusEl) {
    return;
  }

  backendStatusEl.textContent = "Checking...";
  backendStatusEl.className = "status-pill status-checking";

  try {
    const response = await fetch(backendUrl, {
      method: "GET",
      mode: "cors",
      cache: "no-store",
    });

    if (response.ok) {
      backendStatusEl.textContent = "Reachable";
      backendStatusEl.className = "status-pill status-up";
      return;
    }

    backendStatusEl.textContent = `HTTP ${response.status}`;
    backendStatusEl.className = "status-pill status-down";
  } catch (_corsError) {
    try {
      await fetch(backendUrl, {
        method: "GET",
        mode: "no-cors",
        cache: "no-store",
      });
      backendStatusEl.textContent = "Reachable";
      backendStatusEl.className = "status-pill status-up";
    } catch (_networkError) {
      backendStatusEl.textContent = "Unreachable";
      backendStatusEl.className = "status-pill status-down";
    }
  }
}

async function copyCommand(targetId, buttonEl) {
  const source = document.getElementById(targetId);
  if (!source || !buttonEl) {
    return;
  }

  const original = buttonEl.textContent;
  const command = source.textContent?.trim();
  if (!command) {
    return;
  }

  try {
    await navigator.clipboard.writeText(command);
    buttonEl.textContent = "Copied";
  } catch (_error) {
    buttonEl.textContent = "Copy failed";
  }

  window.setTimeout(() => {
    buttonEl.textContent = original;
  }, 1200);
}

function bindCopyButtons() {
  const buttons = document.querySelectorAll(".copy-btn");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.getAttribute("data-copy-target");
      if (!target) {
        return;
      }
      copyCommand(target, button);
    });
  });
}

bindCopyButtons();
updateBackendStatus();
window.setInterval(updateBackendStatus, 45000);
