"""
报告生成器
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器，用于生成各种格式的分析报告"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'data/reports'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, analysis_data: Dict[str, Any], report_type: str = 'comprehensive') -> Dict[str, str]:
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        reports = {}
        
        if report_type in ['comprehensive', 'json']:
            json_report = self._generate_json_report(analysis_data, timestamp)
            reports['json'] = json_report
        
        if report_type in ['comprehensive', 'csv']:
            csv_report = self._generate_csv_report(analysis_data, timestamp)
            reports['csv'] = csv_report
        
        if report_type in ['comprehensive', 'html']:
            html_report = self._generate_html_report(analysis_data, timestamp)
            reports['html'] = html_report
        
        if report_type in ['comprehensive', 'markdown']:
            markdown_report = self._generate_markdown_report(analysis_data, timestamp)
            reports['markdown'] = markdown_report
        
        return reports
    
    def _generate_json_report(self, analysis_data: Dict[str, Any], timestamp: str) -> str:
        """生成JSON报告"""
        report_file = self.output_dir / f"analysis_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            return ""
    
    def _generate_csv_report(self, analysis_data: Dict[str, Any], timestamp: str) -> str:
        """生成CSV报告"""
        report_file = self.output_dir / f"analysis_report_{timestamp}.csv"
        
        try:
            with open(report_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入总体统计
                writer.writerow(['指标类型', '指标名称', '数值'])
                
                overall = analysis_data.get('overall', {})
                writer.writerow(['总体', '总文件数', overall.get('total_files', 0)])
                writer.writerow(['总体', '总行数', overall.get('total_lines', 0)])
                writer.writerow(['总体', '总大小', overall.get('total_size', 0)])
                writer.writerow(['总体', '总问题数', overall.get('total_issues', 0)])
                writer.writerow(['总体', '总复杂度', overall.get('total_complexity', 0)])
                
                # 写入语言分布
                language_dist = overall.get('language_distribution', {})
                for lang, count in language_dist.items():
                    writer.writerow(['语言分布', lang, count])
                
                # 写入质量指标
                quality = analysis_data.get('quality', {})
                writer.writerow(['质量', '平均问题数', quality.get('avg_issues_per_file', 0)])
                writer.writerow(['质量', '平均质量分数', quality.get('avg_quality_score', 0)])
                
                # 写入复杂度指标
                complexity = analysis_data.get('complexity', {})
                writer.writerow(['复杂度', '平均复杂度', complexity.get('avg_complexity', 0)])
                writer.writerow(['复杂度', '最大复杂度', complexity.get('max_complexity', 0)])
                
                # 写入维护性指标
                maintainability = analysis_data.get('maintainability', {})
                writer.writerow(['维护性', '平均维护性分数', maintainability.get('avg_maintainability_score', 0)])
                writer.writerow(['维护性', '可维护文件数', maintainability.get('maintainable_files', 0)])
                writer.writerow(['维护性', '难以维护文件数', maintainability.get('difficult_to_maintain_files', 0)])
                
                # 写入可读性指标
                readability = analysis_data.get('readability', {})
                writer.writerow(['可读性', '平均可读性分数', readability.get('avg_readability_score', 0)])
                writer.writerow(['可读性', '高可读性文件数', readability.get('highly_readable_files', 0)])
                writer.writerow(['可读性', '难以阅读文件数', readability.get('difficult_to_read_files', 0)])
                
                # 写入测试覆盖率指标
                test_coverage = analysis_data.get('test_coverage', {})
                writer.writerow(['测试覆盖率', '测试文件数', test_coverage.get('test_files', 0)])
                writer.writerow(['测试覆盖率', '源文件数', test_coverage.get('source_files', 0)])
                writer.writerow(['测试覆盖率', '测试比例', test_coverage.get('test_ratio', 0)])
                writer.writerow(['测试覆盖率', '覆盖率估计', test_coverage.get('test_coverage_estimate', 0)])
            
            logger.info(f"CSV报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"生成CSV报告失败: {e}")
            return ""
    
    def _generate_html_report(self, analysis_data: Dict[str, Any], timestamp: str) -> str:
        """生成HTML报告"""
        report_file = self.output_dir / f"analysis_report_{timestamp}.html"
        
        try:
            html_content = self._create_html_content(analysis_data)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return ""
    
    def _create_html_content(self, analysis_data: Dict[str, Any]) -> str:
        """创建HTML内容"""
        overall = analysis_data.get('overall', {})
        quality = analysis_data.get('quality', {})
        complexity = analysis_data.get('complexity', {})
        maintainability = analysis_data.get('maintainability', {})
        readability = analysis_data.get('readability', {})
        test_coverage = analysis_data.get('test_coverage', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码分析报告</title>
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
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #555;
            margin-top: 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .language-dist {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .language-item {{
            background-color: #e9ecef;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 14px;
        }}
        .chart-container {{
            width: 100%;
            height: 300px;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>代码分析报告</h1>
        <p style="text-align: center; color: #666;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="section">
            <h2>总体统计</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{overall.get('total_files', 0)}</div>
                    <div class="metric-label">总文件数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall.get('total_lines', 0):,}</div>
                    <div class="metric-label">总行数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall.get('total_size', 0) / 1024 / 1024:.1f} MB</div>
                    <div class="metric-label">总大小</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall.get('total_issues', 0)}</div>
                    <div class="metric-label">总问题数</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>语言分布</h2>
            <div class="language-dist">
                {self._generate_language_distribution_html(overall.get('language_distribution', {}))}
            </div>
        </div>
        
        <div class="section">
            <h2>代码质量</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{quality.get('avg_issues_per_file', 0):.1f}</div>
                    <div class="metric-label">平均问题数/文件</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{quality.get('avg_quality_score', 0):.1f}</div>
                    <div class="metric-label">平均质量分数</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>代码复杂度</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{complexity.get('avg_complexity', 0):.1f}</div>
                    <div class="metric-label">平均复杂度</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{complexity.get('max_complexity', 0)}</div>
                    <div class="metric-label">最大复杂度</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>维护性</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{maintainability.get('avg_maintainability_score', 0):.1f}</div>
                    <div class="metric-label">平均维护性分数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{maintainability.get('maintainable_files', 0)}</div>
                    <div class="metric-label">可维护文件数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{maintainability.get('difficult_to_maintain_files', 0)}</div>
                    <div class="metric-label">难以维护文件数</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>可读性</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{readability.get('avg_readability_score', 0):.1f}</div>
                    <div class="metric-label">平均可读性分数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{readability.get('highly_readable_files', 0)}</div>
                    <div class="metric-label">高可读性文件数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{readability.get('difficult_to_read_files', 0)}</div>
                    <div class="metric-label">难以阅读文件数</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>测试覆盖率</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{test_coverage.get('test_files', 0)}</div>
                    <div class="metric-label">测试文件数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{test_coverage.get('source_files', 0)}</div>
                    <div class="metric-label">源文件数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{test_coverage.get('test_coverage_estimate', 0):.1f}%</div>
                    <div class="metric-label">覆盖率估计</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_language_distribution_html(self, language_dist: Dict[str, int]) -> str:
        """生成语言分布HTML"""
        total_files = sum(language_dist.values())
        if total_files == 0:
            return ""
        
        html_items = []
        for lang, count in sorted(language_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            html_items.append(f'<div class="language-item">{lang}: {count} ({percentage:.1f}%)</div>')
        
        return ''.join(html_items)
    
    def _generate_markdown_report(self, analysis_data: Dict[str, Any], timestamp: str) -> str:
        """生成Markdown报告"""
        report_file = self.output_dir / f"analysis_report_{timestamp}.md"
        
        try:
            markdown_content = self._create_markdown_content(analysis_data)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            return ""
    
    def _create_markdown_content(self, analysis_data: Dict[str, Any]) -> str:
        """创建Markdown内容"""
        overall = analysis_data.get('overall', {})
        quality = analysis_data.get('quality', {})
        complexity = analysis_data.get('complexity', {})
        maintainability = analysis_data.get('maintainability', {})
        readability = analysis_data.get('readability', {})
        test_coverage = analysis_data.get('test_coverage', {})
        
        markdown = f"""# 代码分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计

