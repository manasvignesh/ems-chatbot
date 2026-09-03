export const WIDGET_STYLES = `
:host {
  --ems-primary: #4f46e5;
  --ems-primary-hover: #4338ca;
  --ems-primary-light: #eef2ff;
  --ems-primary-border: #c7d2fe;
  --ems-bg: #0f172a;
  --ems-card-bg: #1e293b;
  --ems-border: #334155;
  --ems-text: #f8fafc;
  --ems-text-muted: #94a3b8;
  --ems-user-bubble: #4f46e5;
  --ems-user-text: #ffffff;
  --ems-bot-bubble: #1e293b;
  --ems-bot-text: #f8fafc;
  --ems-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  --ems-radius: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--ems-text);
  box-sizing: border-box;
  display: block;
  position: fixed;
  bottom: 0;
  right: 0;
  z-index: 9999999;
  pointer-events: none;
}

*, *::before, *::after {
  box-sizing: inherit;
  margin: 0;
  padding: 0;
}

.ems-widget-root {
  pointer-events: auto;
}

.ems-launcher,
.ems-launcher-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999999;
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 9999px;
  box-shadow: 0 10px 25px -3px rgba(79, 70, 229, 0.5), 0 4px 6px -4px rgba(79, 70, 229, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  pointer-events: auto;
}

.ems-launcher:hover,
.ems-launcher-btn:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 15px 30px -3px rgba(79, 70, 229, 0.6);
  background: linear-gradient(135deg, #4338ca, #6d28d9);
}

.ems-launcher:active,
.ems-launcher-btn:active {
  transform: translateY(0) scale(0.97);
}

.ems-launcher-badge {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
}

/* Chat Panel Container */
.ems-chat-panel {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 420px;
  max-width: calc(100vw - 32px);
  height: 640px;
  max-height: calc(100vh - 48px);
  background-color: var(--ems-bg);
  border-radius: var(--ems-radius);
  box-shadow: var(--ems-shadow);
  border: 1px solid var(--ems-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 9999999;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: bottom right;
  pointer-events: auto;
}

@media (max-width: 640px) {
  .ems-chat-panel {
    bottom: 0;
    right: 0;
    width: 100vw;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
    border: none;
  }
  .ems-launcher,
  .ems-launcher-btn {
    bottom: 16px;
    right: 16px;
  }
}

/* Header */
.ems-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #1e1b4b, #0f172a);
  border-bottom: 1px solid var(--ems-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ems-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ems-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 700;
  font-size: 15px;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
}

.ems-title {
  font-size: 15px;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.2;
}

.ems-subtitle {
  font-size: 12px;
  color: #818cf8;
  font-weight: 500;
  margin-top: 2px;
}

.ems-close-btn {
  background: none;
  border: none;
  color: var(--ems-text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ems-close-btn:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

/* Context Banner */
.ems-context-banner {
  background-color: #1e1b4b;
  border-bottom: 1px solid #312e81;
  padding: 8px 16px;
  font-size: 12px;
  color: #c7d2fe;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ems-context-badge {
  background-color: #4338ca;
  color: #ffffff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

/* Top Suggested Questions Bar */
.ems-top-suggestions-bar {
  background-color: #0d1322;
  border-bottom: 1px solid #1e293b;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
}

.ems-horizontal-suggestions {
  display: flex;
  flex-direction: row;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 6px;
  width: 100%;
  scrollbar-width: thin;
  scrollbar-color: #4f46e5 #1e293b;
}

.ems-horizontal-suggestions::-webkit-scrollbar {
  height: 5px;
}

.ems-horizontal-suggestions::-webkit-scrollbar-track {
  background: #1e293b;
  border-radius: 4px;
}

.ems-horizontal-suggestions::-webkit-scrollbar-thumb {
  background: #4f46e5;
  border-radius: 4px;
}

.ems-horizontal-suggestions::-webkit-scrollbar-thumb:hover {
  background: #6366f1;
}

.ems-suggestion-chip {
  flex-shrink: 0;
  white-space: nowrap;
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 7px 13px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.ems-suggestion-chip:hover:not(:disabled) {
  background-color: #312e81;
  border-color: #6366f1;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
}

.ems-suggestion-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Message List */
.ems-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background-color: #0b0f19;
}

.ems-message {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  animation: ems-slide-up 0.25s ease-out;
}

.ems-message-user {
  align-self: flex-end;
}

.ems-message-assistant {
  align-self: flex-start;
}

.ems-bubble {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 13.5px;
  line-height: 1.5;
  word-break: break-word;
}

.ems-message-user .ems-bubble {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.ems-message-assistant .ems-bubble {
  background-color: #1e293b;
  color: #f1f5f9;
  border-bottom-left-radius: 4px;
  border: 1px solid #334155;
}

.ems-bubble p {
  margin-bottom: 8px;
}
.ems-bubble p:last-child {
  margin-bottom: 0;
}
.ems-bubble ul, .ems-bubble ol {
  margin-left: 18px;
  margin-bottom: 8px;
}
.ems-bubble li {
  margin-bottom: 4px;
}
.ems-bubble strong {
  font-weight: 600;
  color: #ffffff;
}

.ems-sources {
  margin-top: 8px;
  font-size: 11px;
  color: #94a3b8;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ems-source-tag {
  background-color: #0f172a;
  border: 1px solid #334155;
  padding: 2px 8px;
  border-radius: 6px;
  color: #818cf8;
}

/* Event Cards */
.ems-cards-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
  width: 100%;
}

.ems-event-card {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ems-card-title {
  font-weight: 700;
  font-size: 14px;
  color: #ffffff;
}

.ems-card-meta {
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ems-card-btn {
  align-self: flex-start;
  margin-top: 4px;
  background-color: #4f46e5;
  color: #ffffff;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.2s;
}

.ems-card-btn:hover {
  background-color: #4338ca;
}

/* Input Area */
.ems-input-area {
  padding: 14px 16px;
  background-color: #0f172a;
  border-top: 1px solid var(--ems-border);
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.ems-textarea {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 10px 14px;
  color: #ffffff;
  font-size: 13.5px;
  font-family: inherit;
  resize: none;
  max-height: 100px;
  min-height: 40px;
  outline: none;
  transition: border-color 0.2s;
}

.ems-textarea:focus {
  border-color: #6366f1;
}

.ems-send-btn {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  border: none;
  color: #ffffff;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.ems-send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #4338ca, #4f46e5);
  transform: scale(1.05);
}

.ems-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading Dots */
.ems-loading-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
}

.ems-dot {
  width: 6px;
  height: 6px;
  background-color: #818cf8;
  border-radius: 50%;
  animation: ems-pulse 1.4s infinite ease-in-out both;
}

.ems-dot:nth-child(1) { animation-delay: -0.32s; }
.ems-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes ems-slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ems-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes ems-pop-in {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes ems-pulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
`;
