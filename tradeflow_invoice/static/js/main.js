/**
 * TradeFlow Invoice - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('[role="alert"]');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Dark mode toggle (if settings page)
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
    }

    // Invoice item calculations
    const quantityInputs = document.querySelectorAll('.item-quantity');
    const priceInputs = document.querySelectorAll('.item-price');
    
    [quantityInputs, priceInputs].forEach(inputs => {
        inputs.forEach(input => {
            input.addEventListener('input', calculateLineItem);
        });
    });

    function calculateLineItem() {
        const row = this.closest('tr');
        const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
        const price = parseFloat(row.querySelector('.item-price').value) || 0;
        const amountField = row.querySelector('.item-amount');
        
        if (amountField) {
            amountField.value = (quantity * price).toFixed(2);
        }
        
        calculateInvoiceTotals();
    }

    function calculateInvoiceTotals() {
        let subtotal = 0;
        document.querySelectorAll('.item-amount').forEach(field => {
            subtotal += parseFloat(field.value) || 0;
        });

        const taxRate = parseFloat(document.querySelector('#tax-rate')?.value) || 0;
        const discount = parseFloat(document.querySelector('#discount-amount')?.value) || 0;
        
        const taxAmount = subtotal * (taxRate / 100);
        const total = subtotal + taxAmount - discount;

        const subtotalField = document.getElementById('subtotal-display');
        const taxField = document.getElementById('tax-display');
        const totalField = document.getElementById('total-display');

        if (subtotalField) subtotalField.textContent = `$${subtotal.toFixed(2)}`;
        if (taxField) taxField.textContent = `$${taxAmount.toFixed(2)}`;
        if (totalField) totalField.textContent = `$${total.toFixed(2)}`;
    }

    // Add invoice item dynamically
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const tbody = document.querySelector('#invoice-items tbody');
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><input type="text" name="description[]" class="w-full" placeholder="Description" required></td>
                <td><input type="number" name="quantity[]" class="item-quantity w-full" value="1" step="0.01" min="0"></td>
                <td><input type="number" name="unit_price[]" class="item-price w-full" value="0" step="0.01" min="0"></td>
                <td><input type="number" name="amount[]" class="item-amount w-full" value="0" step="0.01" readonly></td>
                <td><button type="button" class="remove-item text-red-600 hover:text-red-800">Remove</button></td>
            `;
            tbody.appendChild(newRow);
            
            // Add event listeners to new inputs
            newRow.querySelector('.item-quantity').addEventListener('input', calculateLineItem);
            newRow.querySelector('.item-price').addEventListener('input', calculateLineItem);
            newRow.querySelector('.remove-item').addEventListener('click', function() {
                newRow.remove();
                calculateInvoiceTotals();
            });
        });
    }

    // Remove item buttons
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('tr').remove();
            calculateInvoiceTotals();
        });
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.closest('form').submit();
            }, 500);
        });
    }

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const preview = this.parentElement.querySelector('.file-preview');
                if (preview) {
                    preview.textContent = file.name;
                    preview.classList.remove('hidden');
                }
            }
        });
    });

    // Print invoice
    const printBtn = document.getElementById('print-invoice');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }

    // Chart initialization helper
    window.initChart = function(canvasId, type, labels, data, label) {
        const ctx = document.getElementById(canvasId);
        if (ctx) {
            new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: data,
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.5)',
                            'rgba(16, 185, 129, 0.5)',
                            'rgba(245, 158, 11, 0.5)',
                            'rgba(239, 68, 68, 0.5)',
                            'rgba(139, 92, 246, 0.5)',
                        ],
                        borderColor: [
                            'rgb(59, 130, 246)',
                            'rgb(16, 185, 129)',
                            'rgb(245, 158, 11)',
                            'rgb(239, 68, 68)',
                            'rgb(139, 92, 246)',
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        }
    };

    // Format currency
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    // Format date
    window.formatDate = function(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    console.log('TradeFlow Invoice loaded successfully!');
});
