import { BotConfig, ChatApiResponse, MessageItem, PageContext } from "./types";

export class ChatApiClient {
  private baseUrl: string;
  private botId: string;

  constructor(baseUrl: string = "http://localhost:8000", botId: string = "ems") {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.botId = botId;
  }

  setBaseUrl(url: string) {
    this.baseUrl = url.replace(/\/+$/, "");
  }

  setBotId(botId: string) {
    this.botId = botId;
  }

  async fetchBotConfig(): Promise<BotConfig> {
    try {
      const res = await fetch(`${this.baseUrl}/api/config/${this.botId}`);
      if (!res.ok) {
        throw new Error(`Failed to fetch bot config: ${res.statusText}`);
      }
      return await res.json();
    } catch (e) {
      console.warn("[EMS Assistant] Config fetch fallback:", e);
      return {
        bot_id: this.botId,
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
      };
    }
  }

  async sendMessage(
    message: string,
    conversationId?: string,
    conversationHistory: MessageItem[] = [],
    pageContext?: PageContext
  ): Promise<ChatApiResponse> {
    const payload = {
      bot_id: this.botId,
      message,
      conversation_id: conversationId,
      conversation_history: conversationHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      page_context: pageContext,
    };

    try {
      const res = await fetch(`${this.baseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        if (res.status === 429) {
          return {
            status: "error",
            message: "Too many requests. Please slow down and wait a moment.",
          };
        }
        const errorData = await res.json().catch(() => ({}));
        return {
          status: "error",
          message: errorData.message || `Server error (${res.status})`,
        };
      }

      const data: ChatApiResponse = await res.json();
      return data;
    } catch (e: any) {
      console.error("[EMS Assistant] Chat API Error:", e);
      return {
        status: "error",
        message:
          "Unable to connect to EMS Assistant backend. Please verify your connection.",
      };
    }
  }
}
