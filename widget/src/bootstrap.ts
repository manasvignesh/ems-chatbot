import React from "react";
import ReactDOM from "react-dom/client";
import { ChatWidget } from "./ChatWidget";
import { WIDGET_STYLES } from "./styles";
import { pageContextManager } from "./context";
import { PageContext, WidgetInitOptions } from "./types";

let hostElement: HTMLElement | null = null;
let shadowRoot: ShadowRoot | null = null;
let reactRoot: ReactDOM.Root | null = null;

export function initWidget(options: WidgetInitOptions = {}) {
  // Prevent duplicate mounts
  if (hostElement) {
    console.warn("[EMS Assistant] Widget is already initialized.");
    return;
  }

  // Set initial context if provided
  if (options.initialContext) {
    pageContextManager.setContext(options.initialContext);
  }

  // Create host container
  hostElement = document.createElement("ems-assistant-root");
  hostElement.id = "ems-assistant-root";
  document.body.appendChild(hostElement);

  // Attach Shadow Root for complete CSS isolation
  shadowRoot = hostElement.attachShadow({ mode: "open" });

  // Inject Styles into Shadow Root
  const styleEl = document.createElement("style");
  styleEl.textContent = WIDGET_STYLES;
  shadowRoot.appendChild(styleEl);

  // Create mount point for React
  const mountPoint = document.createElement("div");
  mountPoint.id = "ems-widget-mount";
  shadowRoot.appendChild(mountPoint);

  // Render React widget
  reactRoot = ReactDOM.createRoot(mountPoint);
  reactRoot.render(React.createElement(ChatWidget, { options }));

  console.log("[EMS Assistant] Widget successfully initialized in Shadow DOM.");
}

export function openWidget() {
  window.dispatchEvent(new CustomEvent("ems-assistant:open"));
}

export function closeWidget() {
  window.dispatchEvent(new CustomEvent("ems-assistant:close"));
}

export function toggleWidget() {
  window.dispatchEvent(new CustomEvent("ems-assistant:toggle"));
}

export function sendMessage(text: string) {
  openWidget();
  window.dispatchEvent(new CustomEvent("ems-assistant:send-message", { detail: { text } }));
}

export function setPageContext(context: Partial<PageContext>) {
  pageContextManager.setContext(context);
}

export function resetConversation() {
  window.dispatchEvent(new CustomEvent("ems-assistant:reset"));
}

export function destroyWidget() {
  if (reactRoot) {
    reactRoot.unmount();
    reactRoot = null;
  }
  if (hostElement && hostElement.parentNode) {
    hostElement.parentNode.removeChild(hostElement);
    hostElement = null;
    shadowRoot = null;
  }
  console.log("[EMS Assistant] Widget destroyed.");
}
