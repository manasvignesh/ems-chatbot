export interface PageContext {
  pageType?: string;
  eventId?: string;
  eventName?: string;
  pathname?: string;
}

export interface EventCardData {
  type: string;
  event_id: string;
  title: string;
  date?: string;
  venue?: string;
  organizer?: string;
  category?: string;
  url?: string;
}

export interface SourceReference {
  title: string;
  source_type: string;
  url?: string;
}

export interface MessageItem {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  sources?: SourceReference[];
  cards?: EventCardData[];
}

export interface BotConfig {
  bot_id: string;
  name: string;
  title: string;
  subtitle: string;
  greeting: string;
  placeholder: string;
  suggested_prompts: string[];
  cooldown_seconds: number;
}

export interface ChatResponse {
  status: "success" | "out_of_scope" | "error";
  conversation_id?: string;
  answer?: string;
  sources?: SourceReference[];
  cards?: EventCardData[];
  classification_level?: "IN_SCOPE" | "LIKELY_IN_SCOPE" | "AMBIGUOUS" | "SUSPICIOUS" | "CLEARLY_OUT_OF_SCOPE";
  warning_type?: "invalid_event_pass" | "suspicious_pass";
  ticket_number?: string;
  cooldown_seconds?: number;
  reason?: string;
  message?: string;
}

export type ChatApiResponse = ChatResponse;

export interface WidgetInitOptions {
  apiUrl?: string;
  botId?: string;
  theme?: "light" | "dark" | "auto";
  position?: "bottom-right" | "bottom-left";
  initialContext?: PageContext;
}
