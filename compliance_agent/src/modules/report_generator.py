import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from ..config import OUTPUT_DIR, REPORT_CONFIG, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ComplianceReport:
    report_id: str
    compliance_level: str
    total_score: int
    issues: List[Dict]
    issue_count: int
    suggestions: List[str]
    checked_at: str
    input_summary: Dict
    rules_version: str


class ReportGenerator:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"compliance_report_{timestamp}"
    
    def generate_summary(self, compliance_result: Dict, 
                         processed_input: Dict) -> Dict:
        issues = compliance_result.get("issues", [])
        
        issue_summary = {}
        for issue in issues:
            issue_type = issue.get("type", "未知")
            if issue_type not in issue_summary:
                issue_summary[issue_type] = []
            issue_summary[issue_type].append(issue.get("word", ""))
        
        level_count = {}
        for issue in issues:
            level = issue.get("level", "unknown")
            level_count[level] = level_count.get(level, 0) + 1
        
        return {
            "compliance_level": compliance_result.get("compliance_level", "未知"),
            "total_score": compliance_result.get("total_score", 0),
            "total_issues": len(issues),
            "issue_summary": issue_summary,
            "level_count": level_count,
            "has_critical": level_count.get("critical", 0) > 0,
            "has_high": level_count.get("high", 0) > 0
        }
    
    def generate_suggestions(self, compliance_result: Dict) -> List[str]:
        issues = compliance_result.get("issues", [])
        suggestions = []
        
        for issue in issues:
            if "suggestion" in issue:
                suggestions.append(issue["suggestion"])
        
        return list(set(suggestions))
    
    def create_input_summary(self, processed_input: Dict) -> Dict:
        return {
            "video_text_length": len(processed_input.get("video_text", "")),
            "note_text_length": len(processed_input.get("note_text", "")),
            "combined_text_length": len(processed_input.get("combined_text", "")),
            "nutrition_data": processed_input.get("nutrition_data", {}),
            "nutrition_claims": processed_input.get("nutrition_claims", []),
            "has_report": bool(processed_input.get("report_data", {}))
        }
    
    def generate_report(self, compliance_result: Dict, 
                        processed_input: Dict) -> ComplianceReport:
        report_id = self.generate_report_id()
        suggestions = self.generate_suggestions(compliance_result)
        input_summary = self.create_input_summary(processed_input)
        
        report = ComplianceReport(
            report_id=report_id,
            compliance_level=compliance_result.get("compliance_level", "未知"),
            total_score=compliance_result.get("total_score", 0),
            issues=compliance_result.get("issues", []),
            issue_count=compliance_result.get("issue_count", 0),
            suggestions=suggestions,
            checked_at=compliance_result.get("checked_at", datetime.now().isoformat()),
            input_summary=input_summary,
            rules_version=compliance_result.get("rules_version", "1.0")
        )
        
        logger.info(f"Report generated: {report_id}")
        return report
    
    def save_json_report(self, report: ComplianceReport, 
                         filename: Optional[str] = None) -> str:
        if filename is None:
            filename = f"{report.report_id}.json"
        
        filepath = self.output_dir / filename
        
        report_data = asdict(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON report saved: {filepath}")
        return str(filepath)
    
    def save_text_report(self, report: ComplianceReport, 
                         filename: Optional[str] = None) -> str:
        if filename is None:
            filename = f"{report.report_id}.txt"
        
        filepath = self.output_dir / filename
        
        lines = []
        lines.append("=" * 60)
        lines.append("合规审核报告")
        lines.append("=" * 60)
        lines.append(f"报告ID: {report.report_id}")
        lines.append(f"审核时间: {report.checked_at}")
        lines.append(f"合规等级: {report.compliance_level}")
        lines.append(f"总分: {report.total_score}")
        lines.append(f"违规数量: {report.issue_count}")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append("输入摘要")
        lines.append("-" * 60)
        lines.append(f"视频文本长度: {report.input_summary.get('video_text_length', 0)}")
        lines.append(f"笔记文本长度: {report.input_summary.get('note_text_length', 0)}")
        lines.append(f"合并文本长度: {report.input_summary.get('combined_text_length', 0)}")
        lines.append(f"营养数据: {report.input_summary.get('nutrition_data', {})}")
        lines.append(f"营养声明: {report.input_summary.get('nutrition_claims', [])}")
        lines.append("")
        
        if report.issues:
            lines.append("-" * 60)
            lines.append("违规详情")
            lines.append("-" * 60)
            
            for i, issue in enumerate(report.issues, 1):
                lines.append(f"\n[{i}] {issue.get('type', '未知')}")
                lines.append(f"    等级: {issue.get('level', 'unknown')}")
                lines.append(f"    关键词: {issue.get('word', '')}")
                lines.append(f"    描述: {issue.get('description', '')}")
                lines.append(f"    依据: {issue.get('basis', '')}")
                lines.append(f"    建议: {issue.get('suggestion', '')}")
            lines.append("")
        
        if report.suggestions:
            lines.append("-" * 60)
            lines.append("修改建议")
            lines.append("-" * 60)
            for i, suggestion in enumerate(report.suggestions, 1):
                lines.append(f"{i}. {suggestion}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"规则版本: {report.rules_version}")
        lines.append("=" * 60)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Text report saved: {filepath}")
        return str(filepath)
    
    def save_html_report(self, report: ComplianceReport, 
                         filename: Optional[str] = None) -> str:
        if filename is None:
            filename = f"{report.report_id}.html"
        
        filepath = self.output_dir / filename
        
        level_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#28a745"
        }
        
        compliance_colors = {
            "严重违规": "#dc3545",
            "一般违规": "#fd7e14",
            "建议优化": "#ffc107",
            "通过": "#28a745"
        }
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合规审核报告 - {report.report_id}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #333; margin-bottom: 10px; }}
        .compliance-badge {{ display: inline-block; padding: 10px 30px; border-radius: 20px; color: white; font-weight: bold; font-size: 18px; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary h2 {{ color: #333; margin-top: 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .summary-item {{ background-color: white; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }}
        .summary-item h3 {{ margin: 0 0 10px 0; color: #666; font-size: 14px; }}
        .summary-item .value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .issues {{ margin-top: 30px; }}
        .issues h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .issue {{ background-color: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #ccc; }}
        .issue.critical {{ border-left-color: #dc3545; }}
        .issue.high {{ border-left-color: #fd7e14; }}
        .issue.medium {{ border-left-color: #ffc107; }}
        .issue.low {{ border-left-color: #28a745; }}
        .issue-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .issue-type {{ font-weight: bold; font-size: 16px; }}
        .issue-level {{ padding: 3px 10px; border-radius: 12px; color: white; font-size: 12px; }}
        .issue-detail {{ margin: 5px 0; color: #666; }}
        .suggestions {{ margin-top: 30px; }}
        .suggestions h2 {{ color: #333; border-bottom: 2px solid #28a745; padding-bottom: 10px; }}
        .suggestion {{ background-color: #d4edda; padding: 12px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #28a745; }}
        .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>合规审核报告</h1>
            <p>报告ID: {report.report_id}</p>
            <p>审核时间: {report.checked_at}</p>
            <div class="compliance-badge" style="background-color: {compliance_colors.get(report.compliance_level, '#333')};">
                {report.compliance_level}
            </div>
        </div>
        
        <div class="summary">
            <h2>审核摘要</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>违规数量</h3>
                    <div class="value">{report.issue_count}</div>
                </div>
                <div class="summary-item">
                    <h3>总分</h3>
                    <div class="value">{report.total_score}</div>
                </div>
                <div class="summary-item">
                    <h3>文本长度</h3>
                    <div class="value">{report.input_summary.get('combined_text_length', 0)}</div>
                </div>
                <div class="summary-item">
                    <h3>营养声明</h3>
                    <div class="value">{len(report.input_summary.get('nutrition_claims', []))}</div>
                </div>
            </div>
        </div>
        
        <div class="issues">
            <h2>违规详情</h2>
        """
        
        if report.issues:
            for issue in report.issues:
                level = issue.get('level', 'unknown')
                html += f"""
            <div class="issue {level}">
                <div class="issue-header">
                    <span class="issue-type">{issue.get('type', '未知')}</span>
                    <span class="issue-level" style="background-color: {level_colors.get(level, '#666')};">
                        {level.upper()}
                    </span>
                </div>
                <div class="issue-detail"><strong>关键词:</strong> {issue.get('word', '')}</div>
                <div class="issue-detail"><strong>描述:</strong> {issue.get('description', '')}</div>
                <div class="issue-detail"><strong>依据:</strong> {issue.get('basis', '')}</div>
                <div class="issue-detail"><strong>建议:</strong> {issue.get('suggestion', '')}</div>
            </div>
        """
        else:
            html += """
            <div class="issue" style="border-left-color: #28a745;">
                <div class="issue-detail" style="color: #28a745; font-weight: bold;">
                    ✓ 未发现违规项，内容符合相关法规要求
                </div>
            </div>
        """
        
        html += """
        </div>
        """
        
        if report.suggestions:
            html += """
        <div class="suggestions">
            <h2>修改建议</h2>
        """
            for suggestion in report.suggestions:
                html += f"""
            <div class="suggestion">
                {suggestion}
            </div>
        """
            html += """
        </div>
        """
        
        html += f"""
        <div class="footer">
            <p>规则版本: {report.rules_version} | 合规审核Agent自动生成</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML report saved: {filepath}")
        return str(filepath)
    
    def generate_all_formats(self, compliance_result: Dict, 
                             processed_input: Dict) -> Dict[str, str]:
        report = self.generate_report(compliance_result, processed_input)
        
        output_files = {}
        
        if REPORT_CONFIG.get("save_to_file", True):
            output_files["json"] = self.save_json_report(report)
            output_files["txt"] = self.save_text_report(report)
            output_files["html"] = self.save_html_report(report)
        
        logger.info(f"All reports generated: {output_files}")
        return output_files
