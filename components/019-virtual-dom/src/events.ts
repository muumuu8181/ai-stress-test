/**
 * Simple event delegation system.
 * Attaches a single listener to the window/document for each event type.
 */

const eventHandlers = new Map<string, Map<Node, Function>>();

/**
 * Updates event listeners on a DOM element using delegation.
 */
export function updateEvents(el: HTMLElement | SVGElement, eventName: string, value: any, oldValue: any): void {
  if (!eventHandlers.has(eventName)) {
    eventHandlers.set(eventName, new Map());
    document.addEventListener(eventName, (event) => {
      let target = event.target as Node | null;
      const handlers = eventHandlers.get(eventName);
      if (!handlers) return;

      while (target) {
        const handler = handlers.get(target);
        if (handler) {
          handler(event);
          break; // Stop after first match for simple delegation
        }
        target = target.parentNode;
      }
    });
  }

  const handlers = eventHandlers.get(eventName)!;
  if (value) {
    handlers.set(el, value);
  } else {
    handlers.delete(el);
  }
}
