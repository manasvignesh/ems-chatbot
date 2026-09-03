import React, { useState, useEffect, useRef } from "react";
import { MessageItem, PageContext, BotConfig } from "./types";
import { Message } from "./Message";
import { ChatApiClient } from "./api";
import {
  X,
  RotateCcw,
  Send,
  Sparkles,
  AlertCircle,
  HelpCircle,
  Clock,
} from "lucide-react";

interface ChatPanelProps {
  apiClient: ChatApiClient;
  botConfig: BotConfig;
  pageContext: PageContext;
  onClose: () => void;
  onTriggerErrorSpam: () => void;
  isCooldown: boolean;
  cooldownRemaining: number;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  apiClient,
  botConfig,
  pageContext,
  onClose,
  onTriggerErrorSpam,
  isCooldown,
  cooldownRemaining,
}) => {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputVal, setInputVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>(() => {
    return "session-" + Math.random().toString(36).substring(2, 10);
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleResetConversation = () => {
    setMessages([]);
    setConversationId("session-" + Math.random().toString(36).substring(2, 10));
    setInputVal("");
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputVal).trim();
    if (!text || isLoading || isCooldown) return;

    const userMsg: MessageItem = {
      id: "usr-" + Date.now(),
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal("");
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage(
        text,
        conversationId,
        messages,
        pageContext
      );

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      if (response.status === "out_of_scope") {
        onTriggerErrorSpam();
      } else if (response.status === "success" && response.answer) {
        const botMsg: MessageItem = {
          id: "bot-" + Date.now(),
          role: "assistant",
          content: response.answer,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          sources: response.sources,
          cards: response.cards,
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        const errorMsg: MessageItem = {
          id: "err-" + Date.now(),
          role: "assistant",
          content: response.message || "Sorry, I encountered an issue. Please try again.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } catch (e: any) {
      const errorMsg: MessageItem = {
        id: "err-" + Date.now(),
        role: "assistant",
        content: e.message || "Network error. Please ensure the backend server is running.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const handleCustomSend = (e: any) => {
      if (e.detail && e.detail.text) {
        handleSend(e.detail.text);
      }
    };
    const handleCustomReset = () => {
      handleResetConversation();
    };

    window.addEventListener("ems-assistant:send-message", handleCustomSend);
    window.addEventListener("ems-assistant:reset", handleCustomReset);

    return () => {
      window.removeEventListener("ems-assistant:send-message", handleCustomSend);
      window.removeEventListener("ems-assistant:reset", handleCustomReset);
    };
  }, [conversationId, messages, pageContext, isLoading, isCooldown]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ems-chat-panel">
      {/* Header */}
      <div className="ems-header">
        <div className="ems-header-info">
          <div className="ems-avatar">
            <Sparkles size={18} />
          </div>
          <div>
            <div className="ems-title">{botConfig.title || "The Equinox 2.0 Assistant"}</div>
            <div className="ems-subtitle">{botConfig.subtitle || "MLRIT CIE E-Summit"}</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <button
            className="ems-close-btn"
            title="Reset conversation"
            onClick={handleResetConversation}
          >
            <RotateCcw size={15} />
          </button>
          <button className="ems-close-btn" title="Close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Active Page Context Indicator */}
      {pageContext.eventId && (
        <div className="ems-context-banner">
          <span className="ems-context-badge">Context</span>
          <span>Viewing: <strong>{pageContext.eventName || pageContext.eventId}</strong></span>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="ems-messages">
        {messages.length === 0 ? (
          <div style={{ padding: "16px 8px", textAlign: "center" }}>
            <div style={{
              width: "48px",
              height: "48px",
              borderRadius: "14px",
              background: "rgba(79, 70, 229, 0.15)",
              color: "#818cf8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 12px auto"
            }}>
              <HelpCircle size={26} />
            </div>
            <p style={{ fontSize: "13px", color: "#cbd5e1", lineHeight: "1.5", marginBottom: "16px" }}>
              {botConfig.greeting}
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", textAlign: "left" }}>
              {botConfig.suggested_prompts.map((prompt, idx) => (
                <button
                  key={idx}
                  className="ems-suggestion-chip"
                  onClick={() => handleSend(prompt)}
                  disabled={isCooldown}
                  style={{ textAlign: "left", width: "100%", padding: "8px 12px" }}
                >
                  ✨ {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => <Message key={m.id} message={m} />)
        )}

        {/* Typing Loading Indicator */}
        {isLoading && (
          <div className="ems-message ems-message-assistant">
            <div className="ems-bubble">
              <div className="ems-loading-dots">
                <div className="ems-dot"></div>
                <div className="ems-dot"></div>
                <div className="ems-dot"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input Area */}
      <div style={{ background: "#0f172a", borderTop: "1px solid #334155" }}>
        {isCooldown && (
          <div style={{
            background: "rgba(239, 68, 68, 0.15)",
            borderBottom: "1px solid rgba(239, 68, 68, 0.3)",
            padding: "6px 14px",
            fontSize: "11.5px",
            color: "#fca5a5",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            <Clock size={13} />
            <span>Chat paused during cooldown: {cooldownRemaining}s</span>
          </div>
        )}

        <div className="ems-input-area">
          <textarea
            ref={textareaRef}
            className="ems-textarea"
            placeholder={
              isCooldown
                ? "Chat paused during cooldown..."
                : botConfig.placeholder || "Ask about Equinox events, venue, sponsorship..."
            }
            rows={1}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || isCooldown}
          />

          <button
            className="ems-send-btn"
            onClick={() => handleSend()}
            disabled={!inputVal.trim() || isLoading || isCooldown}
            title="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};
