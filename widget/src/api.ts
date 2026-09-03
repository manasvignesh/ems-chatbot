import { BotConfig, MessageItem, ChatResponse, PageContext } from './types';

export class ChatApiClient {
  private baseUrl: string;
  private botId: string;

  constructor(baseUrl: string, botId: string = 'ems') {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.botId = botId;
  }

  async fetchBotConfig(): Promise<BotConfig> {
    try {
      const res = await fetch(`${this.baseUrl}/api/config/${this.botId}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch {
      return {
        bot_id: this.botId,
        name: 'The Equinox 2.0 Assistant',
        title: 'The Equinox 2.0 Assistant',
        subtitle: 'MLRIT CIE E-Summit',
        greeting: 'Hi! I can help you explore The Equinox 2.0, its 10 sub-events, dates (30–31 Oct), venue at MLRIT Hyderabad, competitions, sponsorship tiers, and contacts.',
        placeholder: 'Ask about Equinox events, venue, sponsorship...',
        suggested_prompts: [
          'What is Equinox 2.0?',
          'What events are there?',
          'When is Equinox?',
          'Tell me about IPL Auction',
          'Which event is for internships?',
          'What is Startup Poly?',
          'What is Pitch Deck?',
          'Who can I contact?'
        ],
        cooldown_seconds: 10,
      };
    }
  }

  async sendMessage(
    message: string,
    conversationId?: string,
    history?: MessageItem[],
    pageContext?: PageContext | null
  ): Promise<ChatResponse> {
    const payload = {
      bot_id: this.botId,
      message,
      conversation_id: conversationId,
      page_context: pageContext || undefined,
      conversation_history: history
        ? history.map((m) => ({ role: m.role, content: m.content }))
        : undefined,
    };

    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (res.status === 429) {
      throw new Error('Rate limit exceeded. Please wait a moment before sending another message.');
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Server error (${res.status})`);
    }

    return await res.json();
  }
}
