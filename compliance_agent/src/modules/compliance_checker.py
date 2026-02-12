import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ..config import RULES_FILE, COMPLIANCE_LEVELS, AI_CONFIG, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComplianceChecker:
    def __init__(self):
        self.rules = self._load_rules()
        self.classifier = None
        if TRANSFORMERS_AVAILABLE:
            self._load_ai_model()
    
    def _load_rules(self) -> Dict:
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            logger.info("Rules loaded successfully")
            return rules
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return {}
    
    def _load_ai_model(self):
        try:
            self.classifier = pipeline(
                "text-classification",
                model=AI_CONFIG.get("model", "bert-base-chinese"),
                device=-1 if not AI_CONFIG.get("use_gpu", False) else 0
            )
            logger.info("AI model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            self.classifier = None
    
    def check_absolute_words(self, text: str) -> List[Dict]:
        issues = []
        absolute_words = self.rules.get("广告法", {}).get("绝对化用语", [])
        
        for word in absolute_words:
            if word in text:
                issues.append({
                    "type": "绝对化用语",
                    "word": word,
                    "level": "high",
                    "description": f"检测到绝对化用语'{word}'",
                    "basis": self.rules.get("广告法", {}).get("条款说明", {}).get("绝对化用语", ""),
                    "suggestion": f"请删除或修改'{word}'，使用更客观的表述"
                })
        
        return issues
    
    def check_false_advertising(self, text: str) -> List[Dict]:
        issues = []
        keywords = self.rules.get("广告法", {}).get("虚假宣传关键词", [])
        
        for keyword in keywords:
            if keyword in text:
                issues.append({
                    "type": "虚假宣传",
                    "word": keyword,
                    "level": "critical",
                    "description": f"检测到虚假宣传关键词'{keyword}'",
                    "basis": self.rules.get("广告法", {}).get("条款说明", {}).get("虚假宣传", ""),
                    "suggestion": f"请删除'{keyword}'，避免使用绝对化表述"
                })
        
        return issues
    
    def check_medical_terms(self, text: str) -> List[Dict]:
        issues = []
        medical_terms = self.rules.get("广告法", {}).get("医疗相关禁用词", [])
        
        for term in medical_terms:
            if term in text:
                issues.append({
                    "type": "医疗相关",
                    "word": term,
                    "level": "critical",
                    "description": f"检测到医疗相关术语'{term}'",
                    "basis": self.rules.get("广告法", {}).get("条款说明", {}).get("医疗相关", ""),
                    "suggestion": f"请删除'{term}'，非医疗产品不得涉及疾病治疗功能"
                })
        
        return issues
    
    def check_negative_content(self, text: str) -> List[Dict]:
        issues = []
        negative_items = self.rules.get("广告法", {}).get("负面清单", [])
        
        for item in negative_items:
            if item in text:
                issues.append({
                    "type": "负面内容",
                    "word": item,
                    "level": "critical",
                    "description": f"检测到负面内容'{item}'",
                    "basis": "依据相关法律法规，禁止此类内容",
                    "suggestion": f"请删除'{item}'相关内容"
                })
        
        return issues
    
    def check_nutrition_claims(self, text: str, nutrition_data: Dict[str, float], 
                               claims: List[str]) -> List[Dict]:
        issues = []
        claim_thresholds = self.rules.get("GB28050", {}).get("营养声称阈值", {})
        
        for claim in claims:
            if claim in claim_thresholds:
                threshold_data = claim_thresholds[claim]
                threshold = threshold_data.get("固体", 0)
                
                if "糖" in nutrition_data:
                    sugar_value = nutrition_data["糖"]
                    if sugar_value > threshold:
                        issues.append({
                            "type": "营养声称不符",
                            "word": claim,
                            "level": "high",
                            "description": f"声明'{claim}'但糖含量{sugar_value}g/100g超过阈值{threshold}g/100g",
                            "basis": f"依据GB28050，{claim}要求{threshold_data.get('说明', '')}",
                            "suggestion": f"请删除'{claim}'声明或确保糖含量≤{threshold}g/100g"
                        })
        
        mandatory_labels = self.rules.get("GB28050", {}).get("强制标示", [])
        missing_labels = []
        
        for label in mandatory_labels:
            if label not in text and label not in nutrition_data:
                missing_labels.append(label)
        
        if missing_labels:
            issues.append({
                "type": "营养标签缺失",
                "word": ",".join(missing_labels),
                "level": "medium",
                "description": f"缺少强制标示的营养成分：{', '.join(missing_labels)}",
                "basis": "依据GB28050，必须标示能量、蛋白质、脂肪、碳水化合物、钠等营养成分",
                "suggestion": f"请补充标示：{', '.join(missing_labels)}"
            })
        
        return issues
    
    def check_report_consistency(self, declared_data: Dict[str, float], 
                                 report_data: Dict[str, float]) -> List[Dict]:
        issues = []
        error_threshold = self.rules.get("检测报告", {}).get("匹配检查", {}).get("误差阈值", 0.2)
        
        for nutrient, declared_value in declared_data.items():
            if nutrient in report_data:
                report_value = report_data[nutrient]
                if report_value > 0:
                    error_rate = abs(declared_value - report_value) / report_value
                    if error_rate > error_threshold:
                        issues.append({
                            "type": "检测报告不匹配",
                            "word": nutrient,
                            "level": "critical",
                            "description": f"{nutrient}声明值{declared_value}与报告值{report_value}误差{error_rate:.1%}超过阈值{error_threshold:.0%}",
                            "basis": "依据检测报告匹配检查要求",
                            "suggestion": f"请修改声明值或更新检测报告，确保误差≤{error_threshold:.0%}"
                        })
        
        return issues
    
    def ai_semantic_analysis(self, text: str) -> List[Dict]:
        issues = []
        
        if not TRANSFORMERS_AVAILABLE or self.classifier is None:
            logger.warning("AI model not available, skipping semantic analysis")
            return issues
        
        try:
            result = self.classifier(text[:512])
            
            if isinstance(result, list):
                result = result[0]
            
            label = result.get("label", "")
            score = result.get("score", 0)
            
            if "NEGATIVE" in label and score > 0.7:
                issues.append({
                    "type": "AI语义分析",
                    "word": "潜在违规",
                    "level": "medium",
                    "description": f"AI检测到潜在违规内容（置信度：{score:.2%}）",
                    "basis": "基于AI语义分析模型",
                    "suggestion": "建议人工复核该内容"
                })
            
        except Exception as e:
            logger.error(f"AI semantic analysis failed: {e}")
        
        return issues
    
    def check_compliance(self, processed_input: Dict) -> Dict:
        text = processed_input.get("combined_text", "")
        nutrition_data = processed_input.get("nutrition_data", {})
        nutrition_claims = processed_input.get("nutrition_claims", [])
        report_data = processed_input.get("report_data", {}).get("nutrition_data", {})
        
        issues = []
        
        issues.extend(self.check_absolute_words(text))
        issues.extend(self.check_false_advertising(text))
        issues.extend(self.check_medical_terms(text))
        issues.extend(self.check_negative_content(text))
        issues.extend(self.check_nutrition_claims(text, nutrition_data, nutrition_claims))
        
        if report_data:
            issues.extend(self.check_report_consistency(nutrition_data, report_data))
        
        issues.extend(self.ai_semantic_analysis(text))
        
        total_score = sum(COMPLIANCE_LEVELS.get(issue["level"], {}).get("score", 0) for issue in issues)
        
        compliance_level = "通过"
        if total_score >= COMPLIANCE_LEVELS["critical"]["score"]:
            compliance_level = "严重违规"
        elif total_score >= COMPLIANCE_LEVELS["high"]["score"]:
            compliance_level = "一般违规"
        elif total_score >= COMPLIANCE_LEVELS["medium"]["score"]:
            compliance_level = "建议优化"
        
        result = {
            "compliance_level": compliance_level,
            "total_score": total_score,
            "issues": issues,
            "issue_count": len(issues),
            "checked_at": datetime.now().isoformat(),
            "rules_version": "1.0"
        }
        
        logger.info(f"Compliance check completed: {compliance_level}, {len(issues)} issues found")
        return result
    
    def get_suggestions(self, issues: List[Dict]) -> List[str]:
        suggestions = []
        
        for issue in issues:
            if "suggestion" in issue:
                suggestions.append(issue["suggestion"])
        
        return list(set(suggestions))
