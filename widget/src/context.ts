import { PageContext } from "./types";

class PageContextManager {
  private currentContext: PageContext = {
    pageType: "home",
    pathname: typeof window !== "undefined" ? window.location.pathname : "/",
  };

  private listeners: Array<(ctx: PageContext) => void> = [];

  setContext(context: Partial<PageContext>) {
    this.currentContext = {
      ...this.currentContext,
      ...context,
      pathname: typeof window !== "undefined" ? window.location.pathname : "/",
    };
    this.notify();
  }

  getContext(): PageContext {
    return { ...this.currentContext };
  }

  subscribe(listener: (ctx: PageContext) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private notify() {
    for (const listener of this.listeners) {
      try {
        listener(this.currentContext);
      } catch (e) {
        console.error("[EMS Assistant] Context listener error:", e);
      }
    }
  }
}

export const pageContextManager = new PageContextManager();
