const PyloxApp = (function () {
  function executeCode(code) {
    if (!code || typeof code !== "string") {
      console.warn("code is invalid");
      return;
    }

    if (
      !code.trim() ||
      code.trim() === "// Enter Lox code here, or try the examples below"
    ) {
      const outputEl = document.getElementById("output");
      if (outputEl)
        outputEl.textContent = "Start typing Lox code to see results...";
      return;
    }

    const csrfTokenEl = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfTokenEl) {
      console.error("CSRF token not found");
      return;
    }

    const csrfToken = csrfTokenEl.value;

    fetch(window.executeUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrfToken,
        Accept: "text/vnd.turbo-stream.html, text/html",
      },
      body: `csrfmiddlewaretoken=${encodeURIComponent(
        csrfToken
      )}&code=${encodeURIComponent(code)}`,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.text();
      })
      .then((html) => {
        if (html.includes("<turbo-stream")) {
          Turbo.renderStreamMessage(html);
        } else {
          const outputEl = document.getElementById("output");
          if (outputEl) outputEl.innerHTML = html;
        }
      })
      .catch((error) => {
        const outputEl = document.getElementById("output");
        if (outputEl) outputEl.textContent = `Error: ${error.message}`;
      });
  }

  function switchTab(tabName) {
    if (!tabName || typeof tabName !== "string") {
      return;
    }

    const outputTab = document.getElementById("output-tab");
    const astTab = document.getElementById("ast-tab");
    const outputPanel = document.getElementById("output-panel");
    const astPanel = document.getElementById("ast-panel");

    if (!outputTab || !astTab || !outputPanel || !astPanel) {
      return;
    }

    // Switching just means changing visibility
    outputTab.classList.remove("tab-active");
    astTab.classList.remove("tab-active");

    outputPanel.style.display = "none";
    astPanel.style.display = "none";

    if (tabName === "output") {
      outputTab.classList.add("tab-active");
      outputPanel.style.display = "block";
    } else if (tabName === "ast") {
      astTab.classList.add("tab-active");
      astPanel.style.display = "block";
    } else {
      console.warn(`tab name not recognized '${tabName}'`);
    }
  }

  return {
    executeCode,
    switchTab,
  };
})();

window.executeCode = PyloxApp.executeCode;
window.switchTab = PyloxApp.switchTab;
