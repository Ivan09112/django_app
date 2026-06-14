let expenseChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    setupCategoryFilter();
    setupFormSubmit();
});

// Получить CSRF Токен
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Инициализация Chart.js
function initChart() {
    const canvas = document.getElementById('expenseChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Собираем категории расходов из существующей таблицы
    const categoriesData = getCategoriesSummary();

    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoriesData.labels,
            datasets: [{
                data: categoriesData.values,
                backgroundColor: categoriesData.colors,
                borderWidth: 1,
                borderColor: 'rgba(255, 255, 255, 0.08)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94A3B8',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

// Извлечение расходов по категориям из таблицы для графика
function getCategoriesSummary() {
    const rows = document.querySelectorAll('#transaction-list-body tr:not(#empty-row)');
    const summary = {};
    
    rows.forEach(row => {
        const typeCell = row.cells[3].innerText.trim();
        // Нам нужны только Expenses (расходы) для диаграммы распределения трат
        if (typeCell === 'Expense') {
            const categoryBadge = row.querySelector('.category-badge');
            const catName = categoryBadge.innerText.trim();
            const color = categoryBadge.style.color; // берем HEX/RGB сохраненный
            
            // Чистим сумму от знаков минус и баксов
            const amountText = row.cells[4].innerText.replace('-$', '').replace('$', '').trim();
            const amount = parseFloat(amountText);
            
            if (summary[catName]) {
                summary[catName].value += amount;
            } else {
                summary[catName] = {
                    value: amount,
                    color: color
                };
            }
        }
    });

    const labels = Object.keys(summary);
    const values = labels.map(l => summary[l].value);
    const colors = labels.map(l => summary[l].color);

    return { labels, values, colors };
}

// Обновление графика
function updateChart() {
    if (!expenseChart) return;
    const summary = getCategoriesSummary();
    expenseChart.data.labels = summary.labels;
    expenseChart.data.datasets[0].data = summary.values;
    expenseChart.data.datasets[0].backgroundColor = summary.colors;
    expenseChart.update();
}

// Фильтр категорий в форме в зависимости от выбранного типа (доход/расход)
function setupCategoryFilter() {
    const typeSelect = document.getElementById('tx-type');
    const catSelect = document.getElementById('tx-category');
    if (!typeSelect || !catSelect) return;
    
    const filterCategories = () => {
        const selectedType = typeSelect.value;
        const options = catSelect.querySelectorAll('option');
        let firstVisibleSet = false;
        
        options.forEach(opt => {
            const catType = opt.getAttribute('data-type');
            if (catType === selectedType) {
                opt.style.display = 'block';
                if (!firstVisibleSet) {
                    opt.selected = true;
                    firstVisibleSet = true;
                }
            } else {
                opt.style.display = 'none';
            }
        });
    };
    
    typeSelect.addEventListener('change', filterCategories);
    filterCategories(); // Запуск при загрузке
}

// Обработка отправки формы добавления транзакции
function setupFormSubmit() {
    const form = document.getElementById('add-transaction-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const csrfToken = getCookie('csrftoken');
        
        fetch('/api/transaction/add/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                form.reset();
                // Фильтруем категории заново
                document.getElementById('tx-type').dispatchEvent(new Event('change'));
                
                // Обновляем статистику баланса
                updateStats(data.stats);
                
                // Добавляем строку в таблицу
                addTransactionToTable(data.transaction);
                
                // Обновляем график
                updateChart();
            } else {
                alert('Error adding transaction: ' + data.message);
            }
        })
        .catch(err => {
            console.error('API Error:', err);
            alert('Something went wrong. Please try again.');
        });
    });
}

// Добавление строки в DOM
function addTransactionToTable(tx) {
    const body = document.getElementById('transaction-list-body');
    if (!body) return;
    
    const emptyRow = document.getElementById('empty-row');
    if (emptyRow) {
        emptyRow.remove();
    }
    
    const tr = document.createElement('tr');
    tr.id = `tx-row-${tx.id}`;
    
    const isIncome = tx.type === 'INCOME';
    const amountClass = isIncome ? 'amount-income' : 'amount-expense';
    const amountSign = isIncome ? '+' : '-';
    const typeLabel = isIncome ? 'Income' : 'Expense';
    
    tr.innerHTML = `
        <td>${tx.date}</td>
        <td>${tx.description || '-'}</td>
        <td>
            <span class="category-badge" style="background: ${tx.category_color}20; color: ${tx.category_color}; border: 1px solid ${tx.category_color}40;">
                <i data-lucide="${tx.category_icon}" style="width:14px; height:14px;"></i>
                ${tx.category_name}
            </span>
        </td>
        <td>${typeLabel}</td>
        <td class="${amountClass}">${amountSign}$${parseFloat(tx.amount).toFixed(2)}</td>
        <td>
            <button class="btn-delete" onclick="deleteTransaction(${tx.id})" title="Delete transaction">
                <i data-lucide="trash-2" style="width: 16px; height: 16px;"></i>
            </button>
        </td>
    `;
    
    // Вставляем новую запись в начало
    body.insertBefore(tr, body.firstChild);
    
    // Пересоздаем иконки для новой строки
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Удаление транзакции
window.deleteTransaction = function(txId) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    
    const csrfToken = getCookie('csrftoken');
    
    fetch(`/api/transaction/delete/${txId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const row = document.getElementById(`tx-row-${txId}`);
            if (row) {
                row.remove();
            }
            
            // Если таблица пуста, выводим пустое состояние
            const body = document.getElementById('transaction-list-body');
            if (body && body.querySelectorAll('tr').length === 0) {
                body.innerHTML = `
                    <tr id="empty-row">
                        <td colspan="6" class="empty-state">No transactions yet. Add your first transaction above!</td>
                    </tr>
                `;
            }
            
            // Обновляем статистику и график
            updateStats(data.stats);
            updateChart();
        } else {
            alert('Error deleting transaction: ' + data.message);
        }
    })
    .catch(err => {
        console.error('API Error:', err);
        alert('Something went wrong.');
    });
};

// Обновление балансовых карточек
function updateStats(stats) {
    const balance = document.getElementById('total-balance');
    const income = document.getElementById('total-income');
    const expense = document.getElementById('total-expense');
    
    if (balance) balance.innerText = `$${parseFloat(stats.balance).toFixed(2)}`;
    if (income) income.innerText = `$${parseFloat(stats.total_income).toFixed(2)}`;
    if (expense) expense.innerText = `$${parseFloat(stats.total_expense).toFixed(2)}`;
}
