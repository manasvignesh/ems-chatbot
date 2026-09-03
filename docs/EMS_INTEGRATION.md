# EMS Website Integration Guide

This guide provides exact, copy-paste instructions for embedding the **EMS Assistant** chatbot into the official MLRIT CIE Event Management System (EMS) website without modifying EMS business logic or backend code.

---

## 1. Quick Integration via Standard Script Tag

Place this script tag immediately before the closing `</body>` tag of your site's root template:

```html
<!-- EMS Assistant AI Chatbot Widget -->
<script
  src="https://assistant.ems.mlritcie.in/widget/widget.js"
  data-api-url="https://assistant.ems.mlritcie.in"
  data-bot-id="ems"
  data-auto-init="true"
  defer
></script>
```

---

## 2. Integration in Next.js (App Router)

In your Next.js EMS repository (e.g. `app/layout.tsx`):

```tsx
import Script from 'next/script';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}

        {/* EMS Assistant Embed Script */}
        <Script
          src="https://assistant.ems.mlritcie.in/widget/widget.js"
          data-api-url="https://assistant.ems.mlritcie.in"
          data-bot-id="ems"
          data-auto-init="true"
          strategy="lazyOnload"
        />
      </body>
    </html>
  );
}
```

---

## 3. Dynamic Page Context on Event Detail Pages

On event detail pages (e.g. `app/events/[id]/page.tsx`), notify the assistant of the current event so users can ask contextual questions like *"What is the team size?"* without repeating the event name:

```tsx
'use client';

import { useEffect } from 'react';

declare global {
  interface Window {
    EMSAssistant?: {
      setContext: (ctx: {
        pageType: string;
        eventId: string;
        eventName?: string;
        pathname?: string;
      }) => void;
    };
  }
}

export default function EventDetailPage({ event }: { event: any }) {
  useEffect(() => {
    if (window.EMSAssistant) {
      window.EMSAssistant.setContext({
        pageType: 'event',
        eventId: event.id || event.slug,
        eventName: event.title,
        pathname: window.location.pathname,
      });
    }
  }, [event]);

  return (
    <main>
      <h1>{event.title}</h1>
      {/* Event Details */}
    </main>
  );
}
```

---

## 4. CORS Configuration

In the chatbot's `.env` file, ensure your EMS domains are whitelisted:

```env
ALLOWED_WIDGET_ORIGINS='["https://ems.mlritcie.in", "https://staging.ems.mlritcie.in", "http://localhost:3000"]'
```

---

## 5. Automatic Event Sync Webhook (Optional)

When an event is published or updated in EMS, you can optionally notify the chatbot backend to synchronize immediately:

```bash
curl -X POST "https://assistant.ems.mlritcie.in/api/sync/ems?bot_id=ems"
```
