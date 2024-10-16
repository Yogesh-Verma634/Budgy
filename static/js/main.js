document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const expensesContainer = document.getElementById('expenses-container');
    const chartContainer = document.getElementById('chart-container');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            
            fetch('/upload_receipt', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert('error', data.error);
                } else {
                    showAlert('success', data.message);
                    if (data.data) {
                        displayReceiptData(data.data);
                    }
                    loadExpenses();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'An error occurred while uploading the receipt. Please try again.');
            });
        });
    }

    function showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertContainer.role = 'alert';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertContainer, container.firstChild);
            
            // Auto-dismiss the alert after 5 seconds
            setTimeout(() => {
                alertContainer.remove();
            }, 5000);
        }
    }

    function displayReceiptData(data) {
        const receiptDataContainer = document.getElementById('receipt-data');
        if (receiptDataContainer) {
            receiptDataContainer.innerHTML = `
                <h3>Processed Receipt Data</h3>
                <p><strong>Store:</strong> ${data.store_name}</p>
                <p><strong>Total Amount:</strong> $${data.total_amount.toFixed(2)}</p>
                <p><strong>Category:</strong> ${data.category}</p>
                <h4>Items:</h4>
                <ul>
                    ${data.items.map(item => `
                        <li>${item.name} - $${item.price.toFixed(2)} (${item.category})</li>
                    `).join('')}
                </ul>
            `;
        }
    }

    function loadExpenses() {
        console.log('Loading expenses...');
        fetch('/get_expenses')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(expenses => {
                console.log('Expenses loaded:', expenses);
                if (expenses.error) {
                    throw new Error(expenses.error);
                }
                if (!Array.isArray(expenses)) {
                    throw new Error('Received data is not an array');
                }
                if (expensesContainer) {
                    displayExpenses(expenses);
                }
                if (chartContainer) {
                    createChart(expenses);
                }
            })
            .catch(error => {
                console.error('Error loading expenses:', error);
                showAlert('error', `An error occurred while loading expenses: ${error.message}`);
            });
    }

    function displayExpenses(expenses) {
        if (!expensesContainer) {
            console.error('Expenses container not found');
            return;
        }
        
        console.log('Displaying expenses:', expenses);
        expensesContainer.innerHTML = '';
        if (expenses.length === 0) {
            expensesContainer.innerHTML = '<p>No expenses found.</p>';
            return;
        }
        expenses.forEach(expense => {
            const expenseElement = document.createElement('div');
            expenseElement.classList.add('expense-item', 'card', 'mb-3');
            expenseElement.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${expense.store_name}</h5>
                    <p class="card-text">Date: ${expense.date}</p>
                    <p class="card-text">Total: $${expense.total_amount.toFixed(2)}</p>
                    <p class="card-text">Category: ${expense.category}</p>
                    <h6 class="card-subtitle mb-2 text-muted">Items:</h6>
                    <ul class="list-group list-group-flush">
                        ${expense.items.map(item => `<li class="list-group-item">${item.name} - $${item.price.toFixed(2)} (${item.category})</li>`).join('')}
                    </ul>
                </div>
            `;
            expensesContainer.appendChild(expenseElement);
        });
    }

    function createChart(expenses) {
        if (!chartContainer) {
            console.error('Chart container not found');
            return;
        }

        const ctx = document.getElementById('expenses-chart');
        if (!ctx) {
            console.error('Expenses chart canvas not found');
            return;
        }

        const ctxCanvas = ctx.getContext('2d');
        
        // Prepare data for chart
        const categories = [...new Set(expenses.map(e => e.category))];
        const data = categories.map(category => {
            return expenses.filter(e => e.category === category)
                           .reduce((sum, e) => sum + e.total_amount, 0);
        });

        console.log('Creating chart with data:', { categories, data });

        new Chart(ctxCanvas, {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Expenses by Category'
                    }
                }
            }
        });
    }

    // Load expenses on page load if the container exists
    if (expensesContainer || chartContainer) {
        console.log('Initializing expense loading...');
        loadExpenses();
    } else {
        console.log('Expenses or chart container not found. Current page might not require expense data.');
    }
});
