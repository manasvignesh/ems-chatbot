# JavaScript Widget API Reference

The EMS Assistant embed widget exposes a global `window.EMSAssistant` object that provides programmatic control over the chatbot lifecycle, state, and page context.

---

## Global Object: `window.EMSAssistant`

### 1. `init(options?: WidgetInitOptions)`
Manually initializes the widget inside an open Shadow DOM root attached to `document.body`. (Note: If `data-auto-init="true"` is set on the script tag, initialization happens automatically upon DOM ready).

```javascript
window.EMSAssistant.init({
  apiUrl: "https://assistant.ems.mlritcie.in",
  botId: "ems",
  initialContext: {
    pageType: "home",
    pathname: "/"
  }
});
```

---

### 2. `open()`
Programmatically opens the chat panel.

```javascript
window.EMSAssistant.open();
```

---

### 3. `close()`
Programmatically closes the chat panel, returning to the floating launcher button.

```javascript
window.EMSAssistant.close();
```

---

### 4. `toggle()`
Toggles the open/closed state of the chat panel.

```javascript
window.EMSAssistant.toggle();
```

---

### 5. `setContext(context: PageContext)`
Updates the active page context sent alongside all subsequent user queries.

```javascript
window.EMSAssistant.setContext({
  pageType: "event",
  eventId: "hackverse-2026",
  eventName: "HackVerse 2026",
  pathname: window.location.pathname
});
```

---

### 6. `resetConversation()`
Clears the active conversation history in the widget and initiates a new session ID.

```javascript
window.EMSAssistant.resetConversation();
```

---

### 7. `destroy()`
Unmounts the React root, removes the Shadow DOM container, and cleans up all listeners and timers.

```javascript
window.EMSAssistant.destroy();
```
