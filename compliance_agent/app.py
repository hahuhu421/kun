import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from datetime import datetime

from src.config import LOG_FILE
from src.modules.input_processor import InputProcessor
from src.modules.compliance_checker import ComplianceChecker
from src.modules.report_generator import ReportGenerator

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ComplianceAgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("合规审核Agent")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        self.input_processor = InputProcessor()
        self.compliance_checker = ComplianceChecker()
        self.report_generator = ReportGenerator()
        
        self.video_path = ""
        self.report_path = ""
        self.current_result = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="合规审核Agent",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=(0, 15))
        
        video_frame = ctk.CTkFrame(input_frame)
        video_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            video_frame, 
            text="视频文件:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(15, 10))
        
        self.video_path_label = ctk.CTkLabel(video_frame, text="未选择文件", text_color="gray")
        self.video_path_label.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            video_frame, 
            text="选择视频",
            command=self.select_video,
            width=120
        ).pack(side="left", padx=(0, 15))
        
        report_frame = ctk.CTkFrame(input_frame)
        report_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            report_frame, 
            text="检测报告:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(15, 10))
        
        self.report_path_label = ctk.CTkLabel(report_frame, text="未选择文件", text_color="gray")
        self.report_path_label.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            report_frame, 
            text="选择报告",
            command=self.select_report,
            width=120
        ).pack(side="left", padx=(0, 15))
        
        text_frame = ctk.CTkFrame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(
            text_frame, 
            text="笔记文本内容:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.text_input = ctk.CTkTextbox(text_frame, height=150)
        self.text_input.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.text_input.insert("1.0", "请输入或粘贴笔记文本内容...")
        self.text_input.bind("<FocusIn>", self.on_text_focus)
        
        transcribe_frame = ctk.CTkFrame(main_frame)
        transcribe_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(
            transcribe_frame, 
            text="视频转录文本 (自动解析):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.transcribe_text = ctk.CTkTextbox(transcribe_frame, height=150)
        self.transcribe_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.transcribe_text.insert("1.0", "选择视频后，点击开始审核将自动转录...")
        self.transcribe_text.configure(state="disabled")
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            button_frame, 
            text="开始审核",
            command=self.start_check,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#164e7a"
        ).pack(side="left", padx=15, pady=15)
        
        ctk.CTkButton(
            button_frame, 
            text="清空",
            command=self.clear_all,
            height=40,
            width=120
        ).pack(side="right", padx=15, pady=15)
        
        ctk.CTkButton(
            button_frame, 
            text="打开报告",
            command=self.open_report,
            height=40,
            width=120
        ).pack(side="right", padx=(0, 10), pady=15)
        
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            result_frame, 
            text="审核结果:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(result_frame)
        self.result_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.result_text.insert("1.0", "等待审核...")
        self.result_text.configure(state="disabled")
        
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()
    
    def on_text_focus(self, event):
        if self.text_input.get("1.0", "end-1c") == "请输入或粘贴笔记文本内容...":
            self.text_input.delete("1.0", "end")
    
    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            from pathlib import Path
            
            # 增强路径处理
            file_path = file_path.replace('\\', '/')
            path_obj = Path(file_path)
            
            # 尝试解析路径
            try:
                resolved_path = path_obj.resolve()
                print(f"原始路径: {file_path}")
                print(f"解析后路径: {resolved_path}")
            except Exception as e:
                print(f"路径解析失败: {e}")
                resolved_path = path_obj
            
            # 检查文件存在性
            if not resolved_path.exists():
                # 尝试修复常见路径问题
                potential_paths = [
                    Path(file_path),
                    Path(file_path.replace('/', '\\')),
                    Path(file_path.replace('\\', '/')),
                    Path(file_path.strip()),
                ]
                
                existing_paths = []
                for path in potential_paths:
                    if path.exists():
                        existing_paths.append(str(path))
                
                if existing_paths:
                    message = f"文件不存在：{file_path}\n\n可能的正确路径:\n" + "\n".join(f"  - {p}" for p in existing_paths)
                else:
                    message = f"文件不存在：{file_path}\n\n检查建议:\n  1. 确认文件路径正确\n  2. 检查文件是否存在\n  3. 尝试使用项目目录下的文件\n  4. 重命名为简单英文名"
                
                messagebox.showerror("错误", message)
                return
            
            # 检查是否为文件
            if not resolved_path.is_file():
                message = f"路径不是文件：{file_path}\n\n检查建议:\n  1. 确认选择的是文件而不是文件夹\n  2. 检查路径格式是否正确\n  3. 尝试使用绝对路径"
                messagebox.showerror("错误", message)
                return
            
            # 检查文件大小
            file_size = resolved_path.stat().st_size
            if file_size == 0:
                message = f"视频文件为空：{file_path}\n\n检查建议:\n  1. 确认文件已完整下载\n  2. 检查文件是否损坏\n  3. 尝试使用其他视频文件"
                messagebox.showerror("错误", message)
                return
            
            # 检查文件扩展名
            ext = resolved_path.suffix.lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
            if ext not in video_extensions:
                message = f"文件扩展名可能不是视频：{ext}\n\n支持的视频格式：{' '.join(video_extensions)}\n\n检查建议:\n  1. 确认文件是视频格式\n  2. 尝试使用其他视频文件"
                messagebox.showwarning("警告", message)
            
            # 保存解析后的路径
            self.video_path = str(resolved_path)
            self.video_path_label.configure(text=resolved_path.name, text_color="black")
            
            # 显示成功提示
            messagebox.showinfo("成功", f"视频文件选择成功：\n{resolved_path.name}\n\n文件大小: {file_size / (1024*1024):.2f} MB")
            
        except PermissionError as e:
            message = f"文件权限不足，无法访问：{file_path}\n\n检查建议:\n  1. 以管理员身份运行应用\n  2. 检查文件权限设置\n  3. 复制文件到其他位置"
            messagebox.showerror("错误", message)
        except Exception as e:
            message = f"选择文件失败：{str(e)}\n\n检查建议:\n  1. 确认文件路径正确\n  2. 检查文件是否被其他程序占用\n  3. 尝试复制文件到项目目录"
            messagebox.showerror("错误", message)
    
    def select_report(self):
        file_path = filedialog.askopenfilename(
            title="选择检测报告",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.report_path = file_path
            self.report_path_label.configure(text=Path(file_path).name, text_color="black")
    
    def start_check(self):
        note_text = self.text_input.get("1.0", "end-1c")
        
        if not note_text and not self.video_path:
            messagebox.showwarning("警告", "请输入文本或选择视频文件！")
            return
        
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))
        self.progress_bar.set(0.2)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "正在审核中，请稍候...\n")
        self.result_text.configure(state="disabled")
        self.root.update()
        
        thread = threading.Thread(target=self.run_check, args=(note_text,))
        thread.daemon = True
        thread.start()
    
    def update_progress(self, value):
        self.progress_bar.set(value)
    
    def run_check(self, note_text):
        try:
            self.progress_bar.set(0.2)
            self.root.after(100, lambda: None)
            
            if self.video_path:
                self.progress_bar.set(0.3)
                self.root.after(100, lambda: None)
                
                transcribed_text = self.input_processor.transcribe_video(self.video_path)
                
                self.root.after(0, lambda: self.display_transcribe(transcribed_text))
            
            self.progress_bar.set(0.4)
            self.root.after(100, lambda: None)
            
            video_path = self.video_path if self.video_path else None
            result = self.input_processor.process_input(
                video_path=video_path,
                note_text=note_text,
                report_path=self.report_path if self.report_path else None
            )
            
            self.progress_bar.set(0.6)
            self.root.after(100, lambda: None)
            
            compliance_result = self.compliance_checker.check_compliance(result)
            
            self.progress_bar.set(0.8)
            self.root.after(100, lambda: None)
            
            output_files = self.report_generator.generate_all_formats(
                compliance_result, 
                result
            )
            
            self.progress_bar.set(1.0)
            self.root.after(100, lambda: None)
            
            self.current_result = {
                "compliance_level": compliance_result["compliance_level"],
                "total_score": compliance_result["total_score"],
                "issue_count": compliance_result["issue_count"],
                "issues": compliance_result["issues"],
                "suggestions": self.report_generator.generate_suggestions(compliance_result),
                "output_files": output_files
            }
            
            self.root.after(0, self.display_result)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
    
    def display_transcribe(self, text):
        self.transcribe_text.configure(state="normal")
        self.transcribe_text.delete("1.0", "end")
        
        if text:
            if text.startswith("[错误]"):
                self.transcribe_text.insert("1.0", f"❌ {text}")
            elif text.startswith("[提示]"):
                self.transcribe_text.insert("1.0", f"⚠️ {text}")
            else:
                self.transcribe_text.insert("1.0", f"✅ 视频转录成功！\n\n{text}")
        else:
            self.transcribe_text.insert("1.0", "❌ 视频转录失败：未返回任何内容\n\n可能原因：\n1. 视频没有语音内容\n2. 视频音频格式不支持\n3. Whisper模型未正确加载\n\n建议：\n- 检查视频是否包含中文语音\n- 尝试使用其他视频文件\n- 手动在上方笔记文本框中输入文案")
        
        self.transcribe_text.configure(state="disabled")
    
    def display_result(self):
        result = self.current_result
        
        output = "=" * 60 + "\n"
        output += "合规审核结果\n"
        output += "=" * 60 + "\n"
        output += f"审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"合规等级: {result['compliance_level']}\n"
        output += f"总分: {result['total_score']}\n"
        output += f"违规数量: {result['issue_count']}\n"
        output += "=" * 60 + "\n\n"
        
        if result['issues']:
            output += "违规详情:\n"
            for i, issue in enumerate(result['issues'], 1):
                output += f"\n[{i}] {issue['type']} ({issue['level']})\n"
                output += f"    关键词: {issue['word']}\n"
                output += f"    描述: {issue['description']}\n"
                output += f"    依据: {issue['basis']}\n"
                output += f"    建议: {issue['suggestion']}\n"
            output += "\n"
        
        if result['suggestions']:
            output += "修改建议:\n"
            for i, suggestion in enumerate(result['suggestions'], 1):
                output += f"{i}. {suggestion}\n"
            output += "\n"
        
        output += "=" * 60 + "\n"
        output += "报告文件:\n"
        for format_type, filepath in result['output_files'].items():
            output += f"  {format_type.upper()}: {filepath}\n"
        output += "=" * 60 + "\n"
        
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", output)
        self.result_text.configure(state="disabled")
        
        messagebox.showinfo("审核完成", f"审核完成！\n合规等级: {result['compliance_level']}\n违规数量: {result['issue_count']}")
    
    def show_error(self, error_msg):
        self.progress_bar.pack_forget()
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", f"审核失败: {error_msg}")
        self.result_text.configure(state="disabled")
        messagebox.showerror("错误", f"审核失败: {error_msg}")
    
    def clear_all(self):
        self.video_path = ""
        self.report_path = ""
        self.current_result = None
        
        self.video_path_label.configure(text="未选择文件", text_color="gray")
        self.report_path_label.configure(text="未选择文件", text_color="gray")
        
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", "请输入或粘贴笔记文本内容...")
        
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "等待审核...")
        self.result_text.configure(state="disabled")
        
        self.progress_bar.pack_forget()
    
    def open_report(self):
        if self.current_result and 'html' in self.current_result['output_files']:
            import webbrowser
            webbrowser.open(f"file:///{self.current_result['output_files']['html']}")
        else:
            messagebox.showinfo("提示", "请先进行审核，然后打开报告")


def main():
    root = ctk.CTk()
    app = ComplianceAgentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
