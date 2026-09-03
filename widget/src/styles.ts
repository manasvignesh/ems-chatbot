export const WIDGET_STYLES = `
:host {
  --ems-primary: #6366f1;
  --ems-primary-hover: #4f46e5;
  --ems-primary-light: #eef2ff;
  --ems-primary-border: #818cf8;
  --ems-bg: #0b0f19;
  --ems-card-bg: #151c2e;
  --ems-border: #222f49;
  --ems-text: #f8fafc;
  --ems-text-muted: #94a3b8;
  --ems-user-bubble: #6366f1;
  --ems-user-text: #ffffff;
  --ems-bot-bubble: #151c2e;
  --ems-bot-text: #f8fafc;
  --ems-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.7);
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

/* Futuristic Cyber Robot Launcher Button */
.ems-launcher-cyber {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999999;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, rgba(30, 27, 75, 0.95), rgba(15, 23, 42, 0.95));
  backdrop-filter: blur(12px);
  color: #ffffff;
  padding: 8px 18px 8px 10px;
  border-radius: 9999px;
  box-shadow: 0 10px 30px -5px rgba(99, 102, 241, 0.45), 0 0 0 1px rgba(129, 140, 248, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  outline: none;
  pointer-events: auto;
}

.ems-launcher-cyber:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 15px 40px -5px rgba(139, 92, 246, 0.65), 0 0 20px rgba(99, 102, 241, 0.5), 0 0 0 1.5px rgba(167, 139, 250, 0.6);
  background: linear-gradient(135deg, rgba(49, 46, 129, 0.98), rgba(24, 24, 58, 0.98));
}

.ems-launcher-cyber:active {
  transform: translateY(0) scale(0.97);
}

/* Robot Avatar & Pulse Animation */
.ems-robot-avatar-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ems-robot-pulse-ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #6366f1, #a855f7, #ec4899, #6366f1);
  animation: ems-spin-glow 3s linear infinite;
  filter: blur(4px);
  opacity: 0.8;
}

.ems-robot-icon-box {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
  z-index: 2;
  transition: transform 0.3s ease;
}

.ems-launcher-cyber:hover .ems-robot-icon-box {
  transform: rotate(-10deg) scale(1.08);
}

.ems-robot-icon {
  animation: ems-robot-bounce 2.5s ease-in-out infinite;
}

.ems-robot-online-dot {
  position: absolute;
  bottom: 0px;
  right: 0px;
  width: 10px;
  height: 10px;
  background-color: #10b981;
  border: 2px solid #0f172a;
  border-radius: 50%;
  box-shadow: 0 0 8px #10b981;
}

/* Label Box */
.ems-launcher-label-box {
  display: flex;
  flex-direction: column;
  text-align: left;
  line-height: 1.15;
}

.ems-launcher-title {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: -0.01em;
  background: linear-gradient(90deg, #ffffff, #c7d2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.ems-launcher-subtitle {
  font-size: 11px;
  font-weight: 600;
  color: #a5b4fc;
}

.ems-launcher-sparkle-glow {
  color: #fbbf24;
  margin-left: 2px;
  filter: drop-shadow(0 0 4px #fbbf24);
  animation: ems-pulse-sparkle 2s infinite ease-in-out;
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
  .ems-launcher-cyber {
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
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.4);
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
  background-color: #151c2e;
  border: 1px solid #28354f;
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
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.ems-suggestion-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Messages Scroll Area */
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
  background-color: #151c2e;
  color: #f1f5f9;
  border-bottom-left-radius: 4px;
  border: 1px solid #28354f;
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

/* =======================================================
   Equinox Event Ticket / Pass Warning Component Styles
   ======================================================= */
.equinox-ticket-wrapper {
  margin: 12px 0 8px 0;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  animation: ems-ticket-slide 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: #111827;
  border: 1px solid #374151;
  position: relative;
}

.equinox-ticket-wrapper.out-of-scope {
  border-color: rgba(239, 68, 68, 0.5);
  background: linear-gradient(180deg, #1f131a 0%, #111827 100%);
}

.equinox-ticket-wrapper.suspicious {
  border-color: rgba(245, 158, 11, 0.5);
  background: linear-gradient(180deg, #1f1a13 0%, #111827 100%);
}

.equinox-ticket-header {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.equinox-ticket-brand {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #c7d2fe;
}

.equinox-ticket-sparkle {
  color: #818cf8;
}

.equinox-ticket-id {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10.5px;
  font-family: monospace;
  color: #94a3b8;
  font-weight: 700;
}

.equinox-ticket-close {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.equinox-ticket-close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.equinox-ticket-perforation-row {
  display: flex;
  align-items: center;
  width: 100%;
  height: 12px;
  position: relative;
  overflow: hidden;
}

.equinox-notch-left {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.equinox-notch-right {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

.equinox-dashed-perforation {
  flex: 1;
  border-bottom: 2px dashed rgba(255, 255, 255, 0.15);
  margin: 0 14px;
}

.equinox-ticket-body {
  padding: 12px 14px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.equinox-stamp-badge {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.badge-invalid {
  background: rgba(239, 68, 68, 0.15);
  border: 1.5px solid #ef4444;
  color: #f87171;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}

.badge-suspicious {
  background: rgba(245, 158, 11, 0.15);
  border: 1.5px solid #f59e0b;
  color: #fbbf24;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
}

.equinox-ticket-message {
  font-size: 12.5px;
  color: #e2e8f0;
  line-height: 1.45;
}

.equinox-ticket-progress-track {
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  width: 100%;
  overflow: hidden;
}

.equinox-ticket-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #ef4444);
  transition: width 0.05s linear;
}

.equinox-cooldown-notice {
  background: rgba(99, 102, 241, 0.12);
  border-bottom: 1px solid rgba(99, 102, 241, 0.25);
  padding: 6px 14px;
  font-size: 11.5px;
  color: #c7d2fe;
  display: flex;
  align-items: center;
  gap: 6px;
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
  background-color: #0b0f19;
  border-top: 1px solid #1f293d;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.ems-textarea {
  flex: 1;
  background-color: #151c2e;
  border: 1px solid #28354f;
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

@keyframes ems-spin-glow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes ems-robot-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

@keyframes ems-pulse-sparkle {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
}

@keyframes ems-slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ems-ticket-slide {
  from { opacity: 0; transform: translateY(-10px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
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
