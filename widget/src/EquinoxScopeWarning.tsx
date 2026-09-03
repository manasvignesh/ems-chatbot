import React, { useEffect, useState, useRef } from "react";
import { X, Sparkles, AlertTriangle, ShieldAlert } from "lucide-react";

interface EquinoxScopeWarningProps {
  isActive: boolean;
  classificationLevel?: "SUSPICIOUS" | "CLEARLY_OUT_OF_SCOPE";
  warningType?: "invalid_event_pass" | "suspicious_pass";
  ticketNumber?: string;
  durationSeconds?: number;
  reason?: string;
  message?: string;
  onDismiss: () => void;
}

export const EquinoxScopeWarning: React.FC<EquinoxScopeWarningProps> = ({
  isActive,
  classificationLevel = "CLEARLY_OUT_OF_SCOPE",
  warningType = "invalid_event_pass",
  ticketNumber = "EQX-PASS-403",
  durationSeconds = 3,
  reason,
  message = "This assistant is focused on The Equinox 2.0. Ask me about events, dates, sub-events, venue, sponsorship, or contacts.",
  onDismiss,
}) => {
  const [progress, setProgress] = useState(100);
  const isSuspicious = classificationLevel === "SUSPICIOUS";
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    if (!isActive) {
      setProgress(100);
      return;
    }

    const durationMs = durationSeconds * 1000;
    startTimeRef.current = Date.now();

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      const remainingPct = Math.max(0, 100 - (elapsed / durationMs) * 100);
      setProgress(remainingPct);

      if (elapsed >= durationMs) {
        clearInterval(interval);
        onDismiss();
      }
    }, 50);

    return () => {
      clearInterval(interval);
    };
  }, [isActive, durationSeconds, onDismiss]);

  if (!isActive) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className={`equinox-ticket-wrapper ${isSuspicious ? "suspicious" : "out-of-scope"}`}
    >
      {/* Top Ticket Header */}
      <div className="equinox-ticket-header">
        <div className="equinox-ticket-brand">
          <Sparkles size={14} className="equinox-ticket-sparkle" />
          <span>THE EQUINOX 2.0 • QUERY PASS</span>
        </div>
        <div className="equinox-ticket-id">
          <span>{ticketNumber}</span>
          <button
            onClick={onDismiss}
            className="equinox-ticket-close"
            title="Dismiss"
            aria-label="Dismiss warning"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* SVG Perforated Notch Left & Right */}
      <div className="equinox-ticket-perforation-row">
        <svg className="equinox-notch-left" width="12" height="24" viewBox="0 0 12 24">
          <path d="M 0,0 C 6.6,0 12,5.4 12,12 C 12,18.6 6.6,24 0,24 Z" fill="#0b0f19" />
        </svg>
        <div className="equinox-dashed-perforation"></div>
        <svg className="equinox-notch-right" width="12" height="24" viewBox="0 0 12 24">
          <path d="M 12,0 C 5.4,0 0,5.4 0,12 C 0,18.6 5.4,24 12,24 Z" fill="#0b0f19" />
        </svg>
      </div>

      {/* Ticket Body Content */}
      <div className="equinox-ticket-body">
        {/* Stamped Stamp Badge SVG */}
        <div className={`equinox-stamp-badge ${isSuspicious ? "badge-suspicious" : "badge-invalid"}`}>
          {isSuspicious ? (
            <>
              <AlertTriangle size={13} />
              <span>NOTICE: OUTSIDE SCOPE</span>
            </>
          ) : (
            <>
              <ShieldAlert size={13} />
              <span>INVALID EVENT PASS</span>
            </>
          )}
        </div>

        <p className="equinox-ticket-message">{message}</p>
      </div>

      {/* Auto-Dismiss Progress Bar */}
      <div className="equinox-ticket-progress-track">
        <div
          className="equinox-ticket-progress-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
};
