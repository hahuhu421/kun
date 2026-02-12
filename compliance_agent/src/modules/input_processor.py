import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import fitz
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from ..config import WHISPER_CONFIG, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InputProcessor:
    def __init__(self):
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            self._load_whisper_model()
    
    def _load_whisper_model(self):
        import torch
        
        try:
            logger.info(f"开始加载 Whisper 模型: {WHISPER_CONFIG['model_size']}")
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用设备: {device}")
            
            self.whisper_model = whisper.load_model(
                WHISPER_CONFIG["model_size"],
                device=device
            )
            
            logger.info(f"Whisper model {WHISPER_CONFIG['model_size']} loaded successfully on {device}")
            
        except MemoryError as e:
            error_msg = f"内存不足，无法加载 Whisper 模型。请关闭其他程序或使用更小的模型。错误: {str(e)}"
            logger.error(error_msg)
            self.whisper_model = None
        except Exception as e:
            error_msg = f"Whisper 模型加载失败: {type(e).__name__} - {str(e)}"
            logger.error(error_msg)
            self.whisper_model = None
    
    def transcribe_video(self, video_path: str) -> str:
        if not WHISPER_AVAILABLE:
            error_msg = "Whisper 未安装，请运行: pip install openai-whisper"
            logger.warning(error_msg)
            return f"[错误] {error_msg}"
        
        if self.whisper_model is None:
            error_msg = "Whisper 模型加载失败，请检查系统资源"
            logger.warning(error_msg)
            return f"[错误] {error_msg}"
        
        if not video_path:
            error_msg = "未提供视频文件路径"
            logger.warning(error_msg)
            return f"[错误] {error_msg}"
        
        # 检查ffmpeg是否可用
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            error_msg = "ffmpeg 未安装，无法处理视频文件\n\n解决方案:\n  1. 安装 ffmpeg: https://ffmpeg.org/download.html\n  2. 将 ffmpeg 添加到系统 PATH\n  3. 重启应用后重试"
            logger.error(error_msg)
            return f"[错误] {error_msg}"
        
        try:
            # 增强 Windows 路径处理
            video_path = video_path.replace('\\', '/')
            video_path_obj = Path(video_path)
            
            # 尝试解析路径
            try:
                resolved_path = video_path_obj.resolve()
                logger.info(f"原始路径: {video_path}")
                logger.info(f"解析后路径: {resolved_path}")
            except Exception as e:
                logger.warning(f"路径解析失败: {e}")
                resolved_path = video_path_obj
            
            # 检查文件存在性
            if not resolved_path.exists():
                # 尝试修复常见路径问题
                potential_paths = [
                    Path(video_path),
                    Path(video_path.replace('/', '\\')),
                    Path(video_path.replace('\\', '/')),
                    Path(video_path.strip()),
                ]
                
                existing_paths = []
                for path in potential_paths:
                    if path.exists():
                        existing_paths.append(str(path))
                
                if existing_paths:
                    error_msg = f"视频文件不存在: {video_path}\n\n可能的正确路径:\n" + "\n".join(f"  - {p}" for p in existing_paths)
                else:
                    error_msg = f"视频文件不存在: {video_path}\n\n检查建议:\n  1. 确认文件路径正确\n  2. 检查文件是否存在\n  3. 尝试使用项目目录下的文件\n  4. 重命名为简单英文名"
                
                logger.warning(error_msg)
                return f"[错误] {error_msg}"
            
            # 检查是否为文件
            if not resolved_path.is_file():
                error_msg = f"路径不是文件: {video_path}\n\n检查建议:\n  1. 确认选择的是文件而不是文件夹\n  2. 检查路径格式是否正确\n  3. 尝试使用绝对路径"
                logger.warning(error_msg)
                return f"[错误] {error_msg}"
            
            # 检查文件大小
            file_size = resolved_path.stat().st_size
            if file_size == 0:
                error_msg = f"视频文件为空: {video_path}\n\n检查建议:\n  1. 确认文件已完整下载\n  2. 检查文件是否损坏\n  3. 尝试使用其他视频文件"
                logger.warning(error_msg)
                return f"[错误] {error_msg}"
            
            logger.info(f"开始转录视频: {resolved_path} (大小: {file_size / (1024*1024):.2f} MB)")
            
            # 验证文件可访问性
            try:
                with open(resolved_path, 'rb') as f:
                    logger.info("文件可正常打开")
            except Exception as e:
                logger.error(f"文件打开失败: {type(e).__name__}: {str(e)}")
                error_msg = f"无法读取视频文件: {str(e)}\n\n检查建议:\n  1. 检查文件权限\n  2. 确认文件未被其他程序占用\n  3. 尝试复制文件到项目目录"
                return f"[错误] {error_msg}"
            
            # 尝试将文件复制到项目目录下，使用更简单的路径
            import shutil
            import tempfile
            
            try:
                # 创建临时目录
                temp_dir = Path(__file__).parent.parent.parent / "temp"
                temp_dir.mkdir(exist_ok=True)
                
                # 复制文件到临时目录
                temp_video_path = temp_dir / resolved_path.name
                logger.info(f"复制文件到临时目录: {temp_video_path}")
                
                shutil.copy2(resolved_path, temp_video_path)
                logger.info(f"文件复制成功: {temp_video_path}")
                
                # 验证复制的文件存在
                if not temp_video_path.exists():
                    logger.error("临时文件不存在")
                    raise FileNotFoundError("无法创建临时文件")
                
                # 使用相对路径格式
                import os
                relative_path = os.path.relpath(temp_video_path)
                relative_path_str = relative_path.replace('\\', '/')
                logger.info(f"使用相对路径: {relative_path_str}")
                
                result = self.whisper_model.transcribe(
                    relative_path_str,
                    language=WHISPER_CONFIG.get("language", "zh"),
                    task=WHISPER_CONFIG.get("task", "transcribe")
                )
                
                logger.info("使用临时文件转录成功")
                
            except Exception as e:
                logger.error(f"临时文件处理失败: {type(e).__name__}: {str(e)}")
                
                # 如果临时文件方法失败，尝试直接使用原始路径
                try:
                    logger.info("尝试使用原始路径格式")
                    result = self.whisper_model.transcribe(
                        str(resolved_path),
                        language=WHISPER_CONFIG.get("language", "zh"),
                        task=WHISPER_CONFIG.get("task", "transcribe")
                    )
                    logger.info("原始路径格式成功")
                except Exception as e:
                    logger.error(f"所有路径格式都失败: {type(e).__name__}: {str(e)}")
                    error_msg = f"视频转录失败: {str(e)}\n\n检查建议:\n  1. 将视频文件复制到项目目录下\n  2. 使用英文文件名，避免特殊字符\n  3. 确保文件路径不包含空格\n  4. 尝试使用更小的视频文件"
                    return f"[错误] {error_msg}"
            
            text = result.get("text", "")
            
            if not text or text.strip() == "":
                logger.warning("视频转录结果为空")
                return "[提示] 视频转录成功，但未检测到语音内容\n\n可能原因:\n  1. 视频没有语音\n  2. 音量过低\n  3. 语音不是中文\n  4. 视频损坏"
            
            logger.info(f"Video transcribed successfully: {len(text)} characters")
            return text
            
        except PermissionError as e:
            error_msg = f"文件权限不足，无法访问视频: {str(e)}\n\n检查建议:\n  1. 以管理员身份运行应用\n  2. 检查文件权限设置\n  3. 复制文件到其他位置"
            logger.error(error_msg)
            return f"[错误] {error_msg}"
        except OSError as e:
            error_code = getattr(e, 'winerror', None)
            if error_code == 2:
                error_msg = f"系统找不到指定的文件: {video_path}\n\n检查建议:\n  1. 确认文件路径正确\n  2. 检查文件是否存在\n  3. 尝试使用项目目录下的文件\n  4. 重命名为简单英文名"
            elif error_code == 3:
                error_msg = f"系统找不到指定的路径: {video_path}\n\n检查建议:\n  1. 确认路径格式正确\n  2. 检查文件夹是否存在\n  3. 尝试使用绝对路径"
            else:
                error_msg = f"文件访问错误: {type(e).__name__} - {str(e)}\n\n检查建议:\n  1. 检查文件是否被其他程序占用\n  2. 检查磁盘空间\n  3. 尝试复制文件到其他位置"
            logger.error(error_msg)
            return f"[错误] {error_msg}"
        except Exception as e:
            error_msg = f"视频转录失败: {type(e).__name__} - {str(e)}\n\n可能原因:\n  1. 视频格式不支持\n  2. 视频损坏\n  3. 系统资源不足\n  4. Whisper 模型问题\n\n建议:\n  1. 尝试其他视频文件\n  2. 重启应用\n  3. 检查日志文件获取详细信息"
            logger.error(error_msg)
            return f"[错误] {error_msg}"
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        noise_patterns = [
            r'\[.*?\]',
            r'\(.*?\)',
            r'<.*?>',
            r'♪.*?♪',
            r'\*.*?\*'
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_nutrition_data(self, text: str) -> Dict[str, float]:
        nutrition_data = {}
        
        patterns = {
            "能量": r'能量[：:]\s*(\d+\.?\d*)\s*(kJ|千焦|kcal|千卡)',
            "蛋白质": r'蛋白质[：:]\s*(\d+\.?\d*)\s*',
            "脂肪": r'脂肪[：:]\s*(\d+\.?\d*)\s*',
            "饱和脂肪": r'饱和脂肪[：:]\s*(\d+\.?\d*)\s*',
            "碳水化合物": r'碳水化合物[：:]\s*(\d+\.?\d*)\s*',
            "糖": r'糖[：:]\s*(\d+\.?\d*)\s*',
            "钠": r'钠[：:]\s*(\d+\.?\d*)\s*(mg|毫克)'
        }
        
        for nutrient, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0][0])
                    nutrition_data[nutrient] = value
                except (IndexError, ValueError):
                    continue
        
        logger.info(f"Extracted nutrition data: {nutrition_data}")
        return nutrition_data
    
    def extract_nutrition_claims(self, text: str) -> List[str]:
        claims = []
        
        claim_patterns = [
            r'低糖',
            r'无糖',
            r'低脂',
            r'无脂',
            r'低钠',
            r'高蛋白',
            r'零添加',
            r'纯天然',
            r'有机',
            r'全麦',
            r'无添加',
            r'脱脂',
            r'减盐',
            r'减油',
            r'减糖'
        ]
        
        for pattern in claim_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                claims.append(pattern)
        
        logger.info(f"Extracted nutrition claims: {claims}")
        return claims
    
    def parse_pdf_report(self, pdf_path: str) -> Dict[str, any]:
        if not PDF_AVAILABLE:
            logger.warning("PyMuPDF not available, cannot parse PDF")
            return {}
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            
            report_data = {
                "text": text,
                "nutrition_data": self.extract_nutrition_data(text),
                "extracted_at": datetime.now().isoformat()
            }
            
            logger.info(f"PDF parsed successfully: {len(text)} characters")
            return report_data
            
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            return {}
    
    def process_input(self, video_path: Optional[str] = None, 
                     note_text: str = "",
                     report_path: Optional[str] = None) -> Dict[str, any]:
        result = {
            "video_text": "",
            "note_text": note_text,
            "combined_text": note_text,
            "nutrition_data": {},
            "nutrition_claims": [],
            "report_data": {},
            "processed_at": datetime.now().isoformat()
        }
        
        if video_path and Path(video_path).exists():
            result["video_text"] = self.transcribe_video(video_path)
            result["combined_text"] = result["video_text"] + " " + result["note_text"]
        
        result["combined_text"] = self.clean_text(result["combined_text"])
        result["note_text"] = self.clean_text(result["note_text"])
        
        result["nutrition_data"] = self.extract_nutrition_data(result["combined_text"])
        result["nutrition_claims"] = self.extract_nutrition_claims(result["combined_text"])
        
        if report_path and Path(report_path).exists():
            result["report_data"] = self.parse_pdf_report(report_path)
        
        logger.info("Input processing completed")
        return result
    
    def extract_value_from_text(self, text: str, keyword: str) -> Optional[float]:
        pattern = rf'{keyword}[：:]\s*(\d+\.?\d*)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None
