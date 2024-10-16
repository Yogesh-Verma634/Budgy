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
        document.querySelector('.container').insertBefore(alertContainer, document.querySelector('.container').firstChild);
        
        // Auto-dismiss the alert after 5 seconds
        setTimeout(() => {
            alertContainer.remove();
        }, 5000);
    }

    function loadExpenses() {
        fetch('/get_expenses')
            .then(response => response.json())
            .then(expenses => {
                if (expensesContainer) {
                    displayExpenses(expenses);
                }
                if (chartContainer) {
                    createChart(expenses);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function displayExpenses(expenses) {
        if (!expensesContainer) return;
        
        expensesContainer.innerHTML = '';
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
        if (!chartContainer) return;

        const ctx = document.getElementById('expenses-chart').getContext('2d');
        
        // Prepare data for chart
        const categories = [...new Set(expenses.map(e => e.category))];
        const data = categories.map(category => {
            return expenses.filter(e => e.category === category)
                           .reduce((sum, e) => sum + e.total_amount, 0);
        });

        new Chart(ctx, {
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
        loadExpenses();
    }
});
