/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function addButtons() {
    document.querySelectorAll('.wishlist-section article[data-product-id]').forEach((article) => {
        if (article.querySelector('.o_wish_interest')) {
            return;
        }
        const productId = article.dataset.productId || article.getAttribute('data-product-id');
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-secondary o_wish_interest';
        btn.style.marginLeft = '8px';
        btn.textContent = 'Quan tâm';
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
                const res = await rpc('/smileliving/wishlist/interest', { product_id: parseInt(productId, 10) });
                if (res && res.success) {
                    btn.textContent = 'Đã gửi';
                } else {
                    btn.textContent = 'Lỗi';
                    btn.disabled = false;
                }
            } catch {
                btn.textContent = 'Lỗi';
                btn.disabled = false;
            }
        });

        const actionContainer = article.querySelector('.o_wish_buttons')
            || article.querySelector('.o_wish_action')
            || article.querySelector('.o_wish')
            || (article.querySelector('.o_wish_rm') && article.querySelector('.o_wish_rm').parentNode);

        if (actionContainer) {
            actionContainer.appendChild(btn);
        } else {
            article.appendChild(btn);
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    addButtons();
    const target = document.querySelector('.wishlist-section');
    if (target) {
        const mo = new MutationObserver(() => addButtons());
        mo.observe(target, { childList: true, subtree: true });
    }
});

export { addButtons };
