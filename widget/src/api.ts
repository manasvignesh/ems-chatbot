import { BotConfig, ChatMessage, ChatResponse, PageContext } from './types';

export class ChatApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  async fetchConfig(botId: string): Promise<BotConfig> {
    try {
      const res = await fetch(`${this.baseUrl}/api/config/${botId}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch {
      return {
        bot_id: botId,
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
    botId: string,
    message: string,
    conversationId?: string,
    pageContext?: PageContext | null,
    history?: ChatMessage[]
  ): Promise<ChatResponse> {
    const payload = {
      bot_id: botId,
      message,
      conversation_id: conversationId,
      page_context: pageContext || undefined,
      conversation_history: history || undefined,
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