| 指标 | 数值 |
|------|------|
| 总文件数 | {overall.get('total_files', 0)} |
| 总行数 | {overall.get('total_lines', 0):,} |
| 总大小 | {overall.get('total_size', 0) / 1024 / 1024:.1f} MB |
| 总问题数 | {overall.get('total_issues', 0)} |
| 总复杂度 | {overall.get('total_complexity', 0)} |

## 语言分布

"""
        
        # 添加语言分布
        language_dist = overall.get('language_distribution', {})
        total_files = sum(language_dist.values())
        if total_files > 0:
            for lang, count in sorted(language_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_files) * 100
                markdown += f"- **{lang}**: {count} 文件 ({percentage:.1f}%)\n"
        
        markdown += f"""
## 代码质量

| 指标 | 数值 |
|------|------|
| 平均问题数/文件 | {quality.get('avg_issues_per_file', 0):.1f} |
| 平均质量分数 | {quality.get('avg_quality_score', 0):.1f} |

## 代码复杂度

| 指标 | 数值 |
|------|------|
| 平均复杂度 | {complexity.get('avg_complexity', 0):.1f} |
| 最大复杂度 | {complexity.get('max_complexity', 0)} |

## 维护性

| 指标 | 数值 |
|------|------|
| 平均维护性分数 | {maintainability.get('avg_maintainability_score', 0):.1f} |
| 可维护文件数 | {maintainability.get('maintainable_files', 0)} |
| 难以维护文件数 | {maintainability.get('difficult_to_maintain_files', 0)} |

## 可读性

| 指标 | 数值 |
|------|------|
| 平均可读性分数 | {readability.get('avg_readability_score', 0):.1f} |
| 高可读性文件数 | {readability.get('highly_readable_files', 0)} |
| 难以阅读文件数 | {readability.get('difficult_to_read_files', 0)} |

## 测试覆盖率

| 指标 | 数值 |
|------|------|
| 测试文件数 | {test_coverage.get('test_files', 0)} |
| 源文件数 | {test_coverage.get('source_files', 0)} |
| 测试比例 | {test_coverage.get('test_ratio', 0):.2f} |
| 覆盖率估计 | {test_coverage.get('test_coverage_estimate', 0):.1f}% |

## 建议

基于以上分析，建议：

1. **代码质量**: 关注平均问题数，考虑增加代码审查
2. **复杂度**: 如果平均复杂度过高，考虑重构复杂函数
3. **维护性**: 关注难以维护的文件，考虑拆分或重构
4. **可读性**: 提高代码可读性，增加注释和文档
5. **测试覆盖率**: 增加测试文件以提高代码覆盖率

---
*此报告由 RopeDP 工具自动生成*
"""
        
        return markdown

