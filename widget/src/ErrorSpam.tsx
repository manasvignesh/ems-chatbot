import React, { useEffect, useState, useRef } from "react";
import ReactDOM from "react-dom";

interface ErrorSpamProps {
  durationSeconds?: number;
  onComplete: () => void;
}

interface SpamTag {
  id: number;
  text: string;
  top: number; // percentage
  left: number; // percentage
  rotation: number; // degrees
  scale: number;
  animType: "shake" | "pulse" | "glitch";
  colorTheme: "red" | "crimson" | "amber" | "dark";
}

const ERROR_MESSAGES = [
  "OUT OF SCOPE",
  "INVALID QUERY",
  "EMS ONLY",
  "QUERY REJECTED",
  "CONTEXT VIOLATION",
  "EVENT QUESTIONS ONLY",
  "ERROR 403",
  "WRONG CONTEXT",
  "REQUEST BLOCKED",
  "INVALID CONTEXT",
  "EMS ACCESS FILTER",
  "QUERY BLOCKED",
  "NOT AN EMS QUERY",
  "COLLEGE EVENTS ONLY",
];

const THEME_STYLES = {
  red: { bg: "#ef4444", text: "#ffffff", border: "#b91c1c" },
  crimson: { bg: "#dc2626", text: "#ffffff", border: "#991b1b" },
  amber: { bg: "#f59e0b", text: "#000000", border: "#d97706" },
  dark: { bg: "#0f172a", text: "#ef4444", border: "#dc2626" },
};

export const ErrorSpamOverlay: React.FC<ErrorSpamProps> = ({
  durationSeconds = 10,
  onComplete,
}) => {
  const [tags, setTags] = useState<SpamTag[]>([]);
  const [remaining, setRemaining] = useState(durationSeconds);
  const tagCounter = useRef(0);
  const prefersReducedMotion = useRef(
    typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );

  useEffect(() => {
    // Inject keyframes into document head if not already present
    const styleId = "ems-error-spam-keyframes";
    if (!document.getElementById(styleId)) {
      const styleEl = document.createElement("style");
      styleEl.id = styleId;
      styleEl.innerHTML = `
        @keyframes emsShake {
          0%, 100% { transform: translate(0, 0) rotate(var(--rot)); }
          20% { transform: translate(-4px, 4px) rotate(calc(var(--rot) - 3deg)); }
          40% { transform: translate(4px, -3px) rotate(calc(var(--rot) + 3deg)); }
          60% { transform: translate(-3px, -2px) rotate(calc(var(--rot) - 2deg)); }
          80% { transform: translate(3px, 3px) rotate(calc(var(--rot) + 2deg)); }
        }
        @keyframes emsPulse {
          0%, 100% { opacity: 0.95; transform: scale(var(--scale)) rotate(var(--rot)); }
          50% { opacity: 0.4; transform: scale(calc(var(--scale) * 1.1)) rotate(var(--rot)); }
        }
        @keyframes emsSpawnFade {
          0% { opacity: 0; transform: scale(0.4) rotate(0deg); }
          100% { opacity: 0.95; transform: scale(var(--scale)) rotate(var(--rot)); }
        }
      `;
      document.head.appendChild(styleEl);
    }

    // Function to generate a new random tag
    const spawnTag = () => {
      tagCounter.current += 1;
      const text = ERROR_MESSAGES[Math.floor(Math.random() * ERROR_MESSAGES.length)];
      const anims: Array<"shake" | "pulse" | "glitch"> = ["shake", "pulse", "glitch"];
      const themes: Array<"red" | "crimson" | "amber" | "dark"> = [
        "red",
        "crimson",
        "amber",
        "dark",
      ];

      const newTag: SpamTag = {
        id: tagCounter.current,
        text,
        top: Math.random() * 85 + 5, // 5% to 90%
        left: Math.random() * 80 + 5, // 5% to 85%
        rotation: (Math.random() - 0.5) * 40, // -20deg to +20deg
        scale: Math.random() * 0.5 + 0.85, // 0.85 to 1.35
        animType: anims[Math.floor(Math.random() * anims.length)],
        colorTheme: themes[Math.floor(Math.random() * themes.length)],
      };

      setTags((prev) => {
        // Cap max simultaneous DOM elements to 35 to prevent lag
        const updated = [...prev, newTag];
        if (updated.length > 35) {
          return updated.slice(updated.length - 35);
        }
        return updated;
      });
    };

    // Spawn burst immediately
    for (let i = 0; i < 8; i++) {
      spawnTag();
    }

    // Spawn continuous tags throughout the effect
    const spawnInterval = setInterval(spawnTag, 280);

    // Countdown interval
    const countdownInterval = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          clearInterval(spawnInterval);
          onComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(spawnInterval);
      clearInterval(countdownInterval);
    };
  }, [durationSeconds, onComplete]);

  const overlayContent = (
    <>
      {/* Accessible screen-reader status */}
      <div
        role="status"
        aria-live="polite"
        style={{
          position: "absolute",
          width: "1px",
          height: "1px",
          padding: 0,
          margin: "-1px",
          overflow: "hidden",
          clip: "rect(0, 0, 0, 0)",
          border: 0,
        }}
      >
        This question is outside the EMS Assistant scope. Chat is temporarily unavailable for 10 seconds.
      </div>

      {/* Visual random error message overlay */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          pointerEvents: "none",
          zIndex: 999999,
          overflow: "hidden",
          userSelect: "none",
        }}
      >
        {tags.map((tag) => {
          const theme = THEME_STYLES[tag.colorTheme];
          const isReduced = prefersReducedMotion.current;

          let animationStyle = "emsSpawnFade 0.25s ease-out forwards";
          if (!isReduced) {
            if (tag.animType === "shake") {
              animationStyle += ", emsShake 0.4s infinite alternate ease-in-out";
            } else if (tag.animType === "pulse") {
              animationStyle += ", emsPulse 0.8s infinite alternate ease-in-out";
            }
          }

          return (
            <div
              key={tag.id}
              style={
                {
                  position: "absolute",
                  top: `${tag.top}%`,
                  left: `${tag.left}%`,
                  background: theme.bg,
                  color: theme.text,
                  border: `2px solid ${theme.border}`,
                  padding: "8px 16px",
                  borderRadius: "8px",
                  fontWeight: 900,
                  fontSize: "15px",
                  letterSpacing: "1px",
                  boxShadow: "0 8px 16px rgba(0,0,0,0.35)",
                  textTransform: "uppercase",
                  whiteSpace: "nowrap",
                  fontFamily: "system-ui, -apple-system, sans-serif",
                  "--rot": `${tag.rotation}deg`,
                  "--scale": tag.scale,
                  animation: animationStyle,
                } as React.CSSProperties
              }
            >
              ⚠️ {tag.text}
            </div>
          );
        })}
      </div>
    </>
  );

  return typeof document !== "undefined"
    ? ReactDOM.createPortal(overlayContent, document.body)
    : null;
};
