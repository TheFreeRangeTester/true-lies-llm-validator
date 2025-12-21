#!/usr/bin/env python3
"""
HTML Reporter - HTML Reporting System for True Lies Validator
=============================================================

Generates professional HTML reports for chatbot and LLM validations.
Includes metrics, results tables and detailed analysis.

Basic usage:
    from true_lies.html_reporter import HTMLReporter
    
    reporter = HTMLReporter()
    reporter.generate_report(
        results=validation_results,
        output_file="report.html",
        title="Chatbot Tests"
    )
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class HTMLReporter:
    """
    HTML report generator for chatbot validations.
    
    Creates professional reports with metrics, results tables
    and detailed failure analysis.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.template_dir = Path(__file__).parent / "templates"
        self.ensure_template_dir()
    
    def ensure_template_dir(self):
        """Create templates directory if it doesn't exist."""
        self.template_dir.mkdir(exist_ok=True)
    
    def _normalize_results(self, results: List[Dict[str, Any]], scenario: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Normalizes results for compatibility with both test types.
        
        Automatically detects if results are from:
        - Multi-turn conversation (ConversationValidator)
        - Candidate validation (validate_llm_candidates)
        
        Args:
            results: List of results in any format
            scenario: Optional scenario data for extracting expected values
            
        Returns:
            List[Dict]: Results normalized to HTMLReporter expected format
        """
        if not results:
            return results
        
        # Detect result type based on first element structure
        first_result = results[0]
        
        # If has 'index', 'candidate', 'result', 'is_valid' -> from validate_llm_candidates
        if all(key in first_result for key in ['index', 'candidate', 'result', 'is_valid']):
            return self._normalize_candidate_results(results, scenario)
        
        # If already has 'retention_score', 'all_retained' -> from ConversationValidator
        elif all(key in first_result for key in ['retention_score', 'all_retained']):
            return results
        
        # If format not recognized, try to normalize as candidates
        else:
            return self._normalize_candidate_results(results, scenario)
    
    def _normalize_candidate_results(self, results: List[Dict[str, Any]], scenario: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Normalizes validate_llm_candidates results to HTMLReporter expected format.
        
        Args:
            results: Results from validate_llm_candidates
            scenario: Optional scenario data for extracting expected values
            
        Returns:
            List[Dict]: Normalized results
        """
        normalized = []
        
        for item in results:
            result_data = item['result']
            
            # Count retained facts
            facts_retained = 0
            total_facts = 0
            facts_info = {}
            
            # Search all accuracy fields to count facts
            for key, value in result_data.items():
                if key.endswith('_accuracy'):
                    fact_name = key.replace('_accuracy', '')
                    
                    # Skip 'factual' as it's not a real fact, just an internal field
                    if fact_name == 'factual':
                        continue
                    
                    total_facts += 1
                    if value:
                        facts_retained += 1
                    
                    # Create fact information
                    expected_value = 'N/A'
                    if scenario and 'facts' in scenario and fact_name in scenario['facts']:
                        expected_value = scenario['facts'][fact_name].get('expected', 'N/A')
                    
                    facts_info[fact_name] = {
                        'expected': expected_value,
                        'extracted': result_data.get(f'extracted_{fact_name}', 'None'),
                        'accuracy': value
                    }
            
            # Get query from scenario name (preferred) or semantic_reference (fallback)
            query_text = ''
            if scenario:
                # Prefer scenario name (the actual query/question) over semantic_reference
                query_text = scenario.get('name', '') or scenario.get('semantic_reference', '')
            
            # Create normalized result
            normalized_result = {
                'test_name': f"Candidate {item['index']}",
                'retention_score': result_data.get('similarity_score', 0.0),
                'all_retained': item['is_valid'],
                'facts_retained': facts_retained,
                'total_facts': total_facts,
                'candidate_text': item['candidate'],
                'timestamp': datetime.now().isoformat(),
                'test_category': 'LLM Validation',
                'facts_info': facts_info,
                'similarity_score': result_data.get('similarity_score', 0.0),
                'polarity_match': result_data.get('polarity_match', False),
                'reference_polarity': result_data.get('reference_polarity', 'neutral'),
                'candidate_polarity': result_data.get('candidate_polarity', 'neutral'),
                'failure_reason': result_data.get('failure_reason', ''),
                'query': query_text
            }
            
            normalized.append(normalized_result)
        
        return normalized
    
    def _save_execution_to_history(self, results: List[Dict[str, Any]], metrics: Dict[str, Any], scenario: Dict[str, Any] = None):
        """Save current execution data to history for temporal analysis."""
        try:
            # Initialize history manager
            history = ResultsHistory()
            
            # Extract execution data
            execution_data = {
                "scenario_name": scenario.get("name", "unknown") if scenario else "unknown",
                "total_candidates": metrics["total_candidates"],
                "passed": metrics["passed"],
                "failed": metrics["failed"],
                "pass_rate": metrics["pass_rate"],
                "avg_similarity_score": metrics.get("avg_score", 0.0),
                "avg_factual_accuracy": self._calculate_factual_accuracy(results),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to history
            history.save_execution(execution_data)
            
        except Exception as e:
            print(f"Warning: Could not save execution to history: {e}")
    
    def _calculate_factual_accuracy(self, results: List[Dict[str, Any]]) -> float:
        """Calculate average factual accuracy from results."""
        if not results:
            return 0.0
        
        total_facts = 0
        correct_facts = 0
        
        for result in results:
            facts_info = result.get("facts_info", {})
            for fact_name, fact_data in facts_info.items():
                total_facts += 1
                if fact_data.get("accuracy", False):
                    correct_facts += 1
        
        return (correct_facts / total_facts * 100) if total_facts > 0 else 0.0
    
    def _get_temporal_data(self) -> Dict[str, Any]:
        """Get real temporal data for charts."""
        try:
            history = ResultsHistory()
            # Use daily data for more granular view, get last 7 days
            return history.get_temporal_data("daily", 7)
        except Exception as e:
            print(f"Warning: Could not load temporal data: {e}")
            return {"labels": [], "scores": [], "counts": []}
    
    def _get_comparison_data(self) -> Dict[str, Any]:
        """Get real comparison data for charts."""
        try:
            history = ResultsHistory()
            return history.get_comparison_data()
        except Exception as e:
            print(f"Warning: Could not load comparison data: {e}")
            return {
                "current_period": 0,
                "previous_period": 0,
                "historical_average": 0,
                "target": 80
            }
    
    def generate_report(self, 
                       results: List[Dict[str, Any]], 
                       output_file: str,
                       title: str = "Chatbot Validation Report",
                       show_details: bool = True,
                       scenario: Dict[str, Any] = None,
                       save_to_history: bool = True) -> str:
        """
        Generates complete HTML report.
        
        Args:
            results: List of validation results (conversation or candidates)
            output_file: HTML output file
            title: Report title
            show_details: Include details per candidate
            scenario: Optional scenario data for extracting expected values
            save_to_history: Whether to save execution data to history
        
        Returns:
            str: Path of generated file
        """
        # Normalize results for compatibility with both test types
        normalized_results = self._normalize_results(results, scenario)
        
        # Calculate metrics
        metrics = self._calculate_metrics(normalized_results)
        
        # Save to history if requested
        if save_to_history:
            self._save_execution_to_history(normalized_results, metrics, scenario)
        
        # Generate HTML
        html_content = self._generate_html_content(
            normalized_results, metrics, title, show_details
        )
        
        # Save file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path.absolute())
    
    def _calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates general metrics from the results set."""
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
        
        # Calculate average scores
        scores = [r.get('retention_score', 0.0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Score distribution
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
        """Generates complete HTML content."""
        
        # HTML head
        head = self._generate_head(title)
        
        # Header with metrics
        header = self._generate_header(metrics, title)
        
        # Charts section
        charts_section = self._generate_charts_section(results, metrics)
        
        # Results table
        results_table = self._generate_results_table(results, show_details)
        
        # Footer
        footer = self._generate_footer()
        
        # Complete HTML
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
            similarityTrend: null,
            factRetention: null
        }};
        
        {self._get_sorting_javascript()}
        
        {self._get_charts_javascript(results, metrics)}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_charts_section(self, results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Genera la sección de gráficos interactivos."""
        if not results:
            return ""
        
        return """<section class="charts-section">
    <h2>Analytics Dashboard</h2>
    <div class="charts-grid">
        <div class="chart-container chart-centered">
            <h3>Success Rate Distribution</h3>
            <canvas id="successRateChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container chart-wide">
            <h3>Performance Trend</h3>
            <div class="target-control">
                <label for="targetInput">Target (%):</label>
                <input type="number" id="targetInput" value="80" min="0" max="100" step="1" 
                       onchange="updateTarget(this.value)">
            </div>
            <canvas id="weeklyTrendChart" width="800" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Similarity Score Trend</h3>
            <canvas id="similarityTrendChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Fact Retention Trend</h3>
            <canvas id="factRetentionChart" width="400" height="200"></canvas>
        </div>
    </div>
</section>"""
    
    def _generate_head(self, title: str) -> str:
        """Genera la sección head del HTML."""
        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
        <!-- Chart.js CDN -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <!-- PDF Generation Libraries -->
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
    <h1>{title}</h1>
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
    <h2>Results</h2>
    <p>No results to display.</p>
</div>"""
        
        # Header de la tabla
        table_header = """<div class="results-section">
    <h2>Detailed Results</h2>
    <div class="table-container">
        <table class="results-table" id="resultsTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)" class="sortable">
                        ID <span class="sort-indicator">↕</span>
                    </th>
                    <th onclick="sortTable(1)" class="sortable">
                        Score <span class="sort-indicator">↕</span>
                    </th>
                    <th onclick="sortTable(2)" class="sortable">
                        Status <span class="sort-indicator">↕</span>
                    </th>
                    <th onclick="sortTable(3)" class="sortable">
                        Facts Retained <span class="sort-indicator">↕</span>
                    </th>
                    <th onclick="sortTable(4)" class="sortable">
                        Date <span class="sort-indicator">↕</span>
                    </th>
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
                status_icon = '✓'
                status_text = 'PASS'
            else:
                status_class = 'danger'
                status_icon = '✗'
                status_text = 'FAIL'
            
            # Score class
            score_class = self._get_score_class(score)
            
            # Date (use timestamp if available, otherwise current date)
            timestamp = result.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.strftime('%d/%m/%Y %H:%M')
                except ValueError:
                    date_str = 'N/A'
            else:
                date_str = 'N/A'
            
            # Expandable details
            details_id = f"details_{i}"
            details_content = self._generate_candidate_details(result) if show_details else ""
            
            # Create button and details row separately
            button_html = f'<button onclick="toggleDetails(\'{details_id}\')" class="btn-details" id="btn-{details_id}">View Details</button>' if show_details else 'N/A'
            details_row = f'<tr id="{details_id}" class="details-row" style="display: none;"><td colspan="6">{details_content}</td></tr>' if show_details else ''
            
            row = f"""<tr class="result-row">
                <td class="candidate-id">{i}</td>
                <td class="score-cell {score_class}">{score:.3f}</td>
                <td class="status-cell {status_class}">
                    {status_icon} {status_text}
                </td>
                <td class="facts-cell">{facts_retained}/{total_facts}</td>
                <td class="date-cell">{date_str}</td>
                <td class="actions-cell">
                    {button_html}
                </td>
            </tr>
            {details_row}"""
            
            table_rows.append(row)
    
        table_footer = """</tbody>
        </table>
    </div>
</div>"""
        
        return table_header + '\n'.join(table_rows) + table_footer
    
    def _generate_candidate_details(self, result: Dict[str, Any]) -> str:
        """Generates expandable details for a candidate."""
        details = []
        
        # General information
        retention_score = f"{result.get('retention_score', 0.0):.3f}"
        facts_retained = result.get('facts_retained', 0)
        total_facts = result.get('total_facts', 0)
        all_retained = result.get('all_retained', False)
        
        details.append(f"""
        <div class="candidate-details">
            <h4>Test Information</h4>
            <div class="detail-grid">
                <div><strong>Test Name:</strong> {result.get('test_name', 'N/A')}</div>
                <div><strong>Test Category:</strong> {result.get('test_category', 'N/A')}</div>
                <div><strong>Retention Score:</strong> {retention_score}</div>
                <div><strong>Facts Retained:</strong> {facts_retained}/{total_facts}</div>
                <div><strong>All Retained:</strong> {'✓ Yes' if all_retained else '✗ No'}</div>
                <div><strong>Timestamp:</strong> {result.get('timestamp', 'N/A')}</div>
            </div>
        """)
        
        # Show query prominently if available
        if result.get('query'):
            details.append(f"""
            <div class="query-section">
                <h4>🔍 Query / Question</h4>
                <div class="query-display">{result.get('query')}</div>
            </div>
            """)
        
        # Details by specific fact
        fact_details = []
        
        # Search for specific fact information in the result
        facts_info = result.get('facts_info', {})
        if facts_info:
            # Use facts_info if available (normalized format)
            for fact_name, fact_data in facts_info.items():
                accuracy = fact_data.get('accuracy', False)
                expected = fact_data.get('expected', 'N/A')
                extracted = fact_data.get('extracted', 'N/A')
                
                status_icon = '✓' if accuracy else '✗'
                
                fact_details.append(f"""
                <div class="fact-detail">
                    <div class="fact-header">
                        <span class="fact-name">{fact_name}</span>
                        <span class="fact-status {status_icon}">{status_icon}</span>
                    </div>
                    <div class="fact-info">
                        <div><strong>Expected:</strong> {expected}</div>
                        <div><strong>Extracted:</strong> {extracted}</div>
                    </div>
                </div>
                """)
        else:
            # If no facts_info, try to extract from other fields (conversation format)
            for key, value in result.items():
                if key.endswith('_retained') and not key.startswith('all_'):
                    fact_name = key.replace('_retained', '')
                    retained = value
                    detected = result.get(f'{fact_name}_detected', 'N/A')
                    expected = result.get(f'{fact_name}_expected', 'N/A')
                    reason = result.get(f'{fact_name}_reason', '')
                    
                    status_icon = '✓' if retained else '✗'
                    
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
            <h4>Facts Analysis</h4>
            <div class="facts-details">
            """ + '\n'.join(fact_details) + """
            </div>
            """)
        
        # Additional information for validated candidates
        if result.get('test_category') == 'LLM Validation':
            similarity_score = result.get('similarity_score', 0.0)
            polarity_match = result.get('polarity_match', False)
            reference_polarity = result.get('reference_polarity', 'neutral')
            candidate_polarity = result.get('candidate_polarity', 'neutral')
            failure_reason = result.get('failure_reason', '')
            
            details.append(f"""
            <h4>Validation Details</h4>
            <div class="validation-details">
                <div class="detail-grid">
                    <div><strong>Similarity Score:</strong> {similarity_score:.3f}</div>
                    <div><strong>Polarity Match:</strong> {'✓ Yes' if polarity_match else '✗ No'}</div>
                    <div><strong>Reference Polarity:</strong> {reference_polarity}</div>
                    <div><strong>Candidate Polarity:</strong> {candidate_polarity}</div>
                </div>
                {f'<div class="failure-reason"><strong>Failure Reason:</strong> {failure_reason}</div>' if failure_reason else ''}
            </div>
            """)
        
        # Input and response texts
        if 'user_input' in result or 'bot_response' in result or 'expected_response' in result or 'candidate_text' in result or 'query' in result:
            details.append("""
            <h4>Texts</h4>
            <div class="conversation-texts">
            """)
            
            if 'query' in result and result['query']:
                details.append(f"""
                <div class="text-section">
                    <h5>🔍 Query / Reference:</h5>
                    <div class="text-content query-text">{result['query']}</div>
                </div>
                """)
            
            if 'candidate_text' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>📝 Candidate Text:</h5>
                    <div class="text-content candidate-text">{result['candidate_text']}</div>
                </div>
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
                    <h5>Expected Response:</h5>
                    <div class="text-content expected-response">{result['expected_response']}</div>
                </div>
                """)
            
            if 'reference_text' in result:
                details.append(f"""
                <div class="text-section">
                    <h5>Reference Text:</h5>
                    <div class="text-content reference-text">{result['reference_text']}</div>
                </div>
                """)
            
            details.append("""
            </div>
            """)
        
        # Additional test information
        additional_info = []
        if 'response_quality' in result:
            additional_info.append(f"<div><strong>Response Quality:</strong> {result['response_quality']}</div>")
        if 'test_duration' in result:
            additional_info.append(f"<div><strong>Test Duration:</strong> {result['test_duration']}ms</div>")
        if 'confidence_score' in result:
            additional_info.append(f"<div><strong>Confidence Score:</strong> {result['confidence_score']:.3f}</div>")
        
        if additional_info:
            details.append(f"""
            <h4>Additional Metrics</h4>
            <div class="detail-grid">
                {''.join(additional_info)}
            </div>
            """)
        
        # Conversation (if available)
        if 'conversation_summary' in result:
            conv_summary = result['conversation_summary']
            details.append(f"""
            <h4>Conversation Summary</h4>
            <div class="conversation-summary">
                <div><strong>Total turns:</strong> {conv_summary.get('total_turns', 0)}</div>
                <div><strong>Total facts:</strong> {conv_summary.get('total_facts', 0)}</div>
            </div>
            """)
        
        details.append("</div>")
        
        return '\n'.join(details)
    
    def _get_sorting_javascript(self) -> str:
        """Genera el JavaScript para el sorting de la tabla."""
        return """
        // Función para ordenar la tabla
        function sortTable(columnIndex) {
            console.log('sortTable called with columnIndex:', columnIndex);
            
            const table = document.getElementById('resultsTable');
            if (!table) {
                console.error('Table with id resultsTable not found');
                return;
            }
            
            const tbody = table.querySelector('tbody');
            if (!tbody) {
                console.error('Table tbody not found');
                return;
            }
            
            const allRows = Array.from(tbody.querySelectorAll('tr'));
            const headers = table.querySelectorAll('th');
            
            console.log('Found', allRows.length, 'total rows and', headers.length, 'headers');
            
            // Filtrar solo las filas que tienen el número correcto de celdas (6 celdas = fila principal)
            const rows = allRows.filter(row => row.cells && row.cells.length >= 6);
            
            console.log('Filtered to', rows.length, 'sortable rows (with 6+ cells)');
            
            if (rows.length === 0) {
                console.error('No sortable rows found in table');
                return;
            }
            
            // Determinar el orden de sorting
            let sortOrder = 'asc';
            const currentHeader = headers[columnIndex];
            
            console.log('Current header classes:', currentHeader.classList.toString());
            
            // Si ya está ordenado por esta columna, cambiar el orden
            if (currentHeader.classList.contains('sort-asc')) {
                sortOrder = 'desc';
                currentHeader.classList.remove('sort-asc');
                currentHeader.classList.add('sort-desc');
            } else if (currentHeader.classList.contains('sort-desc')) {
                sortOrder = 'asc';
                currentHeader.classList.remove('sort-desc');
                currentHeader.classList.add('sort-asc');
            } else {
                // Limpiar clases de sorting de todos los headers
                headers.forEach(header => {
                    header.classList.remove('sort-asc', 'sort-desc');
                });
                sortOrder = 'asc';
                currentHeader.classList.add('sort-asc');
            }
            
            console.log('Sorting in', sortOrder, 'order');
            
            // Ordenar las filas
            console.log('Starting sort with', rows.length, 'rows');
            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();
                
                console.log('Comparing:', aValue, 'vs', bValue);
                
                // Manejar diferentes tipos de datos
                let comparison = 0;
                
                if (columnIndex === 0) { // ID - numérico
                    comparison = parseInt(aValue) - parseInt(bValue);
                } else if (columnIndex === 1) { // Score - numérico
                    comparison = parseFloat(aValue) - parseFloat(bValue);
                } else if (columnIndex === 3) { // Facts Retained - formato "X/Y"
                    const aMatch = aValue.match(/(\\d+)\\/(\\d+)/);
                    const bMatch = bValue.match(/(\\d+)\\/(\\d+)/);
                    if (aMatch && bMatch) {
                        const aRatio = parseInt(aMatch[1]) / parseInt(aMatch[2]);
                        const bRatio = parseInt(bMatch[1]) / parseInt(bMatch[2]);
                        comparison = aRatio - bRatio;
                    } else {
                        comparison = aValue.localeCompare(bValue);
                    }
                } else { // Texto - alfabético
                    comparison = aValue.localeCompare(bValue);
                }
                
                console.log('Comparison result:', comparison, 'sortOrder:', sortOrder);
                return sortOrder === 'asc' ? comparison : -comparison;
            });
            console.log('Sort completed');
            
            // Log del orden después del sorting
            console.log('Order after sorting:');
            rows.forEach((row, index) => {
                const cellValue = row.cells[columnIndex] ? row.cells[columnIndex].textContent.trim() : 'N/A';
                console.log('Sorted row', index, ':', cellValue);
            });
            
            // Reorganizar las filas en el DOM
            console.log('Reorganizing rows in DOM...');
            rows.forEach((row, index) => {
                console.log('Moving row', index, 'to position', index);
                tbody.appendChild(row);
            });
            
            // Verificar que el sorting funcionó
            console.log('Final row order:');
            const finalRows = Array.from(tbody.querySelectorAll('tr'));
            finalRows.forEach((row, index) => {
                const cellValue = row.cells[columnIndex] ? row.cells[columnIndex].textContent.trim() : 'N/A';
                console.log('Row', index, ':', cellValue);
            });
            
            console.log('Table sorted by column', columnIndex, 'in', sortOrder, 'order');
        }
        
        // Asegurar que el DOM esté cargado
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, sorting functions ready');
        });
        """

    def _get_charts_javascript(self, results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Generates JavaScript for interactive charts."""
        if not results:
            return ""
        
        # Prepare data for charts
        scores = [r.get('retention_score', 0.0) for r in results]
        passed_count = metrics['passed']
        failed_count = metrics['failed']
        
        # Get real temporal and comparison data
        temporal_data = self._get_temporal_data()
        comparison_data = self._get_comparison_data()
        
        # Data for facts analysis
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
        // Real data for charts
        const temporalData = {json.dumps(temporal_data)};
        const comparisonData = {json.dumps(comparison_data)};
        
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
        
        // Gráfico de análisis de retención de facts
        const factRetentionCtx = document.getElementById('factRetentionChart').getContext('2d');
        
        // Use real temporal data for fact retention scores
        const factRetentionData = temporalData.fact_retention_scores || [];
        const factRetentionLabels = temporalData.labels || [];
        
        window.chartInstances.factRetention = new Chart(factRetentionCtx, {{
            type: 'line',
            data: {{
                labels: factRetentionLabels.length > 0 ? factRetentionLabels : ['No Data'],
                datasets: [{{
                    label: 'Fact Retention Rate',
                    data: factRetentionData.length > 0 ? factRetentionData : [0],
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#17a2b8',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
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
                                return value.toFixed(0) + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Fact Retention Analysis'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Fact Retention: ' + context.parsed.y.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        
        // Gráfico de tendencia semanal
        const weeklyTrendCtx = document.getElementById('weeklyTrendChart').getContext('2d');
        
        // Use real temporal data
        let currentTarget = 80;
        const targetData = temporalData.labels.map(() => currentTarget);
        
        window.chartInstances.weeklyTrend = new Chart(weeklyTrendCtx, {{
            type: 'line',
            data: {{
                labels: temporalData.labels.length > 0 ? temporalData.labels : ['No Data'],
                datasets: [{{
                    label: 'Pass Rate %',
                    data: temporalData.scores.length > 0 ? temporalData.scores : [0],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}, {{
                    label: 'Target',
                    data: temporalData.labels.length > 0 ? targetData : [currentTarget],
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
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value.toFixed(0) + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Performance vs Target'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'Pass Rate: ' + context.parsed.y.toFixed(1) + '%';
                                }} else {{
                                    return 'Target: ' + context.parsed.y.toFixed(0) + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Función para actualizar el target dinámicamente
        function updateTarget(newTarget) {{
            currentTarget = parseFloat(newTarget);
            if (window.chartInstances.weeklyTrend) {{
                const labels = window.chartInstances.weeklyTrend.data.labels;
                const newTargetData = labels.map(() => currentTarget);
                window.chartInstances.weeklyTrend.data.datasets[1].data = newTargetData;
                window.chartInstances.weeklyTrend.data.datasets[1].label = 'Target (' + currentTarget + '%)';
                window.chartInstances.weeklyTrend.update();
            }}
        }}
        
        // Gráfico de tendencia de similarity scores
        const similarityTrendCtx = document.getElementById('similarityTrendChart').getContext('2d');
        
        // Use real temporal data for similarity scores
        const similarityData = temporalData.similarity_scores || [];
        const similarityLabels = temporalData.labels || [];
        
        window.chartInstances.similarityTrend = new Chart(similarityTrendCtx, {{
            type: 'line',
            data: {{
                labels: similarityLabels.length > 0 ? similarityLabels : ['No Data'],
                datasets: [{{
                    label: 'Average Similarity Score',
                    data: similarityData.length > 0 ? similarityData : [0],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#28a745',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
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
                                return value.toFixed(0) + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Similarity Score Trend'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Similarity: ' + context.parsed.y.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Variables globales para los gráficos (ya inicializadas arriba)
        
        // Función para mostrar/ocultar detalles
        function toggleDetails(detailsId) {{
            const detailsRow = document.getElementById(detailsId);
            const button = document.getElementById('btn-' + detailsId);
            
            if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {{
                detailsRow.style.display = 'table-row';
                button.textContent = 'Hide Details';
                button.classList.add('expanded');
            }} else {{
                detailsRow.style.display = 'none';
                button.textContent = 'View Details';
                button.classList.remove('expanded');
            }}
        }}
        
        
        
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
        
        // Función para generar datos temporales según el período usando datos reales
        function generateTemporalData(period) {{
            // Use the real temporal data that was passed from Python
            const realData = temporalData;
            const currentTarget = parseFloat(document.getElementById('targetInput').value) || 80;
            
            // If we have real data, use it
            if (realData && realData.labels && realData.labels.length > 0) {{
                const labels = realData.labels;
                const scores = realData.scores;
                const targets = labels.map(() => currentTarget);
                const similarity_scores = realData.similarity_scores || [];
                const fact_retention_scores = realData.fact_retention_scores || [];
                
                return {{ labels, scores, targets, similarity_scores, fact_retention_scores }};
            }}
            
            // Fallback: return empty data if no real data available
            return {{ 
                labels: ['No Data'], 
                scores: [0], 
                targets: [currentTarget],
                similarity_scores: [0],
                fact_retention_scores: [0]
            }};
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
    <p>Generated by True Lies Validator v0.9.1</p>
    <p><a href="mailto:patominer@gmail.com">patominer@gmail.com</a></p>
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
        
        .results-table th.sortable {
            cursor: pointer;
            user-select: none;
            position: relative;
            transition: background-color 0.2s ease;
        }
        
        .results-table th.sortable:hover {
            background-color: #e9ecef;
        }
        
        .sort-indicator {
            margin-left: 8px;
            font-size: 12px;
            color: #6c757d;
            transition: color 0.2s ease;
        }
        
        .results-table th.sortable:hover .sort-indicator {
            color: #007bff;
        }
        
        .results-table th.sort-asc .sort-indicator {
            color: #007bff;
        }
        
        .results-table th.sort-asc .sort-indicator::after {
            content: " ↑";
        }
        
        .results-table th.sort-desc .sort-indicator {
            color: #007bff;
        }
        
        .results-table th.sort-desc .sort-indicator::after {
            content: " ↓";
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
        
        .btn-details.expanded {
            background: #dc3545;
        }
        
        .btn-details.expanded:hover {
            background: #c82333;
        }
        
        .details-row td {
            background: #f8f9fa;
            border-top: none;
            padding: 20px;
            border-left: 4px solid #007bff;
        }
        
        .details-row {
            transition: all 0.3s ease;
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
        
        .query-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
            margin-bottom: 20px;
        }
        
        .query-section h4 {
            margin-top: 0;
            margin-bottom: 15px;
            color: #495057;
            font-size: 1.1rem;
        }
        
        .query-display {
            background: white;
            padding: 15px;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 1rem;
            line-height: 1.6;
            color: #333;
            border: 1px solid #e9ecef;
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
        
        .text-content.query-text {
            border-left-color: #9c27b0;
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
        
        .chart-container.chart-wide {
            grid-column: span 2;
        }
        
        .chart-container.chart-centered {
            grid-column: span 2;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-width: 500px;
            margin: 0 auto;
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
        
        .target-control {
            margin-bottom: 15px;
            text-align: center;
        }
        
        .target-control label {
            font-weight: bold;
            color: #495057;
            margin-right: 10px;
        }
        
        .target-control input {
            width: 80px;
            padding: 5px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            text-align: center;
            font-size: 0.9rem;
        }
        
        .target-control input:focus {
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


class ResultsHistory:
    """
    Manages historical validation results for temporal analysis.
    
    Stores execution data in JSON format for generating real performance metrics.
    """
    
    def __init__(self, history_file="validation_history.json", retention_days=30):
        """
        Initialize results history manager.
        
        Args:
            history_file: Name of the history file
            retention_days: Number of days to retain historical data
        """
        self.history_dir = Path("true_lies_reporting")
        self.history_dir.mkdir(exist_ok=True)
        
        self.history_file = self.history_dir / history_file
        self.retention_days = retention_days
        self.history_data = self._load_history()
    
    def _load_history(self) -> Dict[str, Any]:
        """Load historical data from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                return {"executions": []}
        return {"executions": []}
    
    def _save_history(self):
        """Save historical data to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save history: {e}")
    
    def _cleanup_old_data(self):
        """Remove executions older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_iso = cutoff_date.isoformat()
        
        original_count = len(self.history_data["executions"])
        self.history_data["executions"] = [
            exec_data for exec_data in self.history_data["executions"]
            if exec_data["timestamp"] >= cutoff_iso
        ]
        
        removed_count = original_count - len(self.history_data["executions"])
        if removed_count > 0:
            print(f"Cleaned up {removed_count} old execution records")
    
    def save_execution(self, execution_data: Dict[str, Any]):
        """
        Save a new execution to history.
        
        Args:
            execution_data: Dictionary containing execution metrics
        """
        # Add timestamp if not present
        if "timestamp" not in execution_data:
            execution_data["timestamp"] = datetime.now().isoformat()
        
        # Add to history
        self.history_data["executions"].append(execution_data)
        
        # Cleanup old data
        self._cleanup_old_data()
        
        # Save to file
        self._save_history()
    
    def _get_most_recent_per_day(self, executions: List[Dict]) -> List[Dict]:
        """Get only the most recent execution for each day."""
        from collections import defaultdict
        
        # Group by day
        daily_executions = defaultdict(list)
        for exec_data in executions:
            exec_date = datetime.fromisoformat(exec_data["timestamp"])
            day_key = exec_date.strftime("%Y-%m-%d")
            daily_executions[day_key].append(exec_data)
        
        # Keep only the most recent execution per day
        most_recent_executions = []
        for day_executions in daily_executions.values():
            # Sort by timestamp and take the most recent
            day_executions.sort(key=lambda x: x["timestamp"])
            most_recent_executions.append(day_executions[-1])
        
        # Sort all executions by timestamp
        most_recent_executions.sort(key=lambda x: x["timestamp"])
        return most_recent_executions
    
    def get_temporal_data(self, period: str, periods_back: int = 4) -> Dict[str, Any]:
        """
        Get aggregated temporal data for performance trends.
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            periods_back: Number of periods to look back
            
        Returns:
            Dictionary with labels, scores, and counts
        """
        executions = self.history_data["executions"]
        if not executions:
            return {"labels": [], "scores": [], "counts": []}
        
        # Always keep only the most recent execution per day for all periods
        # This ensures consistent data regardless of period (daily, weekly, monthly)
        executions = self._get_most_recent_per_day(executions)
        
        # Group executions by period
        grouped_data = self._group_by_period(executions, period)
        
        # Get last N periods
        periods = sorted(grouped_data.keys())[-periods_back:]
        
        labels = []
        scores = []
        counts = []
        similarity_scores = []
        fact_retention_scores = []
        
        for period_key in periods:
            period_executions = grouped_data[period_key]
            
            # Since we filtered to most recent per day, we should have only one execution
            if len(period_executions) == 1:
                execution = period_executions[0]
                pass_rate = execution["pass_rate"]
                total_tests = execution["total_candidates"]
                avg_similarity = execution.get("avg_similarity_score", 0.0)
                fact_retention = execution.get("avg_factual_accuracy", 0.0)
            else:
                # Fallback: take the most recent if somehow we have multiple
                period_executions.sort(key=lambda x: x["timestamp"])
                execution = period_executions[-1]
                pass_rate = execution["pass_rate"]
                total_tests = execution["total_candidates"]
                avg_similarity = execution.get("avg_similarity_score", 0.0)
                fact_retention = execution.get("avg_factual_accuracy", 0.0)
            
            labels.append(self._format_period_label(period_key, period))
            scores.append(round(pass_rate, 1))
            counts.append(total_tests)
            similarity_scores.append(round(avg_similarity * 100, 1))  # Convert to percentage
            fact_retention_scores.append(round(fact_retention, 1))  # Already in percentage
        
        return {
            "labels": labels,
            "scores": scores,
            "counts": counts,
            "similarity_scores": similarity_scores,
            "fact_retention_scores": fact_retention_scores
        }
    
    def get_comparison_data(self) -> Dict[str, Any]:
        """
        Get data for performance comparison (current vs previous vs historical).
        
        Returns:
            Dictionary with comparison metrics
        """
        executions = self.history_data["executions"]
        if not executions:
            return {
                "current_period": 0,
                "previous_period": 0,
                "historical_average": 0,
                "target": 80
            }
        
        # Sort by timestamp
        executions.sort(key=lambda x: x["timestamp"])
        
        # Calculate current period (last 7 days)
        current_cutoff = datetime.now() - timedelta(days=7)
        current_executions = [
            exec_data for exec_data in executions
            if datetime.fromisoformat(exec_data["timestamp"]) >= current_cutoff
        ]
        
        # Calculate previous period (7-14 days ago)
        previous_start = datetime.now() - timedelta(days=14)
        previous_end = datetime.now() - timedelta(days=7)
        previous_executions = [
            exec_data for exec_data in executions
            if previous_start <= datetime.fromisoformat(exec_data["timestamp"]) < previous_end
        ]
        
        # Calculate metrics
        current_rate = self._calculate_pass_rate(current_executions)
        previous_rate = self._calculate_pass_rate(previous_executions)
        historical_rate = self._calculate_pass_rate(executions)
        
        return {
            "current_period": round(current_rate, 1),
            "previous_period": round(previous_rate, 1),
            "historical_average": round(historical_rate, 1),
            "target": 80
        }
    
    def _group_by_period(self, executions: List[Dict], period: str) -> Dict[str, List[Dict]]:
        """Group executions by time period."""
        grouped = {}
        
        for exec_data in executions:
            exec_date = datetime.fromisoformat(exec_data["timestamp"])
            
            if period == "daily":
                period_key = exec_date.strftime("%Y-%m-%d")
            elif period == "weekly":
                # Get Monday of the week
                monday = exec_date - timedelta(days=exec_date.weekday())
                period_key = monday.strftime("%Y-%m-%d")
            elif period == "monthly":
                period_key = exec_date.strftime("%Y-%m")
            else:
                continue
            
            if period_key not in grouped:
                grouped[period_key] = []
            grouped[period_key].append(exec_data)
        
        return grouped
    
    def _format_period_label(self, period_key: str, period: str) -> str:
        """Format period key for display."""
        if period == "daily":
            date_obj = datetime.strptime(period_key, "%Y-%m-%d")
            return date_obj.strftime("%m/%d")
        elif period == "weekly":
            date_obj = datetime.strptime(period_key, "%Y-%m-%d")
            return f"Week {date_obj.strftime('%m/%d')}"
        elif period == "monthly":
            date_obj = datetime.strptime(period_key, "%Y-%m")
            return date_obj.strftime("%b %Y")
        return period_key
    
    def _calculate_pass_rate(self, executions: List[Dict]) -> float:
        """Calculate average pass rate from executions."""
        if not executions:
            return 0.0
        
        total_tests = sum(exec_data["total_candidates"] for exec_data in executions)
        total_passed = sum(exec_data["passed"] for exec_data in executions)
        
        return (total_passed / total_tests * 100) if total_tests > 0 else 0.0
