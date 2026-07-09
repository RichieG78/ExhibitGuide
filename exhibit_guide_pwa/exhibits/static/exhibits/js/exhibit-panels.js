// This script makes the exhibit page behave like a simple three-tab interface.
// Only one panel should be visible at a time, and Read is the default landing state.

const readButton = document.getElementById('read-button');
const readingPanel = document.getElementById('reading-panel');
const viewButton = document.getElementById('view-button');
const viewPanel = document.getElementById('view-panel');
const listenButton = document.getElementById('listen-button');
const listenPanel = document.getElementById('listen-panel');

const panels = [
    { button: readButton, panel: readingPanel },
    { button: listenButton, panel: listenPanel },
    { button: viewButton, panel: viewPanel },
].filter(({ button, panel }) => button && panel);

function activatePanel(activePanelId) {
    // Switch the active state on both the buttons and the content panels.
    panels.forEach(({ button, panel }) => {
        const isActive = panel.id === activePanelId;
        panel.classList.toggle('is-visible', isActive);
        button.classList.toggle('is-active', isActive);
        button.setAttribute('aria-expanded', String(isActive));
    });
}

panels.forEach(({ button, panel }) => {
    button.addEventListener('click', () => {
        activatePanel(panel.id);
    });
});

if (readingPanel) {
    // Visitors should land in Read first so the core exhibit information is visible immediately.
    activatePanel('reading-panel');
}
