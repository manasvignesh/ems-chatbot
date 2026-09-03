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
        // Trigger the intentional 10-second error spam effect
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
        content: "Network error. Please ensure the backend server is running.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

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
        <div className="ems-header-title">
          <div className="ems-header-icon">
            <Sparkles size={20} />
          </div>
          <div className="ems-header-text">
            <h3>{botConfig.title || "EMS Assistant"}</h3>
            <p>{botConfig.subtitle || "Event Assistant"}</p>
          </div>
        </div>

        <div className="ems-header-actions">
          <button
            className="ems-header-btn"
            title="Reset conversation"
            onClick={handleResetConversation}
          >
            <RotateCcw size={16} />
          </button>
          <button className="ems-header-btn" title="Close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Active Page Context Indicator */}
      {pageContext.eventId && (
        <div className="ems-context-bar">
          <span>📍</span>
          <span>Viewing: <strong>{pageContext.eventName || pageContext.eventId}</strong></span>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="ems-messages-body">
        {messages.length === 0 ? (
          <div className="ems-empty-state">
            <div className="ems-empty-icon">
              <HelpCircle size={28} />
            </div>
            <p className="ems-empty-greeting">{botConfig.greeting}</p>

            <div className="ems-suggestions-grid">
              {botConfig.suggested_prompts.map((prompt, idx) => (
                <button
                  key={idx}
                  className="ems-suggestion-chip"
                  onClick={() => handleSend(prompt)}
                  disabled={isCooldown}
                >
                  ⚡ {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => <Message key={m.id} message={m} />)
        )}

        {/* Typing Loading Indicator */}
        {isLoading && (
          <div className="ems-message-row assistant">
            <div className="ems-bubble assistant ems-typing">
              <div className="ems-dot"></div>
              <div className="ems-dot"></div>
              <div className="ems-dot"></div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input */}
      <div className="ems-footer">
        {isCooldown && (
          <div className="ems-cooldown-bar">
            <Clock size={14} />
            <span>Query rejected. Chat paused: {cooldownRemaining}s</span>
          </div>
        )}

        <div className={`ems-input-box ${isCooldown ? "disabled" : ""}`}>
          <textarea
            ref={textareaRef}
            className="ems-textarea"
            placeholder={
              isCooldown
                ? "Chat paused during cooldown..."
                : botConfig.placeholder || "Ask about events, venues, rules..."
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
