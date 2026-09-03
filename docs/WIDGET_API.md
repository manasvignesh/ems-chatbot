# Embeddable Widget API Reference

The **The Equinox 2.0 Assistant Widget** provides a clean JavaScript API on the global `window.EMSAssistant` object to control visibility, message transmission, and host page context synchronization.

---

## 1. Initialization: `init(options)`

Initializes the widget inside a shadow root attached to `document.body`.

```javascript
window.EMSAssistant.init({
  botId: 'ems',
  apiUrl: 'https://api.yourdomain.com', // Base URL of FastAPI backend
  position: 'bottom-right',             // 'bottom-right' | 'bottom-left'
  initialContext: {
    pageType: 'event',                  // 'portal' | 'event' | 'calendar' | 'registration'
    eventId: 'startup-poly',
    eventName: 'Startup Poly'
  }
});
```

---

## 2. Dynamic Context Synchronization: `setContext(context)`

Updates the active page context on single-page-app (SPA) route changes or modal open events:

```javascript
// On navigating to Startup Poly sub-event page
window.EMSAssistant.setContext({
  pageType: 'event',
  eventId: 'startup-poly',
  eventName: 'Startup Poly'
});

// On navigating back to Equinox Home
window.EMSAssistant.setContext({
  pageType: 'portal',
  eventId: 'equinox-2.0',
  eventName: 'The Equinox 2.0'
});
```

---

## 3. Programmatic Control Methods

### `open()`
Opens the floating chat window.

```javascript
window.EMSAssistant.open();
```

### `close()`
Closes the floating chat window.

```javascript
window.EMSAssistant.close();
```

### `toggle()`
Toggles the chat window open/close state.

```javascript
window.EMSAssistant.toggle();
```

### `sendMessage(text)`
Sends a message on behalf of the user and opens the chat window:

```javascript
window.EMSAssistant.sendMessage("Tell me about IPL Auction");
```
