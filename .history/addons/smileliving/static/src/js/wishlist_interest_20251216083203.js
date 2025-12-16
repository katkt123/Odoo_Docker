/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function replaceAddToCartWithInterest() {
    document.querySelectorAll('.wishlist-section article[data-product-id]').forEach((article) => {
        const productId = article.dataset.productId || article.getAttribute('data-product-id');
        if (!productId) {
            return;
        }

        // On the wishlist page Odoo uses `.o_wish_add` for the "Add to Cart" action.
        const addToCartEl = article.querySelector('.o_wish_add');
        if (!addToCartEl) {
            return;
        }
        if (addToCartEl.dataset.smilelivingInterestApplied === '1') {
            return;
        }

        // Remove Odoo's original click handler by cloning the node.
        const interestEl = addToCartEl.cloneNode(true);
        interestEl.dataset.smilelivingInterestApplied = '1';

        // Prevent Odoo wishlist interaction from rebinding to this element.
        interestEl.classList.remove('o_wish_add');
        interestEl.classList.add('o_wish_interest');

        // Replace label/icon with Interest
        interestEl.textContent = 'Interest';

        interestEl.addEventListener('click', async (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            interestEl.disabled = true;
            try {
                const res = await rpc('/shop/wishlist/interest', { product_id: parseInt(productId, 10) });
                if (res && res.success) {
                    interestEl.textContent = 'Sent';
                } else {
                    interestEl.textContent = 'Error';
                    interestEl.disabled = false;
                }
            } catch {
                interestEl.textContent = 'Error';
                interestEl.disabled = false;
            }
        }, { capture: true });

        addToCartEl.replaceWith(interestEl);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    replaceAddToCartWithInterest();
    const target = document.querySelector('.wishlist-section');
    if (target) {
        const mo = new MutationObserver(() => replaceAddToCartWithInterest());
        mo.observe(target, { childList: true, subtree: true });
    }
});

export { replaceAddToCartWithInterest };
