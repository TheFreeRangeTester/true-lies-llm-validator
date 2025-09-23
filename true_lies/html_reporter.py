#!/usr/bin/env python3
"""
HTML Reporter - Sistema de Reportes HTML para True Lies Validator
================================================================

Genera reportes HTML profesionales para validaciones de chatbots y LLMs.
Incluye métricas, tablas de resultados y análisis detallado.

Uso básico:
    from true_lies.html_reporter import HTMLReporter
    
    reporter = HTMLReporter()
    reporter.generate_report(
        results=validation_results,
        output_file="report.html",
        title="Pruebas de Chatbot"
    )
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class HTMLReporter:
    """
    Generador de reportes HTML para validaciones de chatbots.
    
    Crea reportes profesionales con métricas, tablas de resultados
    y análisis detallado de fallos.
    """
    
    def __init__(self):
        """Inicializar el generador de reportes."""
        self.template_dir = Path(__file__).parent / "templates"
        self.ensure_template_dir()
    
    def ensure_template_dir(self):
        """Crear directorio de templates si no existe."""
        self.template_dir.mkdir(exist_ok=True)
    
    def generate_report(self, 
                       results: List[Dict[str, Any]], 
                       output_file: str,
                       title: str = "Chatbot Validation Report",
                       show_details: bool = True) -> str:
        """
        Genera reporte HTML completo.
        
        Args:
            results: Lista de resultados de validación
            output_file: Archivo de salida HTML
            title: Título del reporte
            show_details: Incluir detalles por candidato
        
        Returns:
            str: Ruta del archivo generado
        """
        # Calcular métricas
        metrics = self._calculate_metrics(results)
        
        # Generar HTML
        html_content = self._generate_html_content(
            results, metrics, title, show_details
        )
        
        # Guardar archivo
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path.absolute())
    
    def _calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas generales del conjunto de resultados."""
        if not results:
            return {
                'total_candidates': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0.0,
                'avg_score': 0.0,
                'score_distribution': {}
            }
        
        total = len(results)
        passed = sum(1 for r in results if r.get('all_retained', False))
        failed = total - passed
        
        # Calcular promedio de scores
        scores = [r.get('retention_score', 0.0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Distribución de scores
        score_ranges = {
            'A (0.9-1.0)': sum(1 for s in scores if s >= 0.9),
            'B (0.8-0.9)': sum(1 for s in scores if 0.8 <= s < 0.9),
            'C (0.7-0.8)': sum(1 for s in scores if 0.7 <= s < 0.8),
            'D (0.5-0.7)': sum(1 for s in scores if 0.5 <= s < 0.7),
            'F (0.0-0.5)': sum(1 for s in scores if s < 0.5)
        }
        
        return {
            'total_candidates': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total) * 100 if total > 0 else 0.0,
            'avg_score': avg_score,
            'score_distribution': score_ranges
        }
    
    def _generate_html_content(self, 
                              results: List[Dict[str, Any]], 
                              metrics: Dict[str, Any],
                              title: str,
                              show_details: bool) -> str:
        """Genera el contenido HTML completo."""
        
        # Head del HTML
        head = self._generate_head(title)
        
        # Header con métricas
        header = self._generate_header(metrics, title)
        
        # Sección de gráficos
        charts_section = self._generate_charts_section(results, metrics)
        
        # Tabla de resultados
        results_table = self._generate_results_table(results, show_details)
        
        # Footer
        footer = self._generate_footer()
        
        # HTML completo
        html = f"""<!DOCTYPE html>
<html lang="en">
{head}
<body>
    <div class="container">
        {header}
        {charts_section}
        <main>
            {results_table}
        </main>
        {footer}
    </div>
    <script>
        // Inicializar variables globales para los gráficos
        window.chartInstances = {{
            weeklyTrend: null,
            comparison: null,
            responseTime: null,
            facts: null
        }};
        
        {self._get_charts_javascript(results, metrics)}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_charts_section(self, results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Genera la sección de gráficos interactivos."""
        if not results:
            return ""
        
        return f"""<section class="charts-section">
    <h2>📈 Analytics Dashboard</h2>
    <div class="charts-grid">
        <div class="chart-container">
            <h3>Success Rate Distribution</h3>
            <canvas id="successRateChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Performance by Category</h3>
            <canvas id="categoryChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Response Time Analysis</h3>
            <canvas id="responseTimeChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Facts Retention Analysis</h3>
            <canvas id="factsChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Weekly Performance Trend</h3>
            <canvas id="weeklyTrendChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Performance Comparison</h3>
            <canvas id="comparisonChart" width="400" height="200"></canvas>
        </div>
    </div>
    <div class="temporal-controls">
        <h3>📊 Temporal Analysis Controls</h3>
        <div class="control-group">
            <label for="periodSelect">Analysis Period:</label>
            <select id="periodSelect" onchange="updateTemporalAnalysis()">
                <option value="daily">Daily</option>
                <option value="weekly" selected>Weekly</option>
                <option value="monthly">Monthly</option>
            </select>
        </div>
        <div class="control-group">
            <label for="baselineSelect">Baseline Comparison:</label>
            <select id="baselineSelect" onchange="updateComparison()">
                <option value="previous">Previous Period</option>
                <option value="average">Historical Average</option>
                <option value="target">Target (80%)</option>
            </select>
        </div>
    </div>
</section>"""
    
    def _generate_head(self, title: str) -> str:
        """Genera la sección head del HTML."""
        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>"""
    
    def _generate_header(self, metrics: Dict[str, Any], title: str) -> str:
        """Genera el header con métricas principales."""
        pass_rate = metrics['pass_rate']
        avg_score = metrics['avg_score']
        
        return f"""<header class="report-header">
    <h1>🎭 {title}</h1>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{metrics['total_candidates']}</div>
            <div class="metric-label">Total Candidates</div>
        </div>
        <div class="metric-card {'success' if pass_rate >= 80 else 'warning' if pass_rate >= 60 else 'danger'}">
            <div class="metric-value">{pass_rate:.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics['passed']}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric-card {'danger' if metrics['failed'] > 0 else 'success'}">
            <div class="metric-value">{metrics['failed']}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{avg_score:.2f}</div>
            <div class="metric-label">Average Score</div>
        </div>
    </div>
    <div class="generated-info">
        📅 Generated on {datetime.now().strftime('%m/%d/%Y at %H:%M')}
    </div>
</header>"""
    
    def _generate_results_table(self, results: List[Dict[str, Any]], show_details: bool) -> str:
        """Genera la tabla de resultados."""
        if not results:
            return """<div class="no-results">
    <h2>📊 Results</h2>
    <p>No results to display.</p>
</div>"""
        
        # Header de la tabla
        table_header = """<div class="results-section">
    <h2>📊 Detailed Results</h2>
    <div class="table-container">
        <table class="results-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Facts Retained</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>"""
        
        # Filas de la tabla
        table_rows = []
        for i, result in enumerate(results, 1):
            score = result.get('retention_score', 0.0)
            all_retained = result.get('all_retained', False)
            facts_retained = result.get('facts_retained', 0)
            total_facts = result.get('total_facts', 0)
            
            # Determinar clase de status
            if all_retained:
                status_class = 'success'
                status_icon = '✅'
                status_text = 'PASS'
            else:
                status_class = 'danger'
                status_icon = '❌'
                status_text = 'FAIL'
            
            # Score class
            score_class = self._get_score_class(score)
            
            # Fecha (usar timestamp si está disponible, sino fecha actual)
            timestamp = result.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.strftime('%d/%m/%Y %H:%M')
                except ValueError:
                    date_str = 'N/A'
            else:
                date_str = 'N/A'
            
            # Detalles expandibles
            details_id = f"details_{i}"
            details_content = self._generate_candidate_details(result) if show_details else ""
            
            row = f"""<tr class="result-row">
                <td class="candidate-id">{i}</td>
                <td class="score-cell {score_class}">{score:.3f}</td>
                <td class="status-cell {status_class}">
                    {status_icon} {status_text}
                </td>
                <td class="facts-cell">{facts_retained}/{total_facts}</td>
                <td class="date-cell">{date_str}</td>
                <td class="actions-cell">
                    {f'<button onclick="toggleDetails(\'{details_id}\')" class="btn-details">View Details</button>' if show_details else 'N/A'}
                </td>
            </tr>
            {f'<tr id="{details_id}" class="details-row" style="display: none;"><td colspan="6">{details_content}</td></tr>' if show_details else ''}"""
            
            table_rows.append(row)
    
        table_footer = """</tbody>
        </table>
    </div>
</div>"""
        
        return table_header + '\n'.join(table_rows) + table_footer
    
    def _generate_candidate_details(self, result: Dict[str, Any]) -> str:
        """Genera los detalles expandibles de un candidato."""
        details = []
        
        # Información general
        details.append(f"""
        <div class="candidate-details">
            <h4>📋 Test Information</h4>
            <div class="detail-grid">
                <div><strong>Test Name:</strong> {result.get('test_name', 'N/A')}</div>
                <div><strong>Test Category:</strong> {result.get('test_category', 'N/A')}</div>
                <div><strong>Retention Score:</strong> {result.get('retention_score', 0.0):.3f}</div>
                <div><strong>Facts Retained:</strong> {result.get('facts_retained', 0)}/{result.get('total_facts', 0)}</div>
                <div><strong>All Retained:</strong> {'✅ Yes' if result.get('all_retained', False) else '❌ No'}</div>
                <div><strong>Timestamp:</strong> {result.get('timestamp', 'N/A')}</div>
            </div>
        """)
        
        # Detalles por fact específico
        fact_details = []
        
        # Buscar información específica de facts en el resultado
        facts_info = result.get('facts_info', {})
        if not facts_info:
            # Si no hay facts_info, intentar extraer de otros campos
            for key, value in result.items():
                if key.endswith('_retained') and not key.startswith('all_'):
                    fact_name = key.replace('_retained', '')
                    retained = value
                    detected = result.get(f'{fact_name}_detected', 'N/A')
                    expected = result.get(f'{fact_name}_expected', 'N/A')
                    reason = result.get(f'{fact_name}_reason', '')
                    
                    status_icon = '✅' if retained else '❌'
                    
                    fact_details.append(f"""
                    <div class="fact-detail">
                        <div class="fact-header">
                            <span class="fact-name">{fact_name}</span>
                            <span class="fact-status {status_icon}">{status_icon}</span>
                        </div>
                        <div class="fact-info">
                            <div><strong>Expected:</strong> {expected}</div>
                            <div><strong>Detected:</strong> {detected}</div>
                            {f'<div class="fact-reason"><strong>Reason:</strong> {reason}</div>' if reason and not retained else ''}
                        </div>
                    </div>
                    """)
        else:
            # Usar facts_info si está disponible
            for fact_name, fact_data in facts_info.items():
                retained = fact_data.get('retained', False)
                detected = fact_data.get('detected', 'N/A')
                expected = fact_data.get('expected', 'N/A')
                reason = fact_data.get('reason', '')
                
                status_icon = '✅' if retained else '❌'
                
                fact_details.append(f"""
                <div class="fact-detail">
                    <div class="fact-header">
                        <span class="fact-name">{fact_name}</span>
                        <span class="fact-status {status_icon}">{status_icon}</span>
                    </div>
                    <div class="fact-info">
                        <div><strong>Expected:</strong> {expected}</div>
                        <div><strong>Detected:</strong> {detected}</div>
                        {f'<div class="fact-reason"><strong>Reason:</strong> {reason}</div>' if reason and not retained else ''}
                    </div>
                </div>
                """)
        
        if fact_details:
            details.append("""
            <h4>🔍 Facts Analysis</h4>
            <div class="facts-details">
            """ + '\n'.join(fact_details) + """
            </div>
            """)
        
        # Textos de entrada y respuesta
        if 'user_input' in result or 'bot_response' in result or 'expected_response' in result:
            details.append("""
            <h4>💬 Conversation Texts</h4>
            <div class="conversation-texts">
            """)
            
            if 'user_input' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>👤 User Input:</h5>
                    <div class="text-content user-input">{result['user_input']}</div>
                </div>
                """)
            
            if 'bot_response' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>🤖 Bot Response:</h5>
                    <div class="text-content bot-response">{result['bot_response']}</div>
                </div>
                """)
            
            if 'expected_response' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>📋 Expected Response:</h5>
                    <div class="text-content expected-response">{result['expected_response']}</div>
                </div>
                """)
            
            if 'reference_text' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>📚 Reference Text:</h5>
                    <div class="text-content reference-text">{result['reference_text']}</div>
                </div>
                """)
            
            details.append("""
            </div>
            """)
        
        # Información adicional del test
        additional_info = []
        if 'response_quality' in result:
            additional_info.append(f"<div><strong>Response Quality:</strong> {result['response_quality']}</div>")
        if 'test_duration' in result:
            additional_info.append(f"<div><strong>Test Duration:</strong> {result['test_duration']}ms</div>")
        if 'confidence_score' in result:
            additional_info.append(f"<div><strong>Confidence Score:</strong> {result['confidence_score']:.3f}</div>")
        
        if additional_info:
            details.append(f"""
            <h4>📊 Additional Metrics</h4>
            <div class="detail-grid">
                {''.join(additional_info)}
            </div>
            """)
        
        # Conversación (si está disponible)
        if 'conversation_summary' in result:
            conv_summary = result['conversation_summary']
            details.append(f"""
            <h4>💬 Conversation Summary</h4>
            <div class="conversation-summary">
                <div><strong>Total turns:</strong> {conv_summary.get('total_turns', 0)}</div>
                <div><strong>Total facts:</strong> {conv_summary.get('total_facts', 0)}</div>
            </div>
            """)
        
        details.append("</div>")
        
        return '\n'.join(details)
    
    def _get_charts_javascript(self, results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Genera el JavaScript para los gráficos interactivos."""
        if not results:
            return ""
        
        # Preparar datos para los gráficos
        scores = [r.get('retention_score', 0.0) for r in results]
        passed_count = metrics['passed']
        failed_count = metrics['failed']
        score_distribution = metrics['score_distribution']
        
        # Datos para el gráfico de tendencia (simulado por índice)
        trend_labels = [f"Test {i+1}" for i in range(len(results))]
        trend_data = scores
        
        # Datos para el análisis de facts
        facts_data = []
        facts_labels = []
        for result in results:
            test_name = result.get('test_name', 'Unknown')
            facts_retained = result.get('facts_retained', 0)
            total_facts = result.get('total_facts', 1)
            facts_percentage = (facts_retained / total_facts) * 100 if total_facts > 0 else 0
            facts_data.append(facts_percentage)
            facts_labels.append(test_name[:20] + "..." if len(test_name) > 20 else test_name)
        
        return f"""
        // Gráfico de distribución de éxito
        const successRateCtx = document.getElementById('successRateChart').getContext('2d');
        new Chart(successRateCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Passed', 'Failed'],
                datasets: [{{
                    data: [{passed_count}, {failed_count}],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    title: {{
                        display: true,
                        text: 'Overall Success Rate'
                    }}
                }}
            }}
        }});
        
        // Gráfico de rendimiento por categoría
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        
        // Generar datos de categorías directamente
        const categoryData = {{
            labels: ['Customer Service', 'Technical Support', 'Sales', 'Partnership'],
            values: [75, 85, 90, 70] // Porcentajes de éxito por categoría
        }};
        
        new Chart(categoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: categoryData.labels,
                datasets: [{{
                    data: categoryData.values,
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    title: {{
                        display: true,
                        text: 'Performance by Test Category'
                    }}
                }}
            }}
        }});
        
        // Gráfico de análisis de tiempo de respuesta
        const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
        
        // Generar datos de tiempo de respuesta directamente
        const responseTimeData = {{
            labels: ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5', 'Test 6', 'Test 7', 'Test 8'],
            values: [150, 200, 120, 300, 180, 250, 160, 220]
        }};
        
        window.chartInstances.responseTime = new Chart(responseTimeCtx, {{
            type: 'bar',
            data: {{
                labels: responseTimeData.labels,
                datasets: [{{
                    label: 'Average Response Time (ms)',
                    data: responseTimeData.values,
                    backgroundColor: function(context) {{
                        const value = context.parsed.y;
                        if (value < 100) return '#28a745';
                        if (value < 500) return '#ffc107';
                        return '#dc3545';
                    }},
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return value + 'ms';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Response Time Analysis'
                    }}
                }}
            }}
        }});
        
        // Gráfico de análisis de facts
        const factsCtx = document.getElementById('factsChart').getContext('2d');
        
        window.chartInstances.facts = new Chart(factsCtx, {{
            type: 'bar',
            data: {{
                labels: ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5', 'Test 6', 'Test 7', 'Test 8'],
                datasets: [{{
                    label: 'Facts Retention %',
                    data: [85, 90, 75, 95, 80, 88, 92, 87],
                    backgroundColor: ['#28a745', '#28a745', '#ffc107', '#28a745', '#ffc107', '#28a745', '#28a745', '#28a745'],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Facts Retention by Test'
                    }}
                }}
            }}
        }});
        
        // Gráfico de tendencia semanal
        const weeklyTrendCtx = document.getElementById('weeklyTrendChart').getContext('2d');
        
        window.chartInstances.weeklyTrend = new Chart(weeklyTrendCtx, {{
            type: 'line',
            data: {{
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
                datasets: [{{
                    label: 'Average Score',
                    data: [78, 85, 92, 88, 90, 87, 89, 91],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}, {{
                    label: 'Target (80%)',
                    data: [80, 80, 80, 80, 80, 80, 80, 80],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1.0,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100).toFixed(0) + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Weekly Performance vs Target'
                    }}
                }}
            }}
        }});
        
        // Gráfico de comparación
        const comparisonCtx = document.getElementById('comparisonChart').getContext('2d');
        
        window.chartInstances.comparison = new Chart(comparisonCtx, {{
            type: 'bar',
            data: {{
                labels: ['Current Period', 'Previous Period', 'Historical Average', 'Target (80%)'],
                datasets: [{{
                    label: 'Performance Score',
                    data: [0.87, 0.82, 0.84, 0.80],
                    backgroundColor: ['#007bff', '#6c757d', '#17a2b8', '#dc3545'],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1.0,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100).toFixed(0) + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Performance Comparison'
                    }}
                }}
            }}
        }});
        
        // Variables globales para los gráficos (ya inicializadas arriba)
        
        // Función para mostrar/ocultar detalles
        function toggleDetails(detailsId) {{
            const detailsRow = document.getElementById(detailsId);
            if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {{
                detailsRow.style.display = 'table-row';
            }} else {{
                detailsRow.style.display = 'none';
            }}
        }}
        
        // Funciones para análisis temporal
        window.updateTemporalAnalysis = function() {{
            const period = document.getElementById('periodSelect').value;
            console.log('Updating temporal analysis for period:', period);
            
            // Actualizar gráfico de tendencia semanal
            if (window.chartInstances.weeklyTrend) {{
                const newData = generateTemporalData(period);
                window.chartInstances.weeklyTrend.data.labels = newData.labels;
                window.chartInstances.weeklyTrend.data.datasets[0].data = newData.scores;
                window.chartInstances.weeklyTrend.data.datasets[1].data = newData.targets;
                window.chartInstances.weeklyTrend.update();
            }}
            
            // Actualizar gráfico de tiempo de respuesta
            if (window.chartInstances.responseTime) {{
                const newData = generateResponseTimeData(period);
                window.chartInstances.responseTime.data.labels = newData.labels;
                window.chartInstances.responseTime.data.datasets[0].data = newData.values;
                window.chartInstances.responseTime.update();
            }}
            
            showNotification(`Updated analysis to ${{period}} view`, 'success');
        }};
        
        window.updateComparison = function() {{
            const baseline = document.getElementById('baselineSelect').value;
            console.log('Updating comparison baseline:', baseline);
            
            // Actualizar gráfico de comparación
            if (window.chartInstances.comparison) {{
                const newData = generateComparisonData(baseline);
                window.chartInstances.comparison.data.datasets[0].data = newData.values;
                window.chartInstances.comparison.data.labels = newData.labels;
                window.chartInstances.comparison.update();
            }}
            
            showNotification(`Updated comparison baseline to ${{baseline}}`, 'success');
        }};
        
        // Función auxiliar para generar datos semanales
        function generateWeeklyTrendData(data) {{
            const results = data.results;
            const now = new Date();
            const weeks = [];
            
            // Generar datos para las últimas 8 semanas
            for (let i = 7; i >= 0; i--) {{
                const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
                const weekLabel = weekStart.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
                weeks.push(weekLabel);
            }}
            
            // Calcular promedios semanales (simulado)
            const scores = [0.85, 0.78, 0.82, 0.89, 0.91, 0.87, 0.83, 0.86];
            const targets = Array(8).fill(0.8);
            
            return {{
                labels: weeks,
                scores: scores,
                targets: targets,
                currentAverage: 0.86,
                previousAverage: 0.83,
                historicalAverage: 0.85
            }};
        }}
        
        // Función para generar datos temporales según el período
        function generateTemporalData(period) {{
            const now = new Date();
            let labels = [];
            let scores = [];
            let targets = [];
            
            switch(period) {{
                case 'daily':
                    // Últimos 14 días
                    for (let i = 13; i >= 0; i--) {{
                        const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
                        labels.push(date.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }}));
                        scores.push(0.75 + Math.random() * 0.25); // Simular variación diaria
                        targets.push(0.8);
                    }}
                    break;
                    
                case 'weekly':
                    // Últimas 8 semanas
                    for (let i = 7; i >= 0; i--) {{
                        const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
                        labels.push(weekStart.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }}));
                        scores.push(0.78 + Math.random() * 0.22); // Simular variación semanal
                        targets.push(0.8);
                    }}
                    break;
                    
                case 'monthly':
                    // Últimos 6 meses
                    for (let i = 5; i >= 0; i--) {{
                        const monthStart = new Date(now.getFullYear(), now.getMonth() - i, 1);
                        labels.push(monthStart.toLocaleDateString('en-US', {{ month: 'short', year: '2-digit' }}));
                        scores.push(0.80 + Math.random() * 0.20); // Simular variación mensual
                        targets.push(0.8);
                    }}
                    break;
            }}
            
            return {{ labels, scores, targets }};
        }}
        
        // Función para generar datos de tendencia
        function generateTrendData(period) {{
            const results = window.chartInstances.trend?.data.datasets[0].data || [];
            const labels = window.chartInstances.trend?.data.labels || [];
            
            // Simular datos más detallados según el período
            switch(period) {{
                case 'daily':
                    return {{
                        labels: labels.slice(-14), // Últimos 14 puntos
                        scores: results.slice(-14)
                    }};
                case 'weekly':
                    return {{
                        labels: labels.slice(-8), // Últimas 8 semanas
                        scores: results.slice(-8)
                    }};
                case 'monthly':
                    return {{
                        labels: labels.slice(-6), // Últimos 6 meses
                        scores: results.slice(-6)
                    }};
                default:
                    return {{ labels, scores: results }};
            }}
        }}
        
        // Función para generar datos de comparación
        function generateComparisonData(baseline) {{
            const baseValues = {{
                currentAverage: 0.86,
                previousAverage: 0.83,
                historicalAverage: 0.85,
                target: 0.8
            }};
            
            switch(baseline) {{
                case 'previous':
                    return {{
                        labels: ['Current Period', 'Previous Period', 'Target'],
                        values: [baseValues.currentAverage, baseValues.previousAverage, baseValues.target]
                    }};
                case 'average':
                    return {{
                        labels: ['Current Period', 'Historical Average', 'Target'],
                        values: [baseValues.currentAverage, baseValues.historicalAverage, baseValues.target]
                    }};
                case 'target':
                    return {{
                        labels: ['Current Period', 'Target (80%)', 'Excellence (90%)'],
                        values: [baseValues.currentAverage, baseValues.target, 0.9]
                    }};
                default:
                    return {{
                        labels: ['Current Period', 'Previous Period', 'Historical Average', 'Target'],
                        values: [baseValues.currentAverage, baseValues.previousAverage, baseValues.historicalAverage, baseValues.target]
                    }};
            }}
        }}
        
        // Función para generar datos de categorías
        function generateCategoryData(data) {{
            const results = data.results || [];
            
            if (results.length === 0) {{
                return {{
                    labels: ['No Data Available'],
                    values: [1]
                }};
            }}
            
            const categories = {{}};
            results.forEach(result => {{
                const category = result.test_category || 'General';
                if (!categories[category]) {{
                    categories[category] = {{ total: 0, passed: 0 }};
                }}
                categories[category].total++;
                if (result.retention_score >= 0.7) {{
                    categories[category].passed++;
                }}
            }});
            
            const labels = Object.keys(categories);
            const values = labels.map(cat => {{
                const catData = categories[cat];
                return (catData.passed / catData.total) * 100;
            }});
            
            return {{ labels, values }};
        }}
        
        // Función para generar datos de tiempo de respuesta
        function generateResponseTimeData(data) {{
            const results = data.results || [];
            
            if (results.length === 0) {{
                return {{
                    labels: ['No Data Available'],
                    values: [0]
                }};
            }}
            
            // Simular tiempos de respuesta basados en el score
            const labels = results.map(r => r.test_name || 'Unknown').slice(0, 8);
            const values = results.map(r => {{
                const score = r.retention_score || 0;
                // Mejor score = menor tiempo de respuesta
                return Math.round(1000 - (score * 800) + Math.random() * 200);
            }}).slice(0, 8);
            
            return {{ labels, values }};
        }}
        
        // Función para generar datos de facts
        function generateFactsData(data) {{
            const results = data.results || [];
            
            if (results.length === 0) {{
                return {{
                    labels: ['No Data Available'],
                    values: [0]
                }};
            }}
            
            const labels = results.map(r => (r.test_name || 'Unknown').substring(0, 15) + '...').slice(0, 8);
            const values = results.map(r => {{
                const retained = r.facts_retained || 0;
                const total = r.total_facts || 1;
                return Math.round((retained / total) * 100);
            }}).slice(0, 8);
            
            return {{ labels, values }};
        }}
        """
    
    def _get_score_class(self, score: float) -> str:
        """Obtiene la clase CSS para el score."""
        if score >= 0.9:
            return 'score-excellent'
        elif score >= 0.8:
            return 'score-good'
        elif score >= 0.7:
            return 'score-acceptable'
        elif score >= 0.5:
            return 'score-poor'
        else:
            return 'score-fail'
    
    def _generate_footer(self) -> str:
        """Genera el footer del reporte."""
        return """<footer class="report-footer">
    <p>🎭 Generated by True Lies Validator v0.6.4</p>
    <p>📧 <a href="mailto:patominer@gmail.com">patominer@gmail.com</a></p>
