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
    name: "EMS Assistant",
    title: "EMS Assistant",
    subtitle: "Event Assistant",
    greeting:
      "Hi! I can help you discover events, understand event details, schedules, venues, registration information, rules, and other EMS-related information.",
    placeholder: "Ask about events, venues, rules...",
    suggested_prompts: [
      "Events happening today",
      "What workshops are happening this week?",
      "Any hackathons this month?",
      "Tell me about HackVerse",
      "Registration deadlines",
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
    setCooldownRemaining(10);

    const timer = setInterval(() => {
      setCooldownRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsCooldown(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleSpamComplete = () => {
    setIsErrorSpamActive(false);
  };

  return (
    <>
      {/* 10-Second Error Spam Overlay (Outside Shadow DOM via Portal to body) */}
      {isErrorSpamActive && (
        <ErrorSpamOverlay durationSeconds={10} onComplete={handleSpamComplete} />
      )}

      {/* Main Chat Panel */}
      {isOpen && (
        <ChatPanel
          apiClient={apiClient}
          botConfig={botConfig}
          pageContext={pageContext}
          onClose={() => setIsOpen(false)}
          onTriggerErrorSpam={handleTriggerErrorSpam}
          isCooldown={isCooldown}
          cooldownRemaining={cooldownRemaining}
        />
      )}

      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          className="ems-launcher"
          onClick={() => setIsOpen(true)}
          aria-label="Open EMS Assistant"
        >
          <Sparkles size={18} />
          <span>Ask EMS</span>
          <span className="ems-launcher-badge" />
        </button>
      )}
    </>
  );
};
