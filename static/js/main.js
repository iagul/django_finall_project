document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.add-to-cart-btn');
  const cartTotalSpan = document.getElementById('cart-total');

  const toastContainer = document.createElement('div');
  toastContainer.style.position = 'fixed';
  toastContainer.style.bottom = '20px';
  toastContainer.style.right = '20px';
  toastContainer.style.zIndex = '9999';
  document.body.appendChild(toastContainer);

  // Add to cart buttons
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const productId = button.dataset.productId;
      const productName = button.dataset.productName || 'Product';
      const productImage = button.dataset.productImage || '';

      fetch('/store/add-to-cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ productId: productId, quantity: 1 }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          if (cartTotalSpan && typeof data.cartItemCount === 'number') {
            cartTotalSpan.textContent = data.cartItemCount;
          } else {
            location.reload();
          }
          showToast(productName, productImage);
        } else {
          showToast('Error adding to cart: ' + (data.error || 'Unknown error.'), '', true);
        }
      })
      .catch(() => showToast('Failed to add to cart.', '', true));
    });
  });

  // Quantity update buttons
  document.querySelectorAll('.btn-add, .btn-remove').forEach(button => {
    button.addEventListener('click', () => {
      const row = button.closest('.cart-item-row');
      if (!row) {
        console.warn('Cart item row not found!');
        return;
      }

      const itemId = row.dataset.itemId;
      const qtyElem = row.querySelector('.qty');
      const priceElem = row.querySelector('.price');
      const unitPriceStr = row.dataset.unitPrice;

      // Debugging logs:
      console.log('Row data-item-id:', itemId);
      console.log('Unit price string:', unitPriceStr);

      if (!unitPriceStr) {
        console.error('Unit price data attribute missing or empty!');
        return;
      }

      const unitPrice = parseFloat(unitPriceStr);
      if (isNaN(unitPrice)) {
        console.error('Unit price is NaN:', unitPriceStr);
        return;
      }

      const action = button.classList.contains('btn-add') ? 'add' : 'remove';

      fetch('/store/cart/update_item/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ itemId: itemId, action: action }),
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (data.deleted) {
            row.remove();
          } else {
            // Update quantity UI
            if (qtyElem.tagName === 'INPUT') {
              qtyElem.value = data.new_quantity;
            } else {
              qtyElem.textContent = data.new_quantity;
            }

            // Update price UI (qty * unit price)
            if (priceElem) {
              const newPrice = unitPrice * data.new_quantity;
              priceElem.textContent = '$' + newPrice.toFixed(2);
            } else {
              console.warn('Price element not found in row!');
            }
          }
          updateCartTotal();
        } else {
          showToast('Error updating cart.', '', true);
        }
      })
      .catch(() => showToast('Failed to update cart.', '', true));
    });
  });

  // Update total cart price by summing all row prices
  function updateCartTotal() {
    let total = 0;
    document.querySelectorAll('.cart-item-row').forEach(row => {
      const priceElem = row.querySelector('.price');
      if (!priceElem) return;

      let priceText = priceElem.textContent || '0';
      let price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
      if (!isNaN(price)) {
        total += price;
      }
    });

    if (cartTotalSpan) {
      cartTotalSpan.textContent = '$' + total.toFixed(2);
    }
  }

  function showToast(message, imgSrc = '', isError = false) {
    const toast = document.createElement('div');
    toast.style.minWidth = '250px';
    toast.style.marginBottom = '10px';
    toast.style.padding = '10px 15px';
    toast.style.borderRadius = '8px';
    toast.style.color = isError ? '#fff' : '#333';
    toast.style.backgroundColor = isError ? '#e74c3c' : '#ecf0f1';
    toast.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.fontFamily = 'Arial, sans-serif';
    toast.style.fontSize = '14px';

    if (!isError && imgSrc) {
      const img = document.createElement('img');
      img.src = imgSrc;
      img.alt = message;
      img.style.width = '40px';
      img.style.height = '40px';
      img.style.objectFit = 'cover';
      img.style.marginRight = '10px';
      img.style.borderRadius = '4px';
      toast.appendChild(img);
    }

    const msgSpan = document.createElement('span');
    msgSpan.textContent = isError ? message : `${message} added to cart!`;
    toast.appendChild(msgSpan);

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.5s ease';
      setTimeout(() => toast.remove(), 500);
    }, 3000);
  }
});

// Helper to get CSRF token cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      const cookie = c.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

 