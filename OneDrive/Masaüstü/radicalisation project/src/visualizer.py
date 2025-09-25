"""
Visualization module for creating charts and reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

def create_html_report(data: Dict[str, Any], output_path: str = None) -> str:
    """Create an HTML report with visualizations"""
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/report_{timestamp}.html"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Radicalization Research Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .chart-section {{
            margin-bottom: 40px;
        }}
        .chart-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .data-table th, .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .data-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .data-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .category-Violence_CallToAction {{ color: #FF4444; }}
        .category-Group_Identity {{ color: #FF8800; }}
        .category-Delegitimisation_Dehumanisation {{ color: #CC0000; }}
        .category-Conspiracy_Polarising {{ color: #FFAA00; }}
        .category-Propaganda_Recruitment {{ color: #FF6600; }}
        .category-Religious_Radical {{ color: #8800FF; }}
        .category-PKK_Related {{ color: #0088FF; }}
        .category-Conversion_Identity {{ color: #00AA88; }}
        .platform-twitter {{ color: #1DA1F2; }}
        .platform-reddit {{ color: #FF4500; }}
        .platform-forum {{ color: #6B46C1; }}
        .platform-news {{ color: #374151; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Digital Radicalization Research Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
    
    # Add summary section
    if 'summary' in data:
        summary = data['summary']
        html_content += """
        <div class="summary-grid">
            <div class="summary-card">
                <h3>📊 Total Records</h3>
                <div class="value">{total_records}</div>
            </div>
            <div class="summary-card">
                <h3>📈 Total Count</h3>
                <div class="value">{total_count}</div>
            </div>
            <div class="summary-card">
                <h3>🌐 Platforms</h3>
                <div class="value">{platform_count}</div>
            </div>
            <div class="summary-card">
                <h3>🗺️ Regions</h3>
                <div class="value">{region_count}</div>
            </div>
        </div>
        """.format(
            total_records=data.get('metadata', {}).get('total_records', 0),
            total_count=summary.get('total_count', 0),
            platform_count=len(summary.get('platforms', [])),
            region_count=len(summary.get('regions', []))
        )
        
        # Top categories section
        if 'top_categories' in summary:
            html_content += """
            <div class="chart-section">
                <div class="chart-title">🎯 Top Categories</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            total_cat_count = sum(summary['top_categories'].values())
            for category, count in summary['top_categories'].items():
                percentage = round((count / total_cat_count) * 100, 1) if total_cat_count > 0 else 0
                html_content += f"""
                        <tr>
                            <td class="category-{category}">{category.replace('_', ' ')}</td>
                            <td>{count}</td>
                            <td>{percentage}%</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </div>
            """
        
        # Platform distribution
        if 'platform_distribution' in summary:
            html_content += """
            <div class="chart-section">
                <div class="chart-title">📱 Platform Distribution</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            total_platform_count = sum(summary['platform_distribution'].values())
            for platform, count in summary['platform_distribution'].items():
                percentage = round((count / total_platform_count) * 100, 1) if total_platform_count > 0 else 0
                platform_icon = {'twitter': '🐦', 'reddit': '🤖', 'forum': '💬', 'news': '📰'}.get(platform, '🌐')
                html_content += f"""
                        <tr>
                            <td class="platform-{platform}">{platform_icon} {platform.title()}</td>
                            <td>{count}</td>
                            <td>{percentage}%</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </div>
            """
    
    # Data table section
    if 'data' in data and data['data']:
        html_content += """
        <div class="chart-section">
            <div class="chart-title">📋 Detailed Results</div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Region</th>
                        <th>Platform</th>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Sort data by count (descending)
        sorted_data = sorted(data['data'], key=lambda x: x.get('count', 0), reverse=True)
        
        for item in sorted_data[:50]:  # Show top 50 results
            html_content += f"""
                <tr>
                    <td>{item.get('week', 'N/A')}</td>
                    <td>{item.get('region', 'N/A')}</td>
                    <td class="platform-{item.get('platform', 'unknown')}">{item.get('platform', 'N/A').title()}</td>
                    <td class="category-{item.get('category', 'unknown')}">{item.get('category', 'N/A').replace('_', ' ')}</td>
                    <td><strong>{item.get('count', 0)}</strong></td>
                </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        """
    
    # Footer
    html_content += """
        <div class="footer">
            <p>Generated by Digital Radicalization Research System</p>
            <p><strong>Disclaimer:</strong> This tool is for research purposes only. Use responsibly and ethically.</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Save HTML file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(output_file)

def create_simple_chart(data: Dict[str, int], title: str = "Chart") -> str:
    """Create a simple ASCII bar chart"""
    if not data:
        return f"{title}: No data available"
    
    max_value = max(data.values())
    max_width = 50
    
    chart_lines = [f"\n{title}:", "=" * len(title)]
    
    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_width = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_width + "░" * (max_width - bar_width)
        percentage = f"({value}/{sum(data.values())} = {round(value/sum(data.values())*100, 1)}%)"
        chart_lines.append(f"{label:20} |{bar}| {value} {percentage}")
    
    return "\n".join(chart_lines)

def export_to_csv(data: List[Dict[str, Any]], output_path: str):
    """Export data to CSV format (simple implementation)"""
    if not data:
        return
    
    # Get all unique keys from the data
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    
    headers = sorted(list(all_keys))
    
    # Create CSV content
    csv_lines = [",".join(headers)]
    
    for item in data:
        row = []
        for header in headers:
            value = str(item.get(header, ""))
            # Simple CSV escaping
            if "," in value or '"' in value:
                value = '"' + value.replace('"', '""') + '"'
            row.append(value)
        csv_lines.append(",".join(row))
    
    # Save CSV file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(csv_lines))

def print_summary_report(data: Dict[str, Any]):
    """Print a formatted summary to console"""
    print("\n" + "=" * 60)
    print("🔍 DIGITAL RADICALIZATION RESEARCH SUMMARY")
    print("=" * 60)
    
    if 'metadata' in data:
        metadata = data['metadata']
        print(f"📅 Generated: {metadata.get('generated_at', 'Unknown')}")
        print(f"📊 Total Records: {metadata.get('total_records', 0)}")
    
    if 'summary' in data:
        summary = data['summary']
        print(f"\n📈 OVERVIEW:")
        print(f"   Total Count: {summary.get('total_count', 0)}")
        print(f"   Platforms: {len(summary.get('platforms', []))}")
        print(f"   Regions: {len(summary.get('regions', []))}")
        print(f"   Categories: {len(summary.get('categories', []))}")
        
        # Top categories chart
        if 'top_categories' in summary:
            print(create_simple_chart(summary['top_categories'], "🎯 TOP CATEGORIES"))
        
        # Platform distribution chart
        if 'platform_distribution' in summary:
            print(create_simple_chart(summary['platform_distribution'], "📱 PLATFORM DISTRIBUTION"))
    
    print("\n" + "=" * 60)