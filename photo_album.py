import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import json
import shutil
from datetime import datetime

class PhotoAlbum:
    def __init__(self, root):
        self.root = root
        self.root.title("사진 앨범")
        self.root.geometry("1000x700")
        
        # 변수 초기화
        self.current_image = None
        self.photo_list = []
        self.current_index = -1
        self.album_data = {}  # 앨범 정보 저장
        self.current_album = "기본 앨범"
        
        # UI 구성
        self.create_widgets()
        
        # 앨범 데이터 로드
        self.load_album_data()
        
    def create_widgets(self):
        # 메인 프레임
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽 프레임 (앨범 목록)
        self.left_frame = tk.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 앨범 목록 레이블
        self.album_label = tk.Label(self.left_frame, text="앨범 목록", font=("Arial", 12, "bold"))
        self.album_label.pack(pady=(0, 5))
        
        # 앨범 목록 트리뷰
        self.album_tree = ttk.Treeview(self.left_frame, selectmode="browse")
        self.album_tree.pack(fill=tk.BOTH, expand=True)
        self.album_tree.bind("<<TreeviewSelect>>", self.on_album_select)
        
        # 앨범 관리 버튼
        self.album_btn_frame = tk.Frame(self.left_frame)
        self.album_btn_frame.pack(fill=tk.X, pady=5)
        
        self.new_album_btn = tk.Button(self.album_btn_frame, text="새 앨범", command=self.create_new_album)
        self.new_album_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_album_btn = tk.Button(self.album_btn_frame, text="앨범 삭제", command=self.delete_album)
        self.delete_album_btn.pack(side=tk.LEFT, padx=2)
        
        # 오른쪽 프레임 (사진 표시 및 컨트롤)
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 상단 버튼 프레임
        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 사진 추가 버튼
        self.add_btn = tk.Button(self.button_frame, text="사진 추가", command=self.add_photos)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        # 이전/다음 버튼
        self.prev_btn = tk.Button(self.button_frame, text="이전", command=self.show_previous)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(self.button_frame, text="다음", command=self.show_next)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # 확대/축소 버튼
        self.zoom_in_btn = tk.Button(self.button_frame, text="확대", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_btn = tk.Button(self.button_frame, text="축소", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5)
        
        # 삭제 버튼
        self.delete_btn = tk.Button(self.button_frame, text="삭제", command=self.delete_photo)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 이미지 표시 영역
        self.image_frame = tk.Frame(self.right_frame, bg="lightgray")
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True)
        
        # 설명 입력
        self.description_frame = tk.Frame(self.right_frame)
        self.description_frame.pack(fill=tk.X, pady=10)
        
        self.description_label = tk.Label(self.description_frame, text="사진 설명:")
        self.description_label.pack(side=tk.LEFT, padx=5)
        
        self.description_entry = tk.Entry(self.description_frame, width=50)
        self.description_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.save_desc_btn = tk.Button(self.description_frame, text="설명 저장", command=self.save_description)
        self.save_desc_btn.pack(side=tk.LEFT, padx=5)
        
        # 상태 표시줄
        self.status_label = tk.Label(self.right_frame, text="사진을 선택해주세요", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        # 기본 앨범 추가
        self.add_album_to_tree("기본 앨범")
        
    def add_album_to_tree(self, album_name):
        self.album_tree.insert("", "end", text=album_name, values=(album_name,))
        if album_name not in self.album_data:
            self.album_data[album_name] = {
                "photos": [],
                "descriptions": {}
            }
    
    def create_new_album(self):
        album_name = tk.simpledialog.askstring("새 앨범", "앨범 이름을 입력하세요:")
        if album_name:
            if album_name in self.album_data:
                messagebox.showinfo("알림", "이미 존재하는 앨범 이름입니다.")
                return
            self.add_album_to_tree(album_name)
            self.save_album_data()
    
    def delete_album(self):
        selected_item = self.album_tree.selection()
        if not selected_item:
            messagebox.showinfo("알림", "삭제할 앨범을 선택하세요.")
            return
        
        album_name = self.album_tree.item(selected_item[0])["text"]
        if album_name == "기본 앨범":
            messagebox.showinfo("알림", "기본 앨범은 삭제할 수 없습니다.")
            return
        
        if messagebox.askyesno("확인", f"'{album_name}' 앨범을 삭제하시겠습니까?"):
            self.album_tree.delete(selected_item)
            del self.album_data[album_name]
            self.save_album_data()
            
            if self.current_album == album_name:
                self.current_album = "기본 앨범"
                self.photo_list = self.album_data["기본 앨범"]["photos"]
                self.current_index = -1
                self.show_current_image()
    
    def on_album_select(self, event):
        selected_item = self.album_tree.selection()
        if selected_item:
            album_name = self.album_tree.item(selected_item[0])["text"]
            self.current_album = album_name
            self.photo_list = self.album_data[album_name]["photos"]
            self.current_index = -1
            self.show_current_image()
    
    def add_photos(self):
        file_paths = filedialog.askopenfilenames(
            title="사진 선택",
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_paths:
            # 앨범 폴더 생성
            album_dir = os.path.join("albums", self.current_album)
            os.makedirs(album_dir, exist_ok=True)
            
            for file_path in file_paths:
                # 파일 복사
                filename = os.path.basename(file_path)
                new_path = os.path.join(album_dir, filename)
                shutil.copy2(file_path, new_path)
                
                # 앨범 데이터에 추가
                if new_path not in self.album_data[self.current_album]["photos"]:
                    self.album_data[self.current_album]["photos"].append(new_path)
            
            self.photo_list = self.album_data[self.current_album]["photos"]
            self.current_index = len(self.photo_list) - 1
            self.show_current_image()
            self.save_album_data()
    
    def show_current_image(self):
        if 0 <= self.current_index < len(self.photo_list):
            # 이미지 로드 및 크기 조정
            image = Image.open(self.photo_list[self.current_index])
            # 이미지 크기 조정 (최대 800x600)
            image.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(image)
            
            # 이미지 표시
            self.image_label.config(image=photo)
            self.image_label.image = photo
            
            # 설명 표시
            filename = os.path.basename(self.photo_list[self.current_index])
            if filename in self.album_data[self.current_album]["descriptions"]:
                self.description_entry.delete(0, tk.END)
                self.description_entry.insert(0, self.album_data[self.current_album]["descriptions"][filename])
            else:
                self.description_entry.delete(0, tk.END)
            
            # 상태 업데이트
            self.status_label.config(text=f"사진 {self.current_index + 1}/{len(self.photo_list)}")
        else:
            self.image_label.config(image="")
            self.description_entry.delete(0, tk.END)
            self.status_label.config(text="사진이 없습니다.")
    
    def show_previous(self):
        if self.photo_list:
            self.current_index = (self.current_index - 1) % len(self.photo_list)
            self.show_current_image()
    
    def show_next(self):
        if self.photo_list:
            self.current_index = (self.current_index + 1) % len(self.photo_list)
            self.show_current_image()
    
    def zoom_in(self):
        if 0 <= self.current_index < len(self.photo_list):
            image = Image.open(self.photo_list[self.current_index])
            # 현재 크기에서 1.2배 확대
            new_size = (int(image.width * 1.2), int(image.height * 1.2))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
    
    def zoom_out(self):
        if 0 <= self.current_index < len(self.photo_list):
            image = Image.open(self.photo_list[self.current_index])
            # 현재 크기에서 0.8배 축소
            new_size = (int(image.width * 0.8), int(image.height * 0.8))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
    
    def delete_photo(self):
        if 0 <= self.current_index < len(self.photo_list):
            if messagebox.askyesno("확인", "선택한 사진을 삭제하시겠습니까?"):
                # 파일 삭제
                os.remove(self.photo_list[self.current_index])
                
                # 앨범 데이터에서 삭제
                filename = os.path.basename(self.photo_list[self.current_index])
                if filename in self.album_data[self.current_album]["descriptions"]:
                    del self.album_data[self.current_album]["descriptions"][filename]
                
                self.photo_list.pop(self.current_index)
                self.album_data[self.current_album]["photos"] = self.photo_list
                
                # 인덱스 조정
                if self.photo_list:
                    self.current_index = min(self.current_index, len(self.photo_list) - 1)
                else:
                    self.current_index = -1
                
                self.show_current_image()
                self.save_album_data()
    
    def save_description(self):
        if 0 <= self.current_index < len(self.photo_list):
            filename = os.path.basename(self.photo_list[self.current_index])
            description = self.description_entry.get()
            self.album_data[self.current_album]["descriptions"][filename] = description
            self.save_album_data()
            messagebox.showinfo("알림", "설명이 저장되었습니다.")
    
    def save_album_data(self):
        os.makedirs("data", exist_ok=True)
        with open("data/album_data.json", "w", encoding="utf-8") as f:
            json.dump(self.album_data, f, ensure_ascii=False, indent=4)
    
    def load_album_data(self):
        try:
            with open("data/album_data.json", "r", encoding="utf-8") as f:
                self.album_data = json.load(f)
                
            # 앨범 트리뷰에 앨범 추가
            for album_name in self.album_data:
                self.add_album_to_tree(album_name)
                
            # 현재 앨범 설정
            self.current_album = "기본 앨범"
            self.photo_list = self.album_data["기본 앨범"]["photos"]
        except FileNotFoundError:
            # 기본 앨범 데이터 생성
            self.album_data = {
                "기본 앨범": {
                    "photos": [],
                    "descriptions": {}
                }
            }
            self.save_album_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoAlbum(root)
    root.mainloop() 