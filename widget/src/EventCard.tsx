import React from "react";
import { EventCardData } from "./types";
import { Calendar, MapPin, ExternalLink, Users } from "lucide-react";

interface EventCardProps {
  card: EventCardData;
}

export const EventCard: React.FC<EventCardProps> = ({ card }) => {
  return (
    <div className="ems-event-card">
      <div className="ems-card-title">{card.title}</div>
      <div className="ems-card-meta">
        {card.date && (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Calendar size={13} style={{ flexShrink: 0, opacity: 0.7 }} />
            <span>{card.date}</span>
          </div>
        )}
        {card.venue && (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <MapPin size={13} style={{ flexShrink: 0, opacity: 0.7 }} />
            <span>{card.venue}</span>
          </div>
        )}
        {card.organizer && (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Users size={13} style={{ flexShrink: 0, opacity: 0.7 }} />
            <span>{card.organizer}</span>
          </div>
        )}
      </div>
      {card.url && (
        <a
          href={card.url}
          className="ems-card-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          View Event
          <ExternalLink size={12} />
        </a>
      )}
    </div>
  );
};
