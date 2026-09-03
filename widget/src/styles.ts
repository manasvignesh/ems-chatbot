export const WIDGET_STYLES = `
:host {
  --ems-primary: #4f46e5;
  --ems-primary-hover: #4338ca;
  --ems-primary-light: #eef2ff;
  --ems-primary-border: #c7d2fe;
  --ems-bg: #ffffff;
  --ems-card-bg: #f8fafc;
  --ems-border: #e2e8f0;
  --ems-text: #0f172a;
  --ems-text-muted: #64748b;
  --ems-user-bubble: #4f46e5;
  --ems-user-text: #ffffff;
  --ems-bot-bubble: #f1f5f9;
  --ems-bot-text: #0f172a;
  --ems-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  --ems-radius: 16px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--ems-text);
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: inherit;
  margin: 0;
  padding: 0;
}

.ems-launcher {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 999990;
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 9999px;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4), 0 4px 6px -4px rgba(79, 70, 229, 0.2);
  border: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.ems-launcher:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 14px 20px -3px rgba(79, 70, 229, 0.5);
  background: linear-gradient(135deg, #4338ca, #4f46e5);
}

.ems-launcher:active {
  transform: translateY(0) scale(0.98);
}

.ems-launcher-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 8px;
  height: 8px;
  background-color: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px #4f46e5;
}

/* Chat Panel Container */
.ems-chat-panel {
  position: fixed;
  bottom: 88px;
  right: 24px;
  width: 400px;
  max-width: calc(100vw - 32px);
  height: 600px;
  max-height: calc(100vh - 110px);
  background-color: var(--ems-bg);
  border-radius: var(--ems-radius);
  box-shadow: var(--ems-shadow);
  border: 1px solid var(--ems-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 999995;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: bottom right;
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
  .ems-launcher {
    bottom: 16px;
    right: 16px;
  }
}

/* Header */
.ems-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #4f46e5, #4338ca);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ems-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ems-header-icon {
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.ems-header-text h3 {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.2;
}

.ems-header-text p {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 2px;
}

.ems-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ems-header-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ems-header-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

/* Context Badge Bar */
.ems-context-bar {
  background: var(--ems-primary-light);
  padding: 6px 16px;
  font-size: 12px;
  color: var(--ems-primary);
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 1px solid var(--ems-primary-border);
  font-weight: 500;
}

/* Messages Scrollable Body */
.ems-messages-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fdfdfd;
}

/* Empty State & Suggestions */
.ems-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-top: 24px;
  gap: 14px;
}

.ems-empty-icon {
  width: 48px;
  height: 48px;
  background: var(--ems-primary-light);
  color: var(--ems-primary);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.ems-empty-greeting {
  font-size: 14px;
  color: var(--ems-text-muted);
  line-height: 1.5;
  padding: 0 10px;
}

.ems-suggestions-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  margin-top: 8px;
}

.ems-suggestion-chip {
  background: #ffffff;
  border: 1px solid var(--ems-border);
  border-radius: 10px;
  padding: 9px 14px;
  font-size: 13px;
  color: var(--ems-text);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.ems-suggestion-chip:hover {
  border-color: var(--ems-primary);
  background: var(--ems-primary-light);
  color: var(--ems-primary);
  transform: translateX(3px);
}

/* Message Bubbles */
.ems-message-row {
  display: flex;
  gap: 10px;
  max-width: 100%;
}

.ems-message-row.user {
  justify-content: flex-end;
}

.ems-message-row.assistant {
  justify-content: flex-start;
}

.ems-bubble {
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.55;
  max-width: 85%;
  word-break: break-word;
}

.ems-bubble.user {
  background: var(--ems-user-bubble);
  color: var(--ems-user-text);
  border-bottom-right-radius: 4px;
}

.ems-bubble.assistant {
  background: var(--ems-bot-bubble);
  color: var(--ems-bot-text);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--ems-border);
}

.ems-bubble p {
  margin-bottom: 8px;
}
.ems-bubble p:last-child {
  margin-bottom: 0;
}
.ems-bubble ul, .ems-bubble ol {
  margin-left: 18px;
  margin-top: 6px;
  margin-bottom: 6px;
}
.ems-bubble li {
  margin-bottom: 4px;
}
.ems-bubble strong {
  font-weight: 600;
  color: #0f172a;
}
.ems-bubble.user strong {
  color: #ffffff;
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
  background: #ffffff;
  border: 1px solid var(--ems-border);
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.ems-event-card:hover {
  border-color: var(--ems-primary);
  box-shadow: 0 4px 8px rgba(79, 70, 229, 0.12);
}

.ems-card-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.ems-card-meta {
  font-size: 12px;
  color: var(--ems-text-muted);
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 8px;
}

.ems-card-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--ems-primary);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  border-radius: 6px;
  padding: 4px 0;
}

.ems-card-link:hover {
  text-decoration: underline;
}

/* Sources Badge Container */
.ems-sources-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px dashed var(--ems-border);
}

.ems-source-tag {
  background: #e2e8f0;
  color: #475569;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
}

/* Typing Indicator */
.ems-typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}

.ems-dot {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: emsBounce 1.4s infinite ease-in-out both;
}

.ems-dot:nth-child(1) { animation-delay: -0.32s; }
.ems-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes emsBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

/* Footer / Input Area */
.ems-footer {
  padding: 12px 16px;
  background: #ffffff;
  border-top: 1px solid var(--ems-border);
}

.ems-input-box {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid var(--ems-border);
  border-radius: 12px;
  padding: 8px 12px;
  transition: all 0.2s;
}

.ems-input-box:focus-within {
  border-color: var(--ems-primary);
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.ems-input-box.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.ems-textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.4;
  color: var(--ems-text);
  resize: none;
  outline: none;
  max-height: 100px;
  font-family: inherit;
}

.ems-textarea::placeholder {
  color: #94a3b8;
}

.ems-send-btn {
  background: var(--ems-primary);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.ems-send-btn:hover:not(:disabled) {
  background: var(--ems-primary-hover);
}

.ems-send-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

/* Cooldown Alert inside footer */
.ems-cooldown-bar {
  background: #fee2e2;
  color: #991b1b;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 8px;
  margin-top: 8px;
  text-align: center;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
`;
