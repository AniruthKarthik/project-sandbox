// ==UserScript==
// @name         Scopus Batch PDF Downloader - Fixed
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  Automates batch PDF downloads from Scopus with correct button sequence and React-compatible input setting
// @author       Assistant
// @match        https://www.scopus.com/*
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  // Configuration
  const BATCH_SIZE = 40;
  const DELAY_BETWEEN_ACTIONS = 2000; // 2 seconds
  const MAX_WAIT_TIME = 10000; // 10 seconds max wait for elements
  const ELEMENT_CHECK_INTERVAL = 500; // Check every 500ms

  // State management
  let isRunning = false;
  let currentFrom = 1;
  let totalResults = 0;
  let processedBatches = 0;

  // Logging utility
  function log(message, type = "info") {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `[Scopus Downloader ${timestamp}]`;

    switch (type) {
      case "error":
        console.error(`${prefix} ❌ ${message}`);
        break;
      case "success":
        console.log(`${prefix} ✅ ${message}`);
        break;
      case "warning":
        console.warn(`${prefix} ⚠️ ${message}`);
        break;
      default:
        console.log(`${prefix} ℹ️ ${message}`);
    }
  }

  // Wait for element to appear with timeout
  function waitForElement(selector, timeout = MAX_WAIT_TIME) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();

      function checkElement() {
        const element = document.querySelector(selector);
        if (element && element.offsetParent !== null) {
          resolve(element);
          return;
        }

        if (Date.now() - startTime > timeout) {
          reject(
            new Error(`Element ${selector} not found within ${timeout}ms`),
          );
          return;
        }

        setTimeout(checkElement, ELEMENT_CHECK_INTERVAL);
      }

      checkElement();
    });
  }

  // Delay utility
  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Parse total results from page
  function getTotalResults() {
    const selectors = [
      '[data-testid="results-count"]',
      ".results-count",
      '[class*="result"][class*="count"]',
      ".searchResults .resultsCount",
      ".resultsHeader .count",
      ".document-search-results-page h1",
      ".search-results-count",
      "#resultsCount",
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        const text = element.textContent || element.innerText;
        const match = text.match(/[\d,]+/);
        if (match) {
          const count = parseInt(match[0].replace(/,/g, ""));
          if (count > 0) {
            log(`Found total results: ${count} (selector: ${selector})`);
            return count;
          }
        }
      }
    }

    // Search for elements containing "results" text
    const allElements = document.querySelectorAll(
      "span, div, h1, h2, p, .count, .total",
    );
    for (const element of allElements) {
      const text = (
        element.textContent ||
        element.innerText ||
        ""
      ).toLowerCase();
      if (text.includes("result") && !text.includes("per page")) {
        const match = text.match(/[\d,]+/);
        if (match) {
          const count = parseInt(match[0].replace(/,/g, ""));
          if (count > 10) {
            log(
              `Found total results by text search: ${count} in "${text.trim()}"`,
            );
            return count;
          }
        }
      }
    }

    log(
      "⚠️ Could not find total results count - using default of 100",
      "warning",
    );
    return 100; // Safe default
  }

  // Find download button
  function findDownloadButton() {
    const selectors = [
      '[data-testid="download-button"]',
      'button[title*="Download"]',
      'button[aria-label*="Download"]',
      ".download-btn",
      '[class*="download"][class*="button"]',
      'button[data-action="download"]',
      '[data-testid*="download"]',
      "#downloadBtn",
      ".btn-download",
    ];

    for (const selector of selectors) {
      try {
        const element = document.querySelector(selector);
        if (element && element.offsetParent !== null) {
          log(`Found download button with selector: ${selector}`);
          return element;
        }
      } catch (e) {
        continue;
      }
    }

    // Text-based search as fallback
    const buttons = document.querySelectorAll(
      'button, a, [role="button"], input[type="button"]',
    );
    for (const button of buttons) {
      const text = (
        button.textContent ||
        button.innerText ||
        button.value ||
        ""
      )
        .toLowerCase()
        .trim();
      const title = (button.title || "").toLowerCase();
      const ariaLabel = (button.getAttribute("aria-label") || "").toLowerCase();

      if (
        text.includes("download") ||
        text.includes("export") ||
        title.includes("download") ||
        ariaLabel.includes("download")
      ) {
        log(`Found download button by text content: "${text}"`);
        return button;
      }
    }

    return null;
  }

  // Find results radio button
  function findResultsRadioButton() {
    // Use the exact selector you provided
    const exactSelector =
      "#container > micro-ui > document-search-results-page > div.micro-ui-namespace.DocumentSearchResultsPage-module__S9XTT > section:nth-child(2) > div > div.Col-module__hwM1N.PageLayout-module__j0MIQ > div > div:nth-child(3) > div > div:nth-child(1) > div.make-selection-modal > div > div > div > section > div.Modal-module__iyz7c > div > div > div > label > span";

    try {
      const spanElement = document.querySelector(exactSelector);
      if (spanElement) {
        // The span is inside a label, find the actual radio input
        const label = spanElement.closest("label");
        if (label) {
          // Look for radio input inside the label or associated with it
          const radioInput =
            label.querySelector('input[type="radio"]') ||
            document.querySelector(
              `input[type="radio"][id="${label.getAttribute("for")}"]`,
            );
          if (radioInput) {
            log(`✅ Found Results radio button with exact selector (via span)`);
            return radioInput;
          }
        }
      }
    } catch (e) {
      log(`Exact selector failed: ${e.message}`, "warning");
    }

    // Primary selector for Scopus "Results" radio button (original)
    const primarySelector = "#Download\\ documents-selectRange";

    try {
      const element = document.querySelector(primarySelector);
      if (element) {
        log(`Found Results radio button with primary selector`);
        return element;
      }
    } catch (e) {
      log(`Primary selector failed: ${e.message}`, "warning");
    }

    // Fallback selectors
    const fallbackSelectors = [
      'input[value="range"]',
      'input[type="radio"][id*="selectRange"]',
      'input[type="radio"][name*="download"]',
      'input[type="radio"][value*="results"]',
      'input[type="radio"][value*="range"]',
    ];

    for (const selector of fallbackSelectors) {
      try {
        const element = document.querySelector(selector);
        if (element) {
          log(`Found Results radio button with fallback selector: ${selector}`);
          return element;
        }
      } catch (e) {
        continue;
      }
    }

    return null;
  }

  // Find from/to input fields
  function findRangeInputs() {
    const fromSelectors = [
      'input[name*="from"]',
      'input[placeholder*="From"]',
      'input[id*="from"]',
      '[data-testid*="from-input"]',
      ".range-from input",
      'input[type="number"]:first-of-type',
    ];

    const toSelectors = [
      'input[name*="to"]',
      'input[placeholder*="To"]',
      'input[id*="to"]',
      '[data-testid*="to-input"]',
      ".range-to input",
      'input[type="number"]:last-of-type',
    ];

    let fromInput = null;
    let toInput = null;

    // Find From input
    for (const selector of fromSelectors) {
      fromInput = document.querySelector(selector);
      if (fromInput) break;
    }

    // Find To input
    for (const selector of toSelectors) {
      toInput = document.querySelector(selector);
      if (toInput) break;
    }

    // Fallback: look for number inputs in modal/dialog
    if (!fromInput || !toInput) {
      const modal = document.querySelector(
        '.modal, .dialog, [role="dialog"], [class*="Modal"]',
      );
      if (modal) {
        const numberInputs = modal.querySelectorAll(
          'input[type="number"], input[type="text"]',
        );
        if (numberInputs.length >= 2) {
          fromInput = numberInputs[0];
          toInput = numberInputs[1];
          log("Found range inputs in modal as fallback");
        }
      }
    }

    return { fromInput, toInput };
  }

  // Find first download button (the one that appears after filling range)
  function findFirstDownloadButton() {
    const selectors = [
      '[data-testid="confirm-download"]',
      'button[type="submit"]',
      ".confirm-btn",
      ".download-confirm",
      '.modal button[class*="primary"]',
      '.dialog button[class*="confirm"]',
      '[data-testid*="confirm"]',
      '[data-testid*="submit"]',
      ".btn-primary",
      ".primary-button",
    ];

    for (const selector of selectors) {
      try {
        const element = document.querySelector(selector);
        if (element && element.offsetParent !== null && !element.disabled) {
          log(`Found first download button with selector: ${selector}`);
          return element;
        }
      } catch (e) {
        continue;
      }
    }

    // Look in modals for any button
    const modals = document.querySelectorAll(
      '.modal, .dialog, [role="dialog"], [class*="Modal"]',
    );
    for (const modal of modals) {
      if (modal.offsetParent !== null) {
        const buttons = modal.querySelectorAll("button:not([disabled])");
        for (const button of buttons) {
          const text = (button.textContent || "").toLowerCase().trim();
          if (
            text.includes("download") ||
            text.includes("confirm") ||
            text.includes("export")
          ) {
            log(`Found first download button by text in modal: "${text}"`);
            return button;
          }
        }
        // If no text match, use first enabled button
        if (buttons.length > 0) {
          log(
            `Using first available button in modal: "${buttons[0].textContent?.trim()}"`,
          );
          return buttons[0];
        }
      }
    }

    return null;
  }

  // Find second download button (the final one)
  function findSecondDownloadButton() {
    // The exact Scopus selector you provided
    const exactScopusSelector =
      "#container > micro-ui > document-search-results-page > div.micro-ui-namespace.DocumentSearchResultsPage-module__S9XTT > section:nth-child(2) > div > div.Col-module__hwM1N.PageLayout-module__j0MIQ > div > div:nth-child(3) > div > div:nth-child(1) > div.Modal-module__HdKbm > div > div > section > div > div > div > button.Button-module__nc6_8.Button-module__rphhF.Button-module__VBKvn.Button-module__R359q.Button-module__hK_LA.Button-module__x5a4w.Button-module__rTQlw";

    try {
      const exactButton = document.querySelector(exactScopusSelector);
      if (
        exactButton &&
        exactButton.offsetParent !== null &&
        !exactButton.disabled
      ) {
        log(`✅ Found EXACT Scopus second download button`);
        return exactButton;
      }
    } catch (e) {
      log(`⚠️ Exact selector failed: ${e.message}`, "warning");
    }

    // Look for Scopus modal and find buttons with those specific classes
    const scopusModal = document.querySelector(".Modal-module__HdKbm");
    if (scopusModal && scopusModal.offsetParent !== null) {
      const specificButton = scopusModal.querySelector(
        "button.Button-module__nc6_8.Button-module__rphhF.Button-module__VBKvn.Button-module__R359q.Button-module__hK_LA.Button-module__x5a4w.Button-module__rTQlw",
      );
      if (
        specificButton &&
        specificButton.offsetParent !== null &&
        !specificButton.disabled
      ) {
        log(`✅ Found Scopus second download button with specific classes`);
        return specificButton;
      }

      // Try any button with partial matching classes
      const partialButtons = scopusModal.querySelectorAll(
        'button[class*="Button-module__nc6_8"], button[class*="Button-module__rphhF"]',
      );
      for (const button of partialButtons) {
        if (button.offsetParent !== null && !button.disabled) {
          log(`✅ Found second download button with partial classes`);
          return button;
        }
      }
    }

    // Fallback: look for any download/confirm button in visible modals
    const modals = document.querySelectorAll(
      '.modal, .dialog, [role="dialog"], [class*="Modal"]',
    );
    for (const modal of modals) {
      if (modal.offsetParent !== null) {
        const buttons = modal.querySelectorAll("button:not([disabled])");
        for (const button of buttons) {
          const text = (button.textContent || "").toLowerCase().trim();
          if (
            text.includes("download") ||
            text.includes("confirm") ||
            text.includes("export")
          ) {
            log(`Found second download button by text: "${text}"`);
            return button;
          }
        }
      }
    }

    return null;
  }

  // Helper to set value in React-controlled inputs
  function setReactInputValue(inputElement, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      "value"
    ).set;
    nativeInputValueSetter.call(inputElement, value.toString());

    inputElement.dispatchEvent(new Event("input", { bubbles: true }));
    inputElement.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // Process a single batch with the EXACT sequence you specified
  async function processBatch(from, to) {
    try {
      log(`🔄 Processing batch ${from}-${to}`);

      // STEP 1: Click download button ONCE
      log("📥 STEP 1: Clicking download button ONCE...");
      const downloadBtn = findDownloadButton();
      if (!downloadBtn) {
        throw new Error("Download button not found");
      }
      downloadBtn.click();
      await delay(DELAY_BETWEEN_ACTIONS);

      // STEP 2: Click result radio button ONCE with enhanced event triggering
      log(
        '🔘 STEP 2: Clicking "Results" radio button ONCE with enhanced events...',
      );
      const resultsRadio = findResultsRadioButton();
      if (!resultsRadio) {
        throw new Error("Results radio button not found");
      }

      // Focus the radio button first
      resultsRadio.focus();
      await delay(200);

      // Set checked state and trigger events
      resultsRadio.checked = true;
      resultsRadio.click();
      resultsRadio.dispatchEvent(new Event("change", { bubbles: true }));
      resultsRadio.dispatchEvent(new Event("input", { bubbles: true }));

      // Also try triggering on the parent label if it exists
      const parentLabel = resultsRadio.closest("label");
      if (parentLabel) {
        parentLabel.click();
      }

      await delay(1500); // Longer wait for inputs to become enabled and form validation to complete

      // STEP 3: Fill in From and To numbers using React-compatible setter
      log(
        `📝 STEP 3: Filling in From: ${from} and To: ${to} with React-compatible setter...`,
      );
      const { fromInput, toInput } = findRangeInputs();

      if (!fromInput || !toInput) {
        throw new Error("Could not find From/To input fields");
      }

      log(`Found inputs - From: ${fromInput.tagName}, To: ${toInput.tagName}`);

      // Fill From input
      fromInput.focus();
      await delay(200);
      setReactInputValue(fromInput, from);
      fromInput.blur();
      await delay(800);

      // Fill To input
      toInput.focus();
      await delay(200);
      setReactInputValue(toInput, to);
      toInput.blur();
      await delay(800);

      // Additional validation trigger - click outside the inputs to ensure blur
      document.body.click();
      await delay(500);

      log(`✅ Range filled and validated: ${from} to ${to}`);
      log(
        `📋 From input value: "${fromInput.value}", To input value: "${toInput.value}"`,
      );

      // Force form validation by triggering form-level events
      const form = fromInput.closest("form");
      if (form) {
        log("📋 Triggering form validation events...");
        form.dispatchEvent(new Event("change", { bubbles: true }));
        form.dispatchEvent(new Event("input", { bubbles: true }));
        await delay(500);
      }

      // STEP 4: Press the first download button TWICE
      log("🔄 STEP 4: Pressing first download button TWICE...");

      const firstDownloadBtn = findFirstDownloadButton();
      if (!firstDownloadBtn) {
        throw new Error("First download button not found");
      }

      // First click
      log("🔥 First click on first download button...");
      firstDownloadBtn.click();
      await delay(1000);

      // Second click
      log("🔥 Second click on first download button...");
      firstDownloadBtn.click();
      await delay(DELAY_BETWEEN_ACTIONS);

      // STEP 5: Press the second download button ONCE
      log("🎯 STEP 5: Looking for second download button...");

      let secondDownloadBtn = null;
      let attempts = 0;
      const maxAttempts = 10;

      // Wait for second download button to appear
      while (!secondDownloadBtn && attempts < maxAttempts) {
        await delay(800);
        attempts++;
        log(
          `🔍 Attempt ${attempts}/${maxAttempts}: Searching for second download button...`,
        );

        secondDownloadBtn = findSecondDownloadButton();

        if (secondDownloadBtn) {
          log(`✅ Found second download button on attempt ${attempts}`);
          break;
        }
      }

      if (!secondDownloadBtn) {
        throw new Error("Second download button not found after all attempts");
      }

      // Click second download button ONCE
      log("🚀 Pressing second download button ONCE...");
      secondDownloadBtn.click();
      await delay(DELAY_BETWEEN_ACTIONS);

      log(
        `✨ Batch ${from}-${to} completed! PDFs should start downloading now.`,
        "success",
      );
      log("💾 Please confirm each PDF save dialog when prompted.", "warning");

      return true;
    } catch (error) {
      log(`❌ Error processing batch ${from}-${to}: ${error.message}`, "error");

      // Try to close any open dialogs on error
      const closeButtons = document.querySelectorAll(
        '.modal .close, .dialog .close, [aria-label="Close"], .close-btn',
      );
      for (const closeBtn of closeButtons) {
        if (closeBtn && closeBtn.offsetParent !== null) {
          closeBtn.click();
          break;
        }
      }

      return false;
    }
  }

  // Main automation function
  async function runBatchDownload() {
    if (isRunning) {
      log("Script is already running!", "warning");
      return;
    }

    isRunning = true;
    log("🚀 Starting batch download automation with fixed sequence...");

    try {
      // Get total results
      totalResults = getTotalResults();
      if (totalResults === 0) {
        await delay(2000);
        totalResults = getTotalResults();
        if (totalResults === 0) {
          throw new Error("Could not determine total results count");
        }
      }

      log(`📊 Total results: ${totalResults}`);
      log(`📦 Batch size: ${BATCH_SIZE}`);

      const totalBatches = Math.ceil(totalResults / BATCH_SIZE);
      log(`🎯 Total batches to process: ${totalBatches}`);

      // Reset state
      currentFrom = 1;
      processedBatches = 0;

      // Process each batch
      for (
        let batchNum = 1;
        batchNum <= totalBatches && isRunning;
        batchNum++
      ) {
        const currentTo = Math.min(currentFrom + BATCH_SIZE - 1, totalResults);

        log(`\n📄 === BATCH ${batchNum}/${totalBatches} ===`);
        log(`📄 Processing papers ${currentFrom} to ${currentTo}`);

        const success = await processBatch(currentFrom, currentTo);

        if (!success) {
          log("❌ Batch failed. Stopping automation.", "error");
          break;
        }

        processedBatches++;
        currentFrom = currentTo + 1;

        // Progress reporting
        const progress = Math.round((currentTo / totalResults) * 100);
        log(
          `📈 Progress: ${progress}% (${currentTo}/${totalResults} papers processed)`,
          "success",
        );

        // Wait before next batch (allow time for file saves)
        if (currentFrom <= totalResults && isRunning) {
          const waitTime = DELAY_BETWEEN_ACTIONS * 4; // Extra time for manual saves
          log(`⏱️ Waiting ${waitTime / 1000} seconds before next batch...`);
          log(`💡 TIP: Save all PDFs from this batch during this wait time`);
          await delay(waitTime);
        }
      }

      if (isRunning) {
        log(`\n🎉 AUTOMATION COMPLETE! 🎉`, "success");
        log(`📊 Successfully processed ${processedBatches} batches`, "success");
        log(
          `📄 Total papers: ${Math.min(currentFrom - 1, totalResults)}`,
          "success",
        );
        log(`💾 Don't forget to save any remaining PDF dialogs!`, "warning");
      } else {
        log(
          `ℹ️ Automation stopped by user after ${processedBatches} batches`,
          "warning",
        );
      }
    } catch (error) {
      log(`💥 Automation failed: ${error.message}`, "error");
      log("🔧 Try refreshing the page and running again", "warning");
    } finally {
      isRunning = false;
    }
  }

  // Create control panel
  function createControlPanel() {
    if (document.getElementById("scopus-downloader-panel")) {
      return;
    }

    const panel = document.createElement("div");
    panel.id = "scopus-downloader-panel";
    panel.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            min-width: 280px;
        `;

    panel.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 10px;">📄 Scopus Batch Downloader - Fixed</div>
            <div style="font-size: 12px; margin-bottom: 10px; background: #34495e; padding: 8px; border-radius: 4px;">
                <strong>Sequence:</strong><br>
                1️⃣ Click download once<br>
                2️⃣ Click results radio once<br>
                3️⃣ Fill from/to numbers<br>
                4️⃣ Press first download twice<br>
                5️⃣ Press second download once
            </div>
            <div id="status" style="margin-bottom: 10px; font-size: 12px;">Ready</div>
            <button id="startBtn" style="
                background: #27ae60;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                margin-bottom: 5px;
            ">Start Batch Download</button>
            <button id="stopBtn" style="
                background: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                margin-bottom: 10px;
            " disabled>Stop</button>
            <div style="font-size: 11px; color: #bdc3c7;">
                ⚠️ You'll need to manually save each PDF dialog that appears.
            </div>
        `;

    document.body.appendChild(panel);

    // Event listeners
    const startBtn = panel.querySelector("#startBtn");
    const stopBtn = panel.querySelector("#stopBtn");
    const statusDiv = panel.querySelector("#status");

    startBtn.addEventListener("click", () => {
      startBtn.disabled = true;
      stopBtn.disabled = false;
      statusDiv.textContent = "Running fixed sequence...";
      runBatchDownload().finally(() => {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusDiv.textContent = "Ready";
      });
    });

    stopBtn.addEventListener("click", () => {
      isRunning = false;
      startBtn.disabled = false;
      stopBtn.disabled = true;
      statusDiv.textContent = "Stopped";
      log("Download automation stopped by user", "warning");
    });

    // Update status periodically
    setInterval(() => {
      if (isRunning) {
        const progress =
          totalResults > 0
            ? Math.round(((currentFrom - 1) / totalResults) * 100)
            : 0;
        statusDiv.textContent = `Running... ${progress}% (Batch ${processedBatches + 1})`;
      }
    }, 1000);

    log("Control panel created with fixed sequence");
  }

  // Initialize script
  function initialize() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", initialize);
      return;
    }

    setTimeout(() => {
      createControlPanel();
      log("🎮 Scopus Batch Downloader (Fixed) initialized");
      log("📋 The script will now follow the exact sequence:");
      log("   1️⃣ Click download button once");
      log("   2️⃣ Click result radio button once");
      log("   3️⃣ Fill from and to numbers");
      log("   4️⃣ Press first download button twice");
      log("   5️⃣ Press second download button once");
      log('🚀 Click "Start Batch Download" to begin');
    }, 2000);
  }

  // Keyboard shortcut (Ctrl+Shift+D)
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === "D") {
      e.preventDefault();
      if (!isRunning) {
        runBatchDownload();
      } else {
        isRunning = false;
        log("ℹ️ Stopped via keyboard shortcut", "warning");
      }
    }
  });

  // Start initialization
  initialize();
})();