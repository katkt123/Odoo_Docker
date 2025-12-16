odoo.define('estate.wishlist_interest', function (require) {
    'use strict';

    const rpc = require('@web/core/network/rpc').rpc;

    function addButtons() {
        document.querySelectorAll('.wishlist-section article[data-product-id]').forEach(function (article) {
            if (article.querySelector('.o_wish_interest')) {
                return;
            }
            const productId = article.dataset.productId || article.getAttribute('data-product-id');
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-outline-secondary o_wish_interest';
            btn.style.marginLeft = '8px';
            btn.textContent = 'Quan tâm';
            btn.addEventListener('click', function () {
                btn.disabled = true;
                rpc('/estate/wishlist/interest', {product_id: parseInt(productId, 10)})
                    .then(function (res) {
                        if (res && res.success) {
                            btn.textContent = 'Đã gửi';
                        } else {
                            btn.textContent = 'Lỗi';
                            btn.disabled = false;
                        }
                    })
                    .catch(function () {
                        btn.textContent = 'Lỗi';
                        btn.disabled = false;
                    });
            });
            // insert the button near existing action buttons
            const actionContainer = article.querySelector('.o_wish_buttons') || article.querySelector('.o_wish_action') || article.querySelector('.o_wish') || (article.querySelector('.o_wish_rm') && article.querySelector('.o_wish_rm').parentNode);
            if (actionContainer) {
                actionContainer.appendChild(btn);
            } else {
                // fallback: append to article
                article.appendChild(btn);
            }
        });
    }

    // Run on DOM ready and when wishlist updates (mutation observer)
    document.addEventListener('DOMContentLoaded', function () {
        addButtons();
        const target = document.querySelector('.wishlist-section');
        if (target) {
            const mo = new MutationObserver(function () { addButtons(); });
            mo.observe(target, {childList: true, subtree: true});
        }
    });

    return {
        addButtons: addButtons,
    };
});
