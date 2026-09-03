import React, { useState, useEffect, useRef } from "react";
import { MessageItem, PageContext, BotConfig, ChatResponse } from "./types";
import { Message } from "./Message";
import { ChatApiClient } from "./api";
import { EquinoxScopeWarning } from "./EquinoxScopeWarning";
import {
  X,
  RotateCcw,
  Send,
  Sparkles,
  Clock,
} from "lucide-react";

interface ChatPanelProps {
  apiClient: ChatApiClient;
  botConfig: BotConfig;
  pageContext: PageContext;
  onClose: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  apiClient,
  botConfig,
  pageContext,
  onClose,
}) => {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputVal, setInputVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>(() => {
    return "session-" + Math.random().toString(36).substring(2, 10);
  });

  // Ticket Warning State
  const [scopeWarning, setScopeWarning] = useState<{
    isActive: boolean;
    classificationLevel?: "SUSPICIOUS" | "CLEARLY_OUT_OF_SCOPE";
    warningType?: "invalid_event_pass" | "suspicious_pass";
    ticketNumber?: string;
    durationSeconds?: number;
    reason?: string;
    message?: string;
  }>({
    isActive: false,
  });

  const [isCooldown, setIsCooldown] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scopeWarning]);

  const handleResetConversation = () => {
    setMessages([]);
    setConversationId("session-" + Math.random().toString(36).substring(2, 10));
    setInputVal("");
    setScopeWarning({ isActive: false });
    setIsCooldown(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleDismissWarning = () => {
    setScopeWarning({ isActive: false });
    setIsCooldown(false);
    setCooldownRemaining(0);
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
      const response: ChatResponse = await apiClient.sendMessage(
        text,
        conversationId,
        messages,
        pageContext
      );

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      if (response.status === "out_of_scope") {
        const isSuspicious = response.classification_level === "SUSPICIOUS";
        const duration = isSuspicious ? 2.5 : 3.5;

        // Trigger lightweight ticket warning pass
        setScopeWarning({
          isActive: true,
          classificationLevel: isSuspicious ? "SUSPICIOUS" : "CLEARLY_OUT_OF_SCOPE",
          warningType: response.warning_type || "invalid_event_pass",
          ticketNumber: response.ticket_number || "EQX-PASS-403",
          durationSeconds: duration,
          reason: response.reason,
          message: response.message || "This assistant is focused on The Equinox 2.0. Ask me about events, dates, sub-events, venue, sponsorship, or contacts.",
        });

        setIsCooldown(true);
        setCooldownRemaining(Math.ceil(duration));

        const interval = setInterval(() => {
          setCooldownRemaining((prev) => {
            if (prev <= 1) {
              clearInterval(interval);
              setIsCooldown(false);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

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

      {/* Top Horizontal Suggested Questions Bar */}
      <div className="ems-top-suggestions-bar">
        <div className="ems-horizontal-suggestions">
          {botConfig.suggested_prompts.map((prompt, idx) => (
            <button
              key={idx}
              className="ems-suggestion-chip"
              onClick={() => handleSend(prompt)}
              disabled={isCooldown}
            >
              ✨ {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="ems-messages">
        {messages.map((m) => (
          <Message key={m.id} message={m} />
        ))}

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

        {/* Inline Equinox Scope Ticket Warning Pass */}
        {scopeWarning.isActive && (
          <EquinoxScopeWarning
            isActive={scopeWarning.isActive}
            classificationLevel={scopeWarning.classificationLevel}
            warningType={scopeWarning.warningType}
            ticketNumber={scopeWarning.ticketNumber}
            durationSeconds={scopeWarning.durationSeconds}
            reason={scopeWarning.reason}
            message={scopeWarning.message}
            onDismiss={handleDismissWarning}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input Area */}
      <div style={{ background: "#0b0f19", borderTop: "1px solid #1f293d" }}>
        {isCooldown && (
          <div className="equinox-cooldown-notice">
            <Clock size={12} />
            <span>Pass validation paused ({cooldownRemaining}s)</span>
          </div>
        )}

        <div className="ems-input-area">
          <textarea
            ref={textareaRef}
            className="ems-textarea"
            placeholder={
              isCooldown
                ? "Chat paused during ticket validation..."
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
