import React, { useState, useEffect } from "react";
import { BotConfig, PageContext, WidgetInitOptions } from "./types";
import { ChatApiClient } from "./api";
import { pageContextManager } from "./context";
import { ChatPanel } from "./ChatPanel";
import { ErrorSpamOverlay } from "./ErrorSpam";
import { MessageSquare, Sparkles } from "lucide-react";

interface ChatWidgetProps {
  options?: WidgetInitOptions;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ options = {} }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [botConfig, setBotConfig] = useState<BotConfig>({
    bot_id: options.botId || "ems",
    name: "The Equinox 2.0 Assistant",
    title: "The Equinox 2.0 Assistant",
    subtitle: "MLRIT CIE E-Summit",
    greeting:
      "Hi! I can help you explore The Equinox 2.0, its 10 sub-events, dates (30–31 Oct), venue at MLRIT Hyderabad, competitions, sponsorship tiers, and contacts.",
    placeholder: "Ask about Equinox events, venue, sponsorship...",
    suggested_prompts: [
      "What is Equinox 2.0?",
      "What events are there?",
      "When is Equinox?",
      "Tell me about IPL Auction",
      "Which event is for internships?",
      "What is Startup Poly?",
      "What is Pitch Deck?",
      "Who can I contact?"
    ],
    cooldown_seconds: 10,
  });

  const [pageContext, setPageContext] = useState<PageContext>(() =>
    pageContextManager.getContext()
  );

  const [isErrorSpamActive, setIsErrorSpamActive] = useState(false);
  const [isCooldown, setIsCooldown] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState(10);

  const [apiClient] = useState(
    () => new ChatApiClient(options.apiUrl || "http://localhost:8000", options.botId || "ems")
  );

  useEffect(() => {
    // Fetch live bot config
    apiClient.fetchBotConfig().then((cfg) => {
      setBotConfig(cfg);
    });

    // Subscribe to page context updates
    const unsubscribe = pageContextManager.subscribe((ctx) => {
      setPageContext(ctx);
    });

    // Listen for custom global events
    const handleOpen = () => setIsOpen(true);
    const handleClose = () => setIsOpen(false);
    const handleToggle = () => setIsOpen((prev) => !prev);

    window.addEventListener("ems-assistant:open", handleOpen);
    window.addEventListener("ems-assistant:close", handleClose);
    window.addEventListener("ems-assistant:toggle", handleToggle);

    return () => {
      unsubscribe();
      window.removeEventListener("ems-assistant:open", handleOpen);
      window.removeEventListener("ems-assistant:close", handleClose);
      window.removeEventListener("ems-assistant:toggle", handleToggle);
    };
  }, [apiClient]);

  const handleTriggerErrorSpam = () => {
    setIsErrorSpamActive(true);
    setIsCooldown(true);
    setCooldownRemaining(botConfig.cooldown_seconds || 10);

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
  };

  const handleDismissErrorSpam = () => {
    setIsErrorSpamActive(false);
  };

  return (
    <div className="ems-widget-root">
      {/* 10-second Error Spam Overlay for Out-of-Scope Requests */}
      <ErrorSpamOverlay
        isActive={isErrorSpamActive}
        durationSeconds={botConfig.cooldown_seconds || 10}
        onComplete={handleDismissErrorSpam}
      />

      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="ems-launcher-btn"
          aria-label="Open The Equinox 2.0 Assistant"
          title="Open The Equinox 2.0 Assistant"
        >
          <Sparkles className="ems-launcher-sparkle" size={16} />
          <MessageSquare size={24} />
          <span className="ems-launcher-badge">Equinox AI</span>
        </button>
      )}

      {/* Slide-out Chat Panel */}
      {isOpen && (
        <ChatPanel
          botConfig={botConfig}
          pageContext={pageContext}
          apiClient={apiClient}
          onClose={() => setIsOpen(false)}
          onTriggerErrorSpam={handleTriggerErrorSpam}
          isCooldown={isCooldown}
          cooldownRemaining={cooldownRemaining}
        />
      )}
    </div>
  );
};
