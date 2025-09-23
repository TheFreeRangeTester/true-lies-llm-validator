// JavaScript para interactividad del reporte HTML
function toggleDetails(detailsId) {
    const detailsRow = document.getElementById(detailsId);
    if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {
        detailsRow.style.display = 'table-row';
    } else {
        detailsRow.style.display = 'none';
    }
}

// Función para expandir/contraer todos los detalles
function toggleAllDetails() {
    const detailsRows = document.querySelectorAll('.details-row');
    const isVisible = detailsRows[0] && detailsRows[0].style.display !== 'none';

    detailsRows.forEach(row => {
        row.style.display = isVisible ? 'none' : 'table-row';
    });
}

// Función para filtrar resultados por status
function filterResults(status) {
    const rows = document.querySelectorAll('.result-row');

    rows.forEach(row => {
        const statusCell = row.querySelector('.status-cell');
        const statusText = statusCell.textContent.trim();

        if (status === 'all' || statusText.includes(status.toUpperCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    // Actualizar contador si existe
    if (document.getElementById('resultsCounter')) {
        updateVisibleCount();
    }
}

// Función para ordenar tabla por score
function sortByScore() {
    const tbody = document.querySelector('.results-table tbody');
    const rows = Array.from(tbody.querySelectorAll('.result-row'));

    rows.sort((a, b) => {
        const scoreA = parseFloat(a.querySelector('.score-cell').textContent);
        const scoreB = parseFloat(b.querySelector('.score-cell').textContent);
        return scoreB - scoreA; // Descendente
    });

    // Reorganizar filas
    rows.forEach(row => {
        tbody.appendChild(row);
    });
}

// Función para ordenar tabla por fecha
function sortByDate() {
    const tbody = document.querySelector('.results-table tbody');
    const rows = Array.from(tbody.querySelectorAll('.result-row'));

    rows.sort((a, b) => {
        const dateA = new Date(a.querySelector('.date-cell').textContent);
        const dateB = new Date(b.querySelector('.date-cell').textContent);
        return dateB - dateA; // Más reciente primero
    });

    // Reorganizar filas
    rows.forEach(row => {
        tbody.appendChild(row);
    });
}

// Función para filtrar por rango de score
function filterByScoreRange() {
    const minScore = parseFloat(prompt('Enter minimum score (0.0 - 1.0):', '0.0'));
    const maxScore = parseFloat(prompt('Enter maximum score (0.0 - 1.0):', '1.0'));

    if (isNaN(minScore) || isNaN(maxScore)) {
        alert('Please enter valid numbers');
        return;
    }

    const rows = document.querySelectorAll('.result-row');

    rows.forEach(row => {
        const score = parseFloat(row.querySelector('.score-cell').textContent);

        if (score >= minScore && score <= maxScore) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    // Actualizar contador
    updateVisibleCount();
}

// Función para filtrar por fecha
function filterByDate() {
    const startDate = prompt('Enter start date (YYYY-MM-DD):', '2024-01-01');
    const endDate = prompt('Enter end date (YYYY-MM-DD):', '2024-12-31');

    if (!startDate || !endDate) {
        alert('Please enter valid dates');
        return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    const rows = document.querySelectorAll('.result-row');

    rows.forEach(row => {
        const dateText = row.querySelector('.date-cell').textContent;
        const rowDate = new Date(dateText);

        if (rowDate >= start && rowDate <= end) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    updateVisibleCount();
}

// Función para filtrar por número de facts
function filterByFacts() {
    const minFacts = parseInt(prompt('Enter minimum facts retained:', '0'));
    const maxFacts = parseInt(prompt('Enter maximum facts retained:', '10'));

    if (isNaN(minFacts) || isNaN(maxFacts)) {
        alert('Please enter valid numbers');
        return;
    }

    const rows = document.querySelectorAll('.result-row');

    rows.forEach(row => {
        const factsText = row.querySelector('.facts-cell').textContent;
        const factsRetained = parseInt(factsText.split('/')[0]);

        if (factsRetained >= minFacts && factsRetained <= maxFacts) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    updateVisibleCount();
}

// Función para actualizar contador de resultados visibles
function updateVisibleCount() {
    const visibleRows = document.querySelectorAll('.result-row[style*="display: none"]');
    const totalRows = document.querySelectorAll('.result-row');
    const visibleCount = totalRows.length - visibleRows.length;

    // Crear o actualizar contador
    let counter = document.getElementById('resultsCounter');
    if (!counter) {
        counter = document.createElement('div');
        counter.id = 'resultsCounter';
        counter.style.cssText = 'margin: 10px 0; padding: 8px; background: #e9ecef; border-radius: 4px; font-weight: bold;';

        const resultsSection = document.querySelector('.results-section h2');
        resultsSection.parentNode.insertBefore(counter, resultsSection.nextSibling);
    }

    counter.textContent = `Showing ${visibleCount} of ${totalRows.length} results`;
}

// Función para filtros combinados
function advancedFilters() {
    const filterType = prompt('Choose filter type:\n1. Score Range\n2. Date Range\n3. Facts Range\n4. Clear All Filters', '1');

    switch (filterType) {
        case '1':
            filterByScoreRange();
            break;
        case '2':
            filterByDate();
            break;
        case '3':
            filterByFacts();
            break;
        case '4':
            filterResults('all');
            break;
        default:
            alert('Invalid option');
    }
}

// Función para exportar datos como JSON
function exportResults() {
    const results = [];
    const rows = document.querySelectorAll('.result-row');

    rows.forEach((row, index) => {
        const score = parseFloat(row.querySelector('.score-cell').textContent);
        const status = row.querySelector('.status-cell').textContent.trim();
        const facts = row.querySelector('.facts-cell').textContent.trim();

        results.push({
            id: index + 1,
            score: score,
            status: status,
            facts: facts
        });
    });

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = 'validation_results.json';
    link.click();
}

// Función para mostrar estadísticas adicionales
function showAdvancedStats() {
    const rows = document.querySelectorAll('.result-row');
    const scores = [];

    rows.forEach(row => {
        const score = parseFloat(row.querySelector('.score-cell').textContent);
        scores.push(score);
    });

    if (scores.length === 0) return;

    // Calcular estadísticas
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    const min = Math.min(...scores);
    const max = Math.max(...scores);
    const median = scores.sort((a, b) => a - b)[Math.floor(scores.length / 2)];

    alert(`📊 Advanced Statistics:
Average: ${avg.toFixed(3)}
Minimum: ${min.toFixed(3)}
Maximum: ${max.toFixed(3)}
Median: ${median.toFixed(3)}
Total: ${scores.length} candidates`);
}

// Función para buscar en la tabla
// Función de debounce para mejorar rendimiento
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Función de búsqueda mejorada
function performAdvancedSearch(searchTerm) {
    if (!searchTerm) {
        // Mostrar todos los resultados si no hay término de búsqueda
        const rows = document.querySelectorAll('.result-row');
        rows.forEach(row => {
            row.style.display = '';
        });
        updateSearchResults(rows.length, rows.length);
        return;
    }

    const rows = document.querySelectorAll('.result-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const testName = row.querySelector('.test-name-cell')?.textContent.toLowerCase() || '';
        const status = row.querySelector('.status-cell')?.textContent.toLowerCase() || '';
        const score = row.querySelector('.score-cell')?.textContent || '';
        const date = row.querySelector('.date-cell')?.textContent || '';
        const facts = row.querySelector('.facts-cell')?.textContent || '';

        // Búsqueda inteligente con múltiples criterios
        const matches = checkAdvancedMatch(searchTerm, {
            testName,
            status,
            score,
            date,
            facts,
            fullText: row.textContent.toLowerCase()
        });

        if (matches) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    updateSearchResults(visibleCount, rows.length);
}

// Función para verificar coincidencias avanzadas
function checkAdvancedMatch(searchTerm, data) {
    // Búsqueda por operadores especiales
    if (searchTerm.startsWith('score:')) {
        const targetScore = parseFloat(searchTerm.substring(6));
        const currentScore = parseFloat(data.score);
        return !isNaN(targetScore) && currentScore >= targetScore;
    }

    if (searchTerm.startsWith('score>')) {
        const targetScore = parseFloat(searchTerm.substring(6));
        const currentScore = parseFloat(data.score);
        return !isNaN(targetScore) && currentScore > targetScore;
    }

    if (searchTerm.startsWith('score<')) {
        const targetScore = parseFloat(searchTerm.substring(6));
        const currentScore = parseFloat(data.score);
        return !isNaN(targetScore) && currentScore < targetScore;
    }

    if (searchTerm.startsWith('date:')) {
        const targetDate = searchTerm.substring(5);
        return data.date.includes(targetDate);
    }

    if (searchTerm.startsWith('facts:')) {
        const targetFacts = searchTerm.substring(6);
        return data.facts.includes(targetFacts);
    }

    if (searchTerm.startsWith('status:')) {
        const targetStatus = searchTerm.substring(7);
        return data.status.includes(targetStatus);
    }

    // Búsqueda por palabras clave inteligentes
    const keywords = {
        'pass': 'pass',
        'fail': 'fail',
        'excellent': 'a',
        'good': 'b',
        'average': 'c',
        'poor': 'd',
        'failing': 'f',
        'today': getTodayString(),
        'yesterday': getYesterdayString(),
        'this week': 'week',
        'high score': '0.8',
        'low score': '0.3'
    };

    for (const [keyword, match] of Object.entries(keywords)) {
        if (searchTerm.includes(keyword)) {
            if (data.fullText.includes(match)) {
                return true;
            }
        }
    }

    // Búsqueda normal por texto
    return data.fullText.includes(searchTerm);
}

// Función para actualizar contador de resultados de búsqueda
function updateSearchResults(visible, total) {
    let searchCounter = document.getElementById('searchCounter');
    if (!searchCounter) {
        searchCounter = document.createElement('div');
        searchCounter.id = 'searchCounter';
        searchCounter.style.cssText = 'margin: 5px 0; padding: 5px 10px; background: #e3f2fd; border-radius: 4px; font-size: 0.9em; color: #1976d2;';

        const searchInput = document.getElementById('searchInput');
        searchInput.parentNode.appendChild(searchCounter);
    }

    if (visible === total) {
        searchCounter.textContent = `Showing all ${total} results`;
        searchCounter.style.background = '#e8f5e8';
        searchCounter.style.color = '#2e7d32';
    } else {
        searchCounter.textContent = `Found ${visible} of ${total} results`;
        searchCounter.style.background = '#e3f2fd';
        searchCounter.style.color = '#1976d2';
    }
}

// Funciones auxiliares para fechas
function getTodayString() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function getYesterdayString() {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toISOString().split('T')[0];
}

// Función de búsqueda original (mantener compatibilidad)
function searchTable() {
    const input = document.getElementById('searchInput');
    performAdvancedSearch(input.value);
}

// Función para exportar a PDF
function exportToPDF() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');

    // Mostrar indicador de carga
    showLoadingIndicator('Generating PDF...');

    // Capturar el contenido del reporte
    const reportElement = document.querySelector('.container');

    html2canvas(reportElement, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        width: reportElement.scrollWidth,
        height: reportElement.scrollHeight
    }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = 210; // A4 width in mm
        const pageHeight = 295; // A4 height in mm
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;

        let position = 0;

        // Agregar primera página
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        // Agregar páginas adicionales si es necesario
        while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
        }

        // Generar nombre de archivo con timestamp
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `chatbot_validation_report_${timestamp}.pdf`;

        // Descargar PDF
        pdf.save(filename);

        hideLoadingIndicator();
        showSuccessMessage(`PDF exported successfully: ${filename}`);
    }).catch(error => {
        hideLoadingIndicator();
        showErrorMessage('Error generating PDF: ' + error.message);
    });
}

// Función para mostrar indicador de carga
function showLoadingIndicator(message) {
    let loadingDiv = document.getElementById('loadingIndicator');
    if (!loadingDiv) {
        loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingIndicator';
        loadingDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px 40px;
            border-radius: 8px;
            z-index: 10000;
            font-size: 16px;
            font-weight: bold;
        `;
        document.body.appendChild(loadingDiv);
    }
    loadingDiv.textContent = message;
    loadingDiv.style.display = 'block';
}

// Función para ocultar indicador de carga
function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

// Función para mostrar mensaje de éxito
function showSuccessMessage(message) {
    showNotification(message, 'success');
}

// Función para mostrar mensaje de error
function showErrorMessage(message) {
    showNotification(message, 'error');
}

// Función para mostrar notificaciones
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 10001;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;

    if (type === 'success') {
        notification.style.background = '#28a745';
    } else if (type === 'error') {
        notification.style.background = '#dc3545';
    }

    notification.textContent = message;
    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    // Agregar funcionalidad de búsqueda si no existe
    const resultsSection = document.querySelector('.results-section h2');
    if (resultsSection && !document.getElementById('searchInput')) {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.style.marginBottom = '20px';

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.id = 'searchInput';
        searchInput.placeholder = '🔍 Search in results... (supports: test names, scores, dates, facts)';
        searchInput.style.padding = '8px 12px';
        searchInput.style.border = '1px solid #ddd';
        searchInput.style.borderRadius = '4px';
        searchInput.style.width = '300px';

        searchInput.addEventListener('input', debounce(function () {
            performAdvancedSearch(this.value);
        }, 300));

        searchContainer.appendChild(searchInput);
        resultsSection.parentNode.insertBefore(searchContainer, resultsSection.nextSibling);
    }

    // Agregar botones de control si no existen
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer && !document.getElementById('controlButtons')) {
        const controlDiv = document.createElement('div');
        controlDiv.id = 'controlButtons';
        controlDiv.style.marginBottom = '15px';
        controlDiv.style.display = 'flex';
        controlDiv.style.gap = '10px';
        controlDiv.style.flexWrap = 'wrap';

        const buttons = [
            { text: '📊 Statistics', onclick: 'showAdvancedStats()' },
            { text: '🔽 Sort by Score', onclick: 'sortByScore()' },
            { text: '📅 Sort by Date', onclick: 'sortByDate()' },
            { text: '🔍 Advanced Filters', onclick: 'advancedFilters()' },
            { text: '✅ Success Only', onclick: 'filterResults("pass")' },
            { text: '❌ Failures Only', onclick: 'filterResults("fail")' },
            { text: '🔄 Show All', onclick: 'filterResults("all")' },
            { text: '📁 Export JSON', onclick: 'exportResults()' },
            { text: '📄 Export PDF', onclick: 'exportToPDF()' }
        ];

        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.textContent = btn.text;
            button.onclick = eval(btn.onclick);
            button.style.padding = '6px 12px';
            button.style.border = '1px solid #007bff';
            button.style.borderRadius = '4px';
            button.style.background = 'white';
            button.style.color = '#007bff';
            button.style.cursor = 'pointer';
            button.style.fontSize = '0.9rem';

            button.addEventListener('mouseenter', function () {
                this.style.background = '#007bff';
                this.style.color = 'white';
            });

            button.addEventListener('mouseleave', function () {
                this.style.background = 'white';
                this.style.color = '#007bff';
            });

            controlDiv.appendChild(button);
        });

        tableContainer.parentNode.insertBefore(controlDiv, tableContainer);
    }
});