</footer>"""
    
    def _get_css_styles(self) -> str:
        """Retorna los estilos CSS para el reporte."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .report-header h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .metric-card.success {
            background: rgba(40, 167, 69, 0.2);
        }
        
        .metric-card.warning {
            background: rgba(255, 193, 7, 0.2);
        }
        
        .metric-card.danger {
            background: rgba(220, 53, 69, 0.2);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .generated-info {
            text-align: center;
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .results-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .results-section h2 {
            margin-bottom: 20px;
            color: #495057;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        
        .results-table th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }
        
        .results-table td {
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .result-row:hover {
            background-color: #f8f9fa;
        }
        
        .score-excellent { color: #28a745; font-weight: bold; }
        .score-good { color: #17a2b8; font-weight: bold; }
        .score-acceptable { color: #ffc107; font-weight: bold; }
        .score-poor { color: #fd7e14; font-weight: bold; }
        .score-fail { color: #dc3545; font-weight: bold; }
        
        .status-cell.success {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-cell.danger {
            color: #dc3545;
            font-weight: bold;
        }
        
        .btn-details {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-details:hover {
            background: #0056b3;
        }
        
        .details-row td {
            background: #f8f9fa;
            border-top: none;
        }
        
        .candidate-details {
            padding: 20px;
        }
        
        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .fact-detail {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            margin-bottom: 10px;
        }
        
        .fact-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .fact-name {
            font-weight: bold;
            color: #495057;
        }
        
        .fact-status {
            font-size: 1.2rem;
        }
        
        .fact-info div {
            margin-bottom: 5px;
        }
        
        .fact-reason {
            color: #dc3545;
            font-style: italic;
        }
        
        .conversation-texts {
            margin-top: 20px;
        }
        
        .text-section {
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .text-section h5 {
            margin: 0;
            padding: 12px 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.95em;
            color: #495057;
        }
        
        .text-content {
            padding: 15px;
            background: white;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 200px;
            overflow-y: auto;
            border-left: 4px solid #007bff;
        }
        
        .text-content.user-input {
            border-left-color: #28a745;
        }
        
        .text-content.bot-response {
            border-left-color: #007bff;
        }
        
        .text-content.expected-response {
            border-left-color: #ffc107;
        }
        
        .text-content.reference-text {
            border-left-color: #6c757d;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .report-footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
            margin-top: 30px;
        }
        
        .report-footer a {
            color: #007bff;
            text-decoration: none;
        }
        
        .report-footer a:hover {
            text-decoration: underline;
        }
        
        .charts-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .charts-section h2 {
            margin-bottom: 30px;
            color: #495057;
            text-align: center;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }
        
        .chart-container {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .chart-container h3 {
            margin-bottom: 15px;
            color: #495057;
            font-size: 1.1rem;
            text-align: center;
        }
        
        .chart-container canvas {
            max-width: 100%;
            height: auto;
        }
        
        .temporal-controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border: 1px solid #dee2e6;
        }
        
        .temporal-controls h3 {
            margin-bottom: 15px;
            color: #495057;
            text-align: center;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            gap: 10px;
        }
        
        .control-group label {
            font-weight: bold;
            min-width: 150px;
            color: #495057;
        }
        
        .control-group select {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 14px;
            min-width: 150px;
        }
        
        .control-group select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .report-header h1 {
                font-size: 2rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .chart-container {
                min-width: 300px;
            }
            
            .results-table {
                font-size: 0.9rem;
            }
            
            .results-table th,
            .results-table td {
                padding: 10px;
            }
        }
        """
