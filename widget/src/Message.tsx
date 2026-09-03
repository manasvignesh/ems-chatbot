import React from "react";
import { MessageItem } from "./types";
import { EventCard } from "./EventCard";
import { Sparkles } from "lucide-react";

interface MessageProps {
  message: MessageItem;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === "user";

  // Simple markdown renderer for paragraphs, bullet points, and bold text
  const renderFormattedText = (text: string) => {
    const paragraphs = text.split("\n\n");

    return paragraphs.map((para, pIdx) => {
      // Check if paragraph is a bullet list
      const lines = para.split("\n");
      const isList = lines.every((line) => line.trim().startsWith("- ") || line.trim().startsWith("* ") || /^\d+\.\s/.test(line.trim()));

      if (isList) {
        return (
          <ul key={pIdx} style={{ margin: "6px 0 6px 18px" }}>
            {lines.map((line, lIdx) => {
              const cleanLine = line.replace(/^[-*]\s+|\d+\.\s+/, "");
              return <li key={lIdx} dangerouslySetInnerHTML={{ __html: formatInline(cleanLine) }} />;
            })}
          </ul>
        );
      }

      return (
        <p key={pIdx} dangerouslySetInnerHTML={{ __html: formatInline(para) }} />
      );
    });
  };

  const formatInline = (text: string): string => {
    let formatted = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // **bold**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // *italic*
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // `code`
    formatted = formatted.replace(/`([^`]+)`/g, "<code style='background:rgba(0,0,0,0.06);padding:2px 4px;border-radius:4px;font-size:12px;'>$1</code>");

    return formatted;
  };

  return (
    <div className={`ems-message-row ${message.role}`}>
      {!isUser && (
        <div
          style={{
            width: "28px",
            height: "28px",
            borderRadius: "8px",
            background: "#4f46e5",
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            marginTop: "2px",
          }}
        >
          <Sparkles size={16} />
        </div>
      )}

      <div className={`ems-bubble ${message.role}`}>
        {renderFormattedText(message.content)}

        {/* Structured Event Cards */}
        {message.cards && message.cards.length > 0 && (
          <div className="ems-cards-container">
            {message.cards.map((card, idx) => (
              <EventCard key={idx} card={card} />
            ))}
          </div>
        )}

        {/* Source References */}
        {message.sources && message.sources.length > 0 && (
          <div className="ems-sources-container">
            {message.sources.map((src, idx) => (
              <span key={idx} className="ems-source-tag">
                📄 {src.title}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
