document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-wishlist]").forEach((button) => {
        button.addEventListener("click", () => {
            const icon = button.querySelector("i");
            const isSaved = button.classList.toggle("is-saved");
            button.setAttribute("aria-label", isSaved ? "Remove from wishlist" : button.getAttribute("aria-label").replace("Remove from wishlist", "Add to wishlist"));
            icon.classList.toggle("fa-regular", !isSaved);
            icon.classList.toggle("fa-solid", isSaved);
        });
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
            if (menu.classList.contains("show")) {
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
        const confirmationTitle = variantSelector.querySelector("[data-confirmation-title]");
        const confirmationSize = variantSelector.querySelector("[data-confirmation-size]");
        const confirmationColor = variantSelector.querySelector("[data-confirmation-color]");
        const confirmationPrice = variantSelector.querySelector("[data-confirmation-price]");
        const confirmationVariantId = variantSelector.querySelector("[data-confirmation-variant-id]");
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
                if (selectedSize && selectedSize.dataset.color !== selectedColor) {
                    clearSizeSelection();
                }
                selectionError.textContent = "";
                selectionConfirmation.hidden = true;
            });
        });

        sizeOptions.forEach((option) => {
            option.addEventListener("click", () => {
                if (option.disabled || option.hidden) return;
                sizeOptions.forEach((sizeOption) => sizeOption.classList.toggle("is-selected", sizeOption === option));
                selectedVariantInput.value = option.dataset.variantId;
                stockRows.forEach((row) => row.classList.toggle("is-selected", row.dataset.variantId === option.dataset.variantId));
                selectionMessage.textContent = `${option.dataset.size}${option.dataset.color ? ` · ${option.dataset.color}` : ""} selected · ${option.dataset.stock} available`;
                selectionError.textContent = "";
                selectionConfirmation.hidden = true;
            });
        });

        variantSelector.addEventListener("submit", (event) => {
            event.preventDefault();
            const selectedOption = sizeOptions.find((option) => option.dataset.variantId === selectedVariantInput.value);
            const validSelection = selectedOption
                && selectedOption.dataset.productId === variantSelector.dataset.productId
                && !selectedOption.disabled
                && Number(selectedOption.dataset.stock) > 0;
            if (!validSelection) {
                selectionError.textContent = "Please select your shoe size.";
                selectionConfirmation.hidden = true;
                const firstAvailable = sizeOptions.find((option) => !option.disabled && !option.hidden);
                if (firstAvailable) firstAvailable.focus();
                return;
            }
            selectionError.textContent = "";
            variantSelector.method = "post";
            variantSelector.action = variantSelector.dataset.checkoutAction || "/checkout";
            HTMLFormElement.prototype.submit.call(variantSelector);
        });

        applyColorFilter();
    }
});
