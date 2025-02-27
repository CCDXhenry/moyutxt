#!/usr/bin/env python3

import os
import json
import time
from typing import Dict, List

# 添加按键检测所需的模块
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix
    import sys
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class BookReader:
    def __init__(self):
        self.bookshelf_file = "bookshelf.json"
        self.bookshelf = self.load_bookshelf()
        self.chapter_markers = ["第", "章"]  # 用于识别章节的标记
        
    def load_bookshelf(self) -> Dict:
        """加载书架数据"""
        if os.path.exists(self.bookshelf_file):
            with open(self.bookshelf_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_bookshelf(self):
        """保存书架数据"""
        with open(self.bookshelf_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookshelf, f, ensure_ascii=False, indent=2)
    
    def import_book(self, filepath: str):
        """导入新书到书架"""
        # 规范化文件路径，处理反斜杠问题
        filepath = os.path.normpath(filepath.strip('"'))
        
        if not os.path.exists(filepath):
            print(f"文件不存在！路径：{filepath}")
            return
        
        # 尝试不同的编码格式
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'ansi']
        content = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("无法识别文件编码格式！")
            return
        
        try:
            book_name = os.path.basename(filepath)
            self.bookshelf[book_name] = {
                "content": content,
                "progress": 0,
                "total_lines": len(content.split('\n')),
                "last_read": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_bookshelf()
            print(f"成功导入《{book_name}》")
        except Exception as e:
            print(f"导入失败：{str(e)}")
    
    def get_chapters(self, lines: List[str]) -> List[tuple]:
        """获取章节列表，返回(行号, 章节名)的列表"""
        chapters = []
        for i, line in enumerate(lines):
            line = line.strip()
            if all(marker in line for marker in self.chapter_markers):
                chapters.append((i, line))
        return chapters

    def show_chapters(self, chapters: List[tuple]):
        """显示章节列表"""
        print("\n" + "="*50)
        print("章节列表：")
        print("="*50)
        for idx, (_, chapter_name) in enumerate(chapters, 1):
            print(f"{idx}. {chapter_name}")
        print("-"*50)

    def read_book(self, book_identifier: str):
        """阅读指定的书籍"""
        # 尝试将输入转换为数字（序号）
        try:
            if book_identifier.isdigit():
                idx = int(book_identifier)
                if idx < 1 or idx > len(self.bookshelf):
                    print("无效的书籍序号！")
                    return
                book_name = list(self.bookshelf.keys())[idx-1]
            else:
                book_name = book_identifier
                if book_name not in self.bookshelf:
                    print("该书籍不在书架中！")
                    return
        except:
            print("无效的输入！")
            return
        
        book = self.bookshelf[book_name]
        lines = book["content"].split('\n')
        current_line = book["progress"]
        chapters = self.get_chapters(lines)
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "="*50)
            print(f"正在阅读：《{book_name}》")
            print(f"进度：{current_line}/{book['total_lines']}")
            print("="*50)
            print("操作说明：")
            print("n: 下一页  p: 上一页")
            print("j: 下一章  k: 上一章")
            print("c: 选择章节  q: 退出")
            print("="*50 + "\n")
            
            # 显示当前页面（显示10行）
            for i in range(current_line, min(current_line + 10, len(lines))):
                print(lines[i])
            
            # 获取按键输入
            if os.name == 'nt':
                cmd = msvcrt.getch()
                if ord(cmd) == 27:  # ESC键
                    os.system('cls' if os.name == 'nt' else 'clear')
                    os._exit(0)
                cmd = cmd.decode('utf-8').lower()
            else:
                cmd = getch()
                if ord(cmd) == 27:  # ESC键
                    os.system('cls' if os.name == 'nt' else 'clear')
                    os._exit(0)
                cmd = cmd.lower()
            
            if cmd == 'j':  # 下一章
                # 找到当前行所在的章节
                current_chapter_idx = -1
                for idx, (line_num, _) in enumerate(chapters):
                    if line_num > current_line:
                        break
                    current_chapter_idx = idx
                
                # 跳转到下一章
                if current_chapter_idx < len(chapters) - 1:
                    current_line = chapters[current_chapter_idx + 1][0]
                    # 自动保存进度
                    self.bookshelf[book_name]["progress"] = current_line
                    self.bookshelf[book_name]["last_read"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.save_bookshelf()
            
            elif cmd == 'k':  # 上一章
                # 找到当前行所在的章节
                current_chapter_idx = -1
                for idx, (line_num, _) in enumerate(chapters):
                    if line_num >= current_line:
                        break
                    current_chapter_idx = idx
                
                # 跳转到上一章
                if current_chapter_idx > 0:
                    current_line = chapters[current_chapter_idx - 1][0]
                    # 自动保存进度
                    self.bookshelf[book_name]["progress"] = current_line
                    self.bookshelf[book_name]["last_read"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.save_bookshelf()
            
            elif cmd == 'c':
                self.show_chapters(chapters)
                try:
                    chapter_idx = int(input("请输入要跳转的章节序号：")) - 1
                    if 0 <= chapter_idx < len(chapters):
                        current_line = chapters[chapter_idx][0]
                        # 自动保存进度
                        self.bookshelf[book_name]["progress"] = current_line
                        self.bookshelf[book_name]["last_read"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        self.save_bookshelf()
                    else:
                        print("无效的章节序号！")
                        time.sleep(1)
                except ValueError:
                    print("请输入有效的数字！")
                    time.sleep(1)
            elif cmd == 'n':
                current_line = min(current_line + 10, len(lines))
                # 自动保存进度
                self.bookshelf[book_name]["progress"] = current_line
                self.bookshelf[book_name]["last_read"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_bookshelf()
            elif cmd == 'p':
                current_line = max(0, current_line - 10)
                # 自动保存进度
                self.bookshelf[book_name]["progress"] = current_line
                self.bookshelf[book_name]["last_read"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_bookshelf()
            elif cmd == 'q':
                break
    
    def show_bookshelf(self):
        """显示书架"""
        if not self.bookshelf:
            print("书架为空！")
            return
        
        print("\n" + "="*50)
        print("我的书架：")
        print("="*50)
        
        for idx, (book_name, book_info) in enumerate(self.bookshelf.items(), 1):
            print(f"{idx}. 《{book_name}》")
            print(f"   进度：{book_info['progress']}/{book_info['total_lines']}")
            print(f"   上次阅读：{book_info['last_read']}")
            print("-"*50)

def main():
    try:
        reader = BookReader()
        
        while True:
            print("\n=== 墨鱼阅读器 ===")
            print("1. 导入新书")
            print("2. 查看书架")
            print("3. 阅读书籍")
            print("4. 退出")
            
            choice = input("请选择操作：")
            
            if choice == '1':
                filepath = input("请输入txt文件路径：")
                reader.import_book(filepath)
            elif choice == '2':
                reader.show_bookshelf()
            elif choice == '3':
                reader.show_bookshelf()
                book_identifier = input("请输入要阅读的书籍序号或名称：")
                reader.read_book(book_identifier)
            elif choice == '4':
                print("感谢使用墨鱼阅读器！")
                break
            else:
                print("无效的选择！")
    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        os._exit(0)

if __name__ == "__main__":
    main()