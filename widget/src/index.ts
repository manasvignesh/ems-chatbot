import {
  initWidget,
  openWidget,
  closeWidget,
  toggleWidget,
  setPageContext,
  resetConversation,
  destroyWidget,
} from "./bootstrap";
import { WidgetInitOptions } from "./types";

// Public global object interface
export const EMSAssistant = {
  init: initWidget,
  open: openWidget,
  close: closeWidget,
  toggle: toggleWidget,
  setContext: setPageContext,
  resetConversation: resetConversation,
  destroy: destroyWidget,
};

// Attach to window object
if (typeof window !== "undefined") {
  (window as any).EMSAssistant = EMSAssistant;

  // Check for auto-init via script tag data attributes
  const currentScript = document.currentScript as HTMLScriptElement;
  if (currentScript) {
    const autoInit = currentScript.getAttribute("data-auto-init") !== "false";
    if (autoInit) {
      const apiUrl =
        currentScript.getAttribute("data-api-url") || "http://localhost:8000";
      const botId = currentScript.getAttribute("data-bot-id") || "ems";

      // Initialize once DOM is ready
      if (
        document.readyState === "complete" ||
        document.readyState === "interactive"
      ) {
        initWidget({ apiUrl, botId });
      } else {
        document.addEventListener("DOMContentLoaded", () => {
          initWidget({ apiUrl, botId });
        });
      }
    }
  }
}

export default EMSAssistant;
