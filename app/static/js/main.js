document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-product-image]").forEach((image) => {
        image.addEventListener("error", () => {
            console.warn("STEPZONE product image could not be loaded:", image.currentSrc || image.src);
            image.hidden = true;
            const fallback = image.parentElement.querySelector("[data-image-fallback]");
            if (fallback) fallback.hidden = false;
        }, { once: true });
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.getAttribute("aria-controls"));
            if (!input) return;
            const reveal = input.type === "password";
            input.type = reveal ? "text" : "password";
            button.textContent = reveal ? "Hide" : "Show";
            button.setAttribute("aria-pressed", reveal ? "true" : "false");
        });
    });

    document.querySelectorAll("[data-password-form]").forEach((form) => {
        const password = form.querySelector('input[name="password"]');
        const confirmation = form.querySelector("[data-password-confirm]");
        const message = form.querySelector("[data-password-message]");
        if (!password || !confirmation) return;
        const validate = () => {
            const matches = password.value === confirmation.value;
            confirmation.setCustomValidity(matches ? "" : "Passwords do not match.");
            if (message) {
                message.textContent = matches || !confirmation.value ? "" : "Passwords do not match.";
                message.classList.toggle("is-error", !matches && Boolean(confirmation.value));
            }
        };
        password.addEventListener("input", validate);
        confirmation.addEventListener("input", validate);
        form.addEventListener("submit", validate);
    });

    const newsletterForm = document.querySelector("[data-newsletter-form]");
    const formMessage = document.querySelector("[data-form-message]");
    if (newsletterForm && formMessage) {
        newsletterForm.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!newsletterForm.checkValidity()) {
                formMessage.textContent = "Please enter a valid email address.";
                formMessage.classList.add("is-error");
                newsletterForm.querySelector("input").focus();
                return;
            }
            formMessage.textContent = "You're in. Watch your inbox for the next drop.";
            formMessage.classList.remove("is-error");
            newsletterForm.reset();
        });
    }

    document.querySelectorAll(".nav-link, .navbar-collapse a").forEach((link) => {
        link.addEventListener("click", () => {
            const menu = document.querySelector("#mainNav");
            if (menu && menu.classList.contains("show")) {
                bootstrap.Collapse.getOrCreateInstance(menu).hide();
            }
        });
    });

    const variantSelector = document.querySelector("[data-variant-selector]");
    if (variantSelector) {
        const selectedVariantInput = variantSelector.querySelector("[data-selected-variant]");
        const selectionMessage = variantSelector.querySelector("[data-selection-message]");
        const selectionError = variantSelector.querySelector("[data-selection-error]");
        const selectionConfirmation = variantSelector.querySelector("[data-selection-confirmation]");
        const sizeOptions = [...variantSelector.querySelectorAll("[data-size-option]")];
        const colorOptions = [...variantSelector.querySelectorAll("[data-color-option]")];
        const stockRows = [...variantSelector.querySelectorAll("[data-stock-row]")];
        let selectedColor = "";

        const clearSizeSelection = () => {
            sizeOptions.forEach((option) => option.classList.remove("is-selected"));
            selectedVariantInput.value = "";
            stockRows.forEach((row) => row.classList.remove("is-selected"));
            selectionMessage.textContent = "Choose a size to see its stock availability.";
        };

        const applyColorFilter = () => {
            sizeOptions.forEach((option) => {
                const matchesColor = !selectedColor || option.dataset.color === selectedColor;
                option.hidden = !matchesColor;
            });
        };

        colorOptions.forEach((option) => {
            option.addEventListener("click", () => {
                selectedColor = option.dataset.color;
                colorOptions.forEach((colorOption) => colorOption.classList.toggle("is-selected", colorOption === option));
                applyColorFilter();
                const selectedSize = sizeOptions.find((sizeOption) => sizeOption.classList.contains("is-selected"));
                if (selectedSize && selectedSize.dataset.color !== selectedColor) clearSizeSelection();
                selectionError.textContent = "";
                if (selectionConfirmation) selectionConfirmation.hidden = true;
            });
        });

        sizeOptions.forEach((option) => {
            option.addEventListener("click", () => {
                if (option.disabled || option.hidden) return;
                sizeOptions.forEach((sizeOption) => sizeOption.classList.toggle("is-selected", sizeOption === option));
                selectedVariantInput.value = option.dataset.variantId;
                stockRows.forEach((row) => row.classList.toggle("is-selected", row.dataset.variantId === option.dataset.variantId));
                selectionMessage.textContent = option.dataset.size + (option.dataset.color ? " · " + option.dataset.color : "") + " selected · " + option.dataset.stock + " available";
                selectionError.textContent = "";
                if (selectionConfirmation) selectionConfirmation.hidden = true;
            });
        });

        variantSelector.addEventListener("submit", (event) => {
            const selectedOption = sizeOptions.find((option) => option.dataset.variantId === selectedVariantInput.value);
            const validSelection = selectedOption
                && selectedOption.dataset.productId === variantSelector.dataset.productId
                && !selectedOption.disabled
                && Number(selectedOption.dataset.stock) > 0;
            if (!validSelection) {
                event.preventDefault();
                selectionError.textContent = "Please select your shoe size.";
                if (selectionConfirmation) selectionConfirmation.hidden = true;
                const firstAvailable = sizeOptions.find((option) => !option.disabled && !option.hidden);
                if (firstAvailable) firstAvailable.focus();
            }
        });

        applyColorFilter();
        const requestedVariant = sizeOptions.find((option) => option.dataset.requested === "true");
        if (requestedVariant) requestedVariant.click();
    }
});
