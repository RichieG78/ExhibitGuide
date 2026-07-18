// This script powers the dashboard filter pills.
// It hides and shows cards on the page instead of doing a full page reload.

const filterButtons = document.querySelectorAll('.filter-pill');
const cards = document.querySelectorAll('.artwork-card');
const emptyState = document.querySelector('[data-filter-empty]');

const emptyMessages = {
    all: 'No paintings to display yet.',
    scanned: 'No newly scanned painting yet. Scan a QR code to add one here.',
    watching: 'Nothing in your watchlist yet. Add a scanned painting to start watching.',
    enquired: 'No inquiries sent yet.',
    acquired: 'No acquired works yet.',
};

function applyFilter(filterValue) {
    // Count visible cards so we can show a friendly empty-state message when needed.
    let visibleCount = 0;

    cards.forEach((card) => {
        const status = card.getAttribute('data-status') || 'watching';
        const shouldShow = filterValue === 'all' || filterValue === status;
        card.classList.toggle('is-hidden', !shouldShow);
        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (emptyState) {
        const message = emptyMessages[filterValue] || emptyMessages.all;
        emptyState.textContent = message;
        emptyState.classList.toggle('is-hidden', visibleCount > 0);
    }
}

filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
        // Only one pill should look active at a time.
        filterButtons.forEach((item) => item.classList.remove('is-active'));
        button.classList.add('is-active');
        applyFilter(button.getAttribute('data-filter') || 'all');
    });
});

const activeButton = document.querySelector('.filter-pill.is-active');
const initialFilter = (activeButton && activeButton.getAttribute('data-filter')) || 'watching';

// Sync the first rendered screen with whichever pill the template marked as active.
applyFilter(initialFilter);

const enquiryToggles = document.querySelectorAll('[data-inquiry-toggle]');
const enquiryModal = document.querySelector('[data-inquiry-modal]');
const enquiryCloseButtons = document.querySelectorAll('[data-inquiry-close]');
const enquiryTitle = document.querySelector('[data-inquiry-title]');
const enquiryOwner = document.querySelector('[data-inquiry-owner]');
const enquiryExhibitInput = document.querySelector('[data-inquiry-exhibit]');
const enquiryMessageInput = document.querySelector('#inquiry-message');
const phoneMethodInputs = document.querySelectorAll('[data-phone-method]');
const phoneBlock = document.querySelector('[data-phone-block]');
const profileConsent = document.querySelector('[data-profile-consent]');
let lastEnquiryToggle = null;

const modalFocusableSelector = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'textarea:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
].join(',');

function updatePhoneBlockState() {
    if (!phoneBlock) {
        return;
    }

    const needsPhone = Array.from(phoneMethodInputs).some((input) => input.checked);
    phoneBlock.classList.toggle('is-hidden', !needsPhone);

    if (profileConsent) {
        // Only offer profile-save consent when phone/text details are relevant.
        profileConsent.disabled = !needsPhone;
        if (!needsPhone) {
            profileConsent.checked = false;
        }
    }
}

function openEnquiryModal(toggleButton) {
    if (!enquiryModal || !enquiryExhibitInput) {
        return;
    }

    lastEnquiryToggle = toggleButton;

    const exhibitId = toggleButton.getAttribute('data-exhibit-id') || '';
    const artworkTitle = toggleButton.getAttribute('data-artwork-title') || 'This Artwork';
    const galleryOwner = toggleButton.getAttribute('data-gallery-owner') || 'Gallery Owner';

    enquiryExhibitInput.value = exhibitId;
    if (enquiryTitle) {
        enquiryTitle.textContent = `Enquire About ${artworkTitle}`;
    }
    if (enquiryOwner) {
        enquiryOwner.textContent = galleryOwner;
    }
    if (enquiryMessageInput) {
        enquiryMessageInput.value = '';
    }

    updatePhoneBlockState();
    enquiryModal.classList.remove('is-hidden');
    enquiryModal.setAttribute('aria-hidden', 'false');

    if (enquiryMessageInput) {
        enquiryMessageInput.focus();
    }
}

function closeEnquiryModal() {
    if (!enquiryModal) {
        return;
    }

    enquiryModal.classList.add('is-hidden');
    enquiryModal.setAttribute('aria-hidden', 'true');

    if (lastEnquiryToggle) {
        lastEnquiryToggle.focus();
    }
}

function handleEnquiryModalKeyboard(event) {
    if (!enquiryModal || enquiryModal.classList.contains('is-hidden')) {
        return;
    }

    if (event.key === 'Escape') {
        event.preventDefault();
        closeEnquiryModal();
        return;
    }

    if (event.key !== 'Tab') {
        return;
    }

    const focusable = Array.from(enquiryModal.querySelectorAll(modalFocusableSelector)).filter((element) =>
        element.getClientRects().length > 0
    );

    if (focusable.length === 0) {
        return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
        return;
    }

    if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
}

enquiryToggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
        openEnquiryModal(toggle);
    });
});

enquiryCloseButtons.forEach((button) => {
    button.addEventListener('click', closeEnquiryModal);
});

phoneMethodInputs.forEach((input) => {
    input.addEventListener('change', updatePhoneBlockState);
});

document.addEventListener('keydown', handleEnquiryModalKeyboard);

updatePhoneBlockState();
