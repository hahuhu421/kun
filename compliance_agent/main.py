import argparse
import sys
import logging
from pathlib import Path

from src.config import LOG_FILE
from src.modules.input_processor import InputProcessor
from src.modules.compliance_checker import ComplianceChecker
from src.modules.report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ComplianceAgent:
    def __init__(self):
        self.input_processor = InputProcessor()
        self.compliance_checker = ComplianceChecker()
        self.report_generator = ReportGenerator()
        logger.info("Compliance Agent initialized")
    
    def check_video_note(self, video_path: str = None, 
                         note_text: str = "", 
                         report_path: str = None) -> dict:
        logger.info("Starting compliance check")
        
        processed_input = self.input_processor.process_input(
            video_path=video_path,
            note_text=note_text,
            report_path=report_path
        )
        
        compliance_result = self.compliance_checker.check_compliance(processed_input)
        
        output_files = self.report_generator.generate_all_formats(
            compliance_result, 
            processed_input
        )
        
        result = {
            "compliance_level": compliance_result["compliance_level"],
            "total_score": compliance_result["total_score"],
            "issue_count": compliance_result["issue_count"],
            "issues": compliance_result["issues"],
            "suggestions": self.report_generator.generate_suggestions(compliance_result),
            "output_files": output_files
        }
        
        logger.info(f"Compliance check completed: {result['compliance_level']}")
        return result
    
    def check_text_only(self, text: str) -> dict:
        return self.check_video_note(note_text=text)
    
    def check_with_report(self, text: str, report_path: str) -> dict:
        return self.check_video_note(note_text=text, report_path=report_path)


def main():
    parser = argparse.ArgumentParser(
        description="合规审核Agent - 用于审核视频笔记内容的合规性"
    )
    
    parser.add_argument(
        "--video", "-v",
        type=str,
        help="视频文件路径"
    )
    
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="笔记文本内容"
    )
    
    parser.add_argument(
        "--report", "-r",
        type=str,
        help="检测报告PDF文件路径"
    )
    
    parser.add_argument(
        "--text-file", "-f",
        type=str,
        help="包含笔记文本的文件路径"
    )
    
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["json", "txt", "html", "all"],
        default="all",
        help="输出报告格式"
    )
    
    args = parser.parse_args()
    
    note_text = ""
    
    if args.text:
        note_text = args.text
    elif args.text_file:
        text_file = Path(args.text_file)
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                note_text = f.read()
        else:
            logger.error(f"Text file not found: {args.text_file}")
            sys.exit(1)
    
    if not note_text and not args.video:
        logger.error("Please provide either text (--text or --text-file) or video (--video)")
        parser.print_help()
        sys.exit(1)
    
    agent = ComplianceAgent()
    
    result = agent.check_video_note(
        video_path=args.video,
        note_text=note_text,
        report_path=args.report
    )
    
    print("\n" + "=" * 60)
    print("合规审核结果")
    print("=" * 60)
    print(f"合规等级: {result['compliance_level']}")
    print(f"总分: {result['total_score']}")
    print(f"违规数量: {result['issue_count']}")
    print("=" * 60)
    
    if result['issues']:
        print("\n违规详情:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"\n[{i}] {issue['type']} ({issue['level']})")
            print(f"    关键词: {issue['word']}")
            print(f"    描述: {issue['description']}")
            print(f"    建议: {issue['suggestion']}")
    
    if result['suggestions']:
        print("\n修改建议:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"{i}. {suggestion}")
    
    print("\n" + "=" * 60)
    print("报告文件:")
    for format_type, filepath in result['output_files'].items():
        print(f"  {format_type.upper()}: {filepath}")
    print("=" * 60)
    
    return result


def demo():
    print("=" * 60)
    print("合规审核Agent - 演示模式")
    print("=" * 60)
    
    agent = ComplianceAgent()
    
    demo_texts = [
        "这款产品是最佳的，低糖无负担，能量100kJ。",
        "我们的产品永不过敏，治愈一切疾病，百分百有效。",
        "这款饼干是低糖食品，糖含量3g/100g，营养丰富。",
        "纯天然有机食品，无任何添加，绝对安全。"
    ]
    
    for i, text in enumerate(demo_texts, 1):
        print(f"\n{'=' * 60}")
        print(f"演示 {i}: {text}")
        print("=" * 60)
        
        result = agent.check_text_only(text)
        
        print(f"合规等级: {result['compliance_level']}")
        print(f"违规数量: {result['issue_count']}")
        
        if result['issues']:
            print("\n违规项:")
            for issue in result['issues']:
                print(f"  - {issue['type']}: {issue['word']}")
        
        if result['suggestions']:
            print("\n建议:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    else:
        main()
