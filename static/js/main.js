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
                alert(data.message);
                loadExpenses();
            })
            .catch(error => console.error('Error:', error));
        });
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
        expensesContainer.innerHTML = '';
        expenses.forEach(expense => {
            const expenseElement = document.createElement('div');
            expenseElement.classList.add('expense-item', 'mb-3', 'p-3', 'border', 'rounded');
            expenseElement.innerHTML = `
                <h5>${expense.store_name}</h5>
                <p>Date: ${expense.date}</p>
                <p>Total: $${expense.total_amount.toFixed(2)}</p>
                <p>Category: ${expense.category}</p>
                <h6>Items:</h6>
                <ul>
                    ${expense.items.map(item => `<li>${item.name} - $${item.price.toFixed(2)} (${item.category})</li>`).join('')}
                </ul>
            `;
            expensesContainer.appendChild(expenseElement);
        });
    }

    function createChart(expenses) {
        const ctx = document.getElementById('expenses-chart').getContext('2d');
        
        // Prepare data for chart
        const categories = [...new Set(expenses.map(e => e.category))];
        const data = categories.map(category => {
            return expenses.filter(e => e.category === category)
                           .reduce((sum, e) => sum + e.total_amount, 0);
        });

        new Chart(ctx, {
            type: 'pie',
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
                title: {
                    display: true,
                    text: 'Expenses by Category'
                }
            }
        });
    }

    // Load expenses on page load if the container exists
    if (expensesContainer || chartContainer) {
        loadExpenses();
    }
});
