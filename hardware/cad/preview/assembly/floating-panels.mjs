const clamp = (value, minimum, maximum) => Math.min(Math.max(value, minimum), maximum);

export function installFloatingPanels(container, { persist = false } = {}) {
  const panels = [...container.querySelectorAll(".floating-panel")];
  const storageKey = `scad-assembly-web-preview:panels:${location.pathname}`;
  let saved = {};
  if (persist) {
    try { saved = JSON.parse(localStorage.getItem(storageKey) || "{}"); }
    catch { saved = {}; }
  }
  const place = (panel, x, y) => {
    panel.style.left = `${clamp(x, 0, Math.max(0, container.clientWidth - panel.offsetWidth))}px`;
    panel.style.top = `${clamp(y, 0, Math.max(0, container.clientHeight - panel.offsetHeight))}px`;
    panel.style.right = "auto";
    panel.style.bottom = "auto";
  };
  const save = () => {
    if (!persist) return;
    const state = Object.fromEntries(panels.map((panel) => [panel.id, {
      x: panel.offsetLeft,
      y: panel.offsetTop,
      collapsed: panel.classList.contains("is-collapsed"),
    }]));
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch { /* Storage may be disabled; panel controls still work. */ }
  };
  for (const panel of panels) {
    const heading = panel.querySelector("[data-drag-handle]");
    const toggle = panel.querySelector("[data-collapse]");
    const content = panel.querySelector(".panel-content");
    const panelName = panel.dataset.panelLabel || panel.querySelector("h1, h2")?.textContent || "控制";
    const prior = saved?.[panel.id];
    const collapse = (collapsed, persistChange = true) => {
      panel.classList.toggle("is-collapsed", collapsed);
      content.hidden = collapsed;
      toggle.textContent = collapsed ? "+" : "−";
      toggle.setAttribute("aria-expanded", String(!collapsed));
      toggle.setAttribute("aria-label", `${collapsed ? "展开" : "折叠"}${panelName}面板`);
      place(panel, panel.offsetLeft, panel.offsetTop);
      if (persistChange) save();
    };
    if (typeof prior?.collapsed === "boolean") collapse(prior.collapsed, false);
    if (Number.isFinite(prior?.x) && Number.isFinite(prior?.y)) place(panel, prior.x, prior.y);
    toggle.addEventListener("click", () => collapse(!content.hidden));

    let dragging = null;
    heading.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || event.target.closest("button")) return;
      dragging = { id: event.pointerId, x: event.clientX, y: event.clientY,
        left: panel.offsetLeft, top: panel.offsetTop };
      panel.style.zIndex = "3";
      heading.setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    heading.addEventListener("pointermove", (event) => {
      if (!dragging || dragging.id !== event.pointerId) return;
      place(panel, dragging.left + event.clientX - dragging.x,
        dragging.top + event.clientY - dragging.y);
    });
    const stop = (event) => {
      if (!dragging || dragging.id !== event.pointerId) return;
      dragging = null;
      panel.style.zIndex = "";
      save();
    };
    heading.addEventListener("pointerup", stop);
    heading.addEventListener("pointercancel", stop);
    heading.addEventListener("keydown", (event) => {
      if (event.target !== heading) return;
      const direction = { ArrowLeft: [-1, 0], ArrowRight: [1, 0],
        ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
      if (!direction) return;
      const step = event.shiftKey ? 20 : 10;
      place(panel, panel.offsetLeft + direction[0] * step,
        panel.offsetTop + direction[1] * step);
      save();
      event.preventDefault();
    });
  }
  new ResizeObserver(() => {
    for (const panel of panels) place(panel, panel.offsetLeft, panel.offsetTop);
    save();
  }).observe(container);
}
