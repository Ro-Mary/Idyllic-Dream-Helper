import customtkinter as ctk
from PIL import Image
import sys, os
from strategies import STRATEGIES, Strategy

ctk.set_appearance_mode("light")
#ctk.set_default_color_theme("blue")

def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

class WindowB(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("출력")
        self.geometry("400x400")
        self.configure(fg_color="#5692b8")

        icon_path = resource_path("icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

        # X 버튼 막기 (닫히지 않게)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.overrideredirect(True)

        # 드래그 이동 구현
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        self._click_blocked = False

        self._move_locked = False
        self._drag_enabled = True
        self._click_through_enabled = False
        self.bind("<Map>", self._reapply_window_styles, add="+")

        # 크기 고정
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self._blank_img = ctk.CTkImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)), size=(1, 1))      

        self.reapply = None

        self.check_strat_frame = ctk.CTkFrame(
            self,
            fg_color="#f0fbff",
            width=390,
            height=37
        )
        self.check_strat_frame.place(x=5, y=5)

        self.check_strat_txt = ctk.CTkLabel(
            self.check_strat_frame,
            text="현재 처리법: 09stop",
            text_color="#000000",
            font=ctk.CTkFont(size=20)
        )
        self.check_strat_txt.place(x=10, y=5)        

        self.container = ctk.CTkFrame(
            self,
            fg_color="#f0fbff",
            width=390,
            height=350
            )
        self.container.place(x=5, y=45)

        # -----------로그-----------
        self.log_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=170,
            height=135
        )
        self.log_frame.place(x=215, y=5)

        ctk.CTkLabel(
            self.log_frame,
            text="클릭 로그",
            font=ctk.CTkFont(size=15)
        ).place(x=7, y=3)

        self.log_box= ctk.CTkTextbox(
            self.log_frame,
            fg_color="#f0fbff",
            width=160,
            height=95
        )
        self.log_box.place(x=5, y=35)
        self.log_box.configure(state="disabled")

        # -----------십자 X자 안전지대-----------  
        self.xplus_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=100,
            height=135
        )
        self.xplus_frame.place(x=5, y=5)
        self.xplus_label = ctk.CTkLabel(self.xplus_frame, text="")
        self.xplus_label.place(x=12, y=25)
        self.xplus_ref = None

        ctk.CTkLabel(
            self.xplus_frame,
            text="첫 기믹 체크",
            font=ctk.CTkFont(size=15)
        ).place(x=7, y=3)

        self.xplus_strat_label = ctk.CTkLabel(
            self.xplus_frame,
            text="",
            font=ctk.CTkFont(size=15),
        )
        self.xplus_strat_label.place(relx=0.49, rely=0.95, anchor="s")

        # -----------심상세계 위아래 안전지대-----------
        self.simsang_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=100,
            height=100
        )
        self.simsang_frame.place(x=110, y=5)
        self.simsang_label = ctk.CTkLabel(self.simsang_frame, text="")
        self.simsang_label.place(x=12, y=25)
        self.simsang_ref = None

        ctk.CTkLabel(
            self.simsang_frame,
            text="첫 안전지대",
            font=ctk.CTkFont(size=15)
        ).place(x=7, y=3)       

        # -----------교대 여부-----------
        self.swap_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=100,
            height=30
        )
        self.swap_frame.place(x=110, y=110)
        
        self.swap_label = ctk.CTkLabel(
            self.swap_frame,
            text="교대 없음(X)",
            font=ctk.CTkFont(size=15)
        )
        self.swap_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # -----------분신 섬, 안전지대 확인-----------
        self.safe_isl_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=160,
            height=93
        )
        self.safe_isl_frame.place(x=5, y=254)
        self.safe_isl_label = ctk.CTkLabel(self.safe_isl_frame, text="")
        self.safe_isl_label.place(x=10, y=30)
        self.safe_isl_ref = None

        self.safe_spot_label = ctk.CTkLabel(self.safe_isl_frame, text="")
        self.safe_spot_label.place(x=80, y=28)
        self.safe_spot_ref = None

        ctk.CTkLabel(
            self.safe_isl_frame,
            text="이동할 섬 및 안전지대",
            font=ctk.CTkFont(size=15)
        ).place(x=5, y=3)
        
        # -----------머리 위 표식에 따른 이동동선-----------
        self.check_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=65,
            height=105
        )
        self.check_frame.place(x=5, y=145)
        self.check_label = ctk.CTkLabel(self.check_frame, text="")
        self.check_label.place(x=5, y=40)
        self.check_img_ref = None
        
        ctk.CTkLabel(
            self.check_frame,
            text="표식",
            font=ctk.CTkFont(size=15)
        ).place(relx=0.5, rely=0.03, anchor="n")

        self.spread_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=240,
            height=105
        )
        self.spread_frame.place(x=145, y=145)

        self.marker_frame = ctk.CTkFrame(
            self.spread_frame,
            fg_color="#cfeaf8",
            width=220,
            height=90
        )
        self.marker_frame.place(x=4, y=32)

        self.marker_labels = []
        self.marker_text_labels = []
        self.marker_refs = [None, None, None, None]
        for i in range(4):
            cell = ctk.CTkFrame(self.marker_frame, fg_color="transparent")
            cell.pack(side="left", padx=3.5, pady=0)

            img_lbl = ctk.CTkLabel(cell, text="")
            img_lbl.pack(pady=(0, 0))

            txt_lbl = ctk.CTkLabel(cell, text="", font=ctk.CTkFont(size=13))
            txt_lbl.pack(pady=(0, 0))

            self.marker_labels.append(img_lbl)
            self.marker_text_labels.append(txt_lbl)

        ctk.CTkLabel(
            self.spread_frame,
            text="산개,쉐어 동선",
            font=ctk.CTkFont(size=15)
        ).place(x=5, y=3)
        
        self.where_center = ctk.CTkLabel(
            self.spread_frame,
            text="/ center: 1, 2징 사이",
            font=ctk.CTkFont(size=14)
        )
        self.where_center.place(x=106, y=3)

        # -----------선 채가기-----------
        self.line_frame = ctk.CTkFrame(
            self.container,
            fg_color="#cfeaf8",
            width=65,
            height=105
        )
        self.line_frame.place(x=75, y=145)

        self.line_img_label = ctk.CTkLabel(self.line_frame, text="")
        self.line_img_label.place(x=8, y=28)

        self.line_text_label = ctk.CTkLabel(
            self.line_frame,
            text="",
            font=ctk.CTkFont(size=15)
        )
        self.line_text_label.place(relx=0.5, rely=0.85, anchor="center")
        self.line_img_ref = None

        ctk.CTkLabel(
            self.line_frame,
            text="선 방향",
            font=ctk.CTkFont(size=15)
        ).place(relx=0.5, rely=0.03, anchor="n")

        # -----------타워 요약-----------           
        self.tower_check_frame = ctk.CTkFrame(
            self.container,
            width=215,
            height=92,
            fg_color="#cfeaf8"
        )
        self.tower_check_frame.place(x=170, y=254)

        self.tower_aero_label =  ctk.CTkLabel(
            self.tower_check_frame,
            text="에어로가(공중): 보스정면에 딱 붙기",
            font=ctk.CTkFont(size=13),
            text_color="#1E972F"
        )
        self.tower_aero_label.place(x=5, y=3)

        self.tower_doom_label = ctk.CTkLabel(
            self.tower_check_frame,
            text="죽선(빔): 숫자징 뒤쪽 변에 서기",
            font=ctk.CTkFont(size=13),
            text_color="#631988"
        )
        self.tower_doom_label.place(x=5, y=23)

        self.tower_nodebuff_range_label =  ctk.CTkLabel(
            self.tower_check_frame,
            text="디버프X 원딜: 섬 남쪽(6시) 끝",
            font=ctk.CTkFont(size=13)
        )
        self.tower_nodebuff_range_label.place(x=5, y=43)

        self.tower_nodebuff_melee_label =  ctk.CTkLabel(
            self.tower_check_frame,
            text="디버프X 근딜: 죽선 대상자 뒤쪽 붙기",
            font=ctk.CTkFont(size=13)
        )
        self.tower_nodebuff_melee_label.place(x=5, y=63)

        self.tower_labels = [
            self.tower_aero_label, 
            self.tower_doom_label, 
            self.tower_nodebuff_range_label, 
            self.tower_nodebuff_melee_label
        ]       
        self.after(200, self._ensure_layered)
        self.after(10, lambda: self.attributes("-topmost", True))

    def set_center_strat_text(self, text: str):
        self.where_center.configure(text=text)

    def set_xplus_strat_text(self, text: str):
        self.xplus_strat_label.configure(text=text)

    def set_check_strat_text(self, text: str):
        self.check_strat_txt.configure(text=text)

    def set_tower_check_texts(self, texts: list[str]):
            padded = (texts + ["", "", "", ""])[:4]
            for i, t in enumerate(padded):
                self.tower_labels[i].configure(text=t)

    def set_safe_isl_image(self, img: ctk.CTkImage | None):
        self.safe_isl_ref = img
        display_img = img if img is not None else self._blank_img
        self.safe_isl_label.configure(image=display_img, text="")

    def set_safe_spot_image(self, img: ctk.CTkImage | None):
        self.safe_spot_ref = img
        display_img = img if img is not None else self._blank_img
        self.safe_spot_label.configure(image=display_img, text="")

    def set_simsang_image(self, img: ctk.CTkImage | None):
        self.simsang_ref = img
        display_img = img if img is not None else self._blank_img
        self.simsang_label.configure(image=display_img, text="")

    def set_xplus_image(self, img: ctk.CTkImage | None):
        self.xplus_ref = img
        display_img = img if img is not None else self._blank_img
        self.xplus_label.configure(image=display_img, text="")

    def set_check_image(self, img: ctk.CTkImage | None):
        self.check_img_ref = img
        display_img = img if img is not None else self._blank_img
        self.check_label.configure(image=display_img, text="")
        self.update_idletasks()

    def set_4_icons(self, icons: list[ctk.CTkImage | None], texts: list[str]):
        padded_icons = (icons + [None, None, None, None])[:4]
        padded_texts = (texts + ["", "", "", ""])[:4]

        for i in range(4):
            img = padded_icons[i]
            text = padded_texts[i]

            self.marker_refs[i] = img
            display_img = img if img is not None else self._blank_img
            self.marker_labels[i].configure(image=display_img, text="")
            self.marker_text_labels[i].configure(text=text)

        self.update_idletasks()

    def set_shift_status(self, enabled: bool):
        self.swap_label.configure(text="교대(O)" if enabled else "교대 없음(X)")

    def _reapply_window_styles(self, event=None):
        if not self._click_through_enabled:
            return
        if self.reapply is not None:
            try:
                self.after_cancel(self.reapply)
            except Exception:
                pass
        self.reapply = self.after(80, lambda: self._apply_click_through_style(True))
        
    def _ensure_layered(self):
        if sys.platform != "win32":
            return
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32

        self.update_idletasks()
        hwnd = self._get_hwnd()
        if not hwnd:
            self.after(100, self._ensure_layered)
            return

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000

        if ctypes.sizeof(ctypes.c_void_p) == 8:
            GetWindowLong = user32.GetWindowLongPtrW
            SetWindowLong = user32.SetWindowLongPtrW
            GetWindowLong.restype = ctypes.c_longlong
            SetWindowLong.restype = ctypes.c_longlong
        else:
            GetWindowLong = user32.GetWindowLongW
            SetWindowLong = user32.SetWindowLongW
            GetWindowLong.restype = ctypes.c_long
            SetWindowLong.restype = ctypes.c_long

        GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
        SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, GetWindowLong.restype]

        exstyle = GetWindowLong(hwnd, GWL_EXSTYLE)
        if not (exstyle & WS_EX_LAYERED):
            exstyle |= WS_EX_LAYERED
            SetWindowLong(hwnd, GWL_EXSTYLE, exstyle)

    def _get_hwnd(self) -> int:
        """항상 '최상위(루트) HWND'를 반환해서 적용/해제 대상이 바뀌지 않게 한다."""
        if sys.platform != "win32":
            return 0
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = self.winfo_id()
        if not hwnd:
            return 0

        # GA_ROOT = 2 : 최상위 루트 윈도우 핸들로 통일
        GA_ROOT = 2
        root = user32.GetAncestor(hwnd, GA_ROOT)
        return root if root else hwnd

    def set_click_through(self, enabled: bool):
        if enabled == self._click_through_enabled:
            return
        self._click_through_enabled = enabled
        self._apply_click_through_style(enabled)

    def _apply_click_through_style(self, enabled: bool):
        import sys
        if sys.platform != "win32":
            # mac/linux: 완전 click-through는 보장 불가. (원하면 disable 정도만)
            try:
                self.attributes("-disabled", enabled)
            except Exception:
                pass
            return

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32

        hwnd = self._get_hwnd()
        if not hwnd:
            # 핸들이 아직 준비 안됐으면 다음 틱에 재시도
            self.after(50, lambda: self._apply_click_through_style(enabled))
            return

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020

        # 64bit/32bit 호환
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            GetWindowLong = user32.GetWindowLongPtrW
            SetWindowLong = user32.SetWindowLongPtrW
            GetWindowLong.restype = ctypes.c_longlong
            SetWindowLong.restype = ctypes.c_longlong
        else:
            GetWindowLong = user32.GetWindowLongW
            SetWindowLong = user32.SetWindowLongW
            GetWindowLong.restype = ctypes.c_long
            SetWindowLong.restype = ctypes.c_long

        GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
        SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, GetWindowLong.restype]

        exstyle = GetWindowLong(hwnd, GWL_EXSTYLE)

        if enabled:
            # click-through를 쓰려면 layered가 같이 필요함
            exstyle |= (WS_EX_LAYERED | WS_EX_TRANSPARENT)
        else:
            # ✅ 핵심: layered는 굳이 빼지 말고, transparent만 확실히 제거
            exstyle &= ~WS_EX_TRANSPARENT

        SetWindowLong(hwnd, GWL_EXSTYLE, exstyle)

        # 스타일 즉시 반영
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

    def set_line_mark(self, img: ctk.CTkImage | None, text: str):
        self.line_img_ref = img
        display_img = img if img is not None else self._blank_img
        self.line_img_label.configure(image=display_img, text="")
        self.line_text_label.configure(text=text)
        self.update_idletasks()       
    
    def set_move_locked(self, locked: bool):
        self._move_locked = locked

    # topmost 재적용 + 앞으로 올리기
    def ensure_on_top(self):
        self.attributes("-topmost", True)
        self.lift()
        self.after(10, lambda: self.attributes("-topmost", True))
    
    def start_move(self, event):
        if getattr(self, "_move_locked", False):
            return
        self._drag_x = event.x_root
        self._drag_y = event.y_root
        self._win_x = self.winfo_x()
        self._win_y = self.winfo_y()

    def do_move(self, event):
        if getattr(self, "_move_locked", False):
            return
        dx = event.x_root - self._drag_x
        dy = event.y_root - self._drag_y
        self.geometry(f"+{self._win_x + dx}+{self._win_y + dy}")

    def append_line(self, text: str):
        tb = self.log_box
        tb.configure(state="normal")

        current = tb.get("1.0", "end-1c")
        if current.strip() == "":
            tb.insert("end", text)
        else:
            tb.insert("end", "\n" + text)

        tb.see("end")
        tb.configure(state="disabled")

    def clear(self):
        tb = self.log_box
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.configure(state="disabled")

# Window A
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Idyllic Dream Helper")
        self.geometry("350x745")
        self.resizable(False, False)
        self.configure(fg_color="#f0fbff")
        self._btn_enabled: dict[int, bool] = {}
        self._btn_normal_color: dict[int, any] = {}     
        icon_path = resource_path("icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

        self.bind("<Map>", self._on_app_restore)
        self.bind("<FocusIn>", self._on_app_restore)
        self.button_icons = {
            "plus": ctk.CTkImage(Image.open(resource_path("img/plusmark.png")), size=(50, 50)),
            "xmark": ctk.CTkImage(Image.open(resource_path("img/xmark.png")), size=(50, 50)),
            "1mark": ctk.CTkImage(Image.open(resource_path("img/1mark.png")), size=(50, 50)),
            "2mark": ctk.CTkImage(Image.open(resource_path("img/2mark.png")), size=(50, 50)),
            "3mark": ctk.CTkImage(Image.open(resource_path("img/3mark.png")), size=(50, 50)),
            "4mark": ctk.CTkImage(Image.open(resource_path("img/4mark.png")), size=(50, 50)),
            "Amark": ctk.CTkImage(Image.open(resource_path("img/Amark.png")), size=(50, 50)),
            "Bmark": ctk.CTkImage(Image.open(resource_path("img/Bmark.png")), size=(50, 50)),
            "Cmark": ctk.CTkImage(Image.open(resource_path("img/Cmark.png")), size=(50, 50)),
            "Dmark": ctk.CTkImage(Image.open(resource_path("img/Dmark.png")), size=(50, 50)),
            "stack": ctk.CTkImage(Image.open(resource_path("img/stack.png")), size=(50, 50)),
            "spread": ctk.CTkImage(Image.open(resource_path("img/spread.png")), size=(50, 50)),
            "center": ctk.CTkImage(Image.open(resource_path("img/centermark.png")), size=(50, 50)),
            "first": ctk.CTkImage(Image.open(resource_path("img/first.png")), size=(50, 50)),
            "second": ctk.CTkImage(Image.open(resource_path("img/second.png")), size=(50, 50)),
            "third": ctk.CTkImage(Image.open(resource_path("img/third.png")), size=(50, 50)),
            "fourth": ctk.CTkImage(Image.open(resource_path("img/fourth.png")), size=(50, 50)),
            "stop1": ctk.CTkImage(Image.open(resource_path("img/stop1.png")), size=(50, 50)),
            "stop2": ctk.CTkImage(Image.open(resource_path("img/stop2.png")), size=(50, 50)),
            "bind1": ctk.CTkImage(Image.open(resource_path("img/bind1.png")), size=(50, 50)),
            "bind2": ctk.CTkImage(Image.open(resource_path("img/bind2.png")), size=(50, 50)),
        }

        self.display_map = {
            1: ctk.CTkImage(Image.open(resource_path("img/plusmark.png")), size=(70, 70)),
            2: ctk.CTkImage(Image.open(resource_path("img/xmark.png")), size=(70, 70)),
            3: ctk.CTkImage(Image.open(resource_path("img/Amark.png")), size=(70, 70)),
            4: ctk.CTkImage(Image.open(resource_path("img/Cmark.png")), size=(70, 70)),
            5: ctk.CTkImage(Image.open(resource_path("img/Bmark.png")), size=(70, 70)),
            6: ctk.CTkImage(Image.open(resource_path("img/Dmark.png")), size=(70, 70)),
        }

        self.marker_move_icons_map = {
            "center": self.button_icons["center"],
            "1": self.button_icons["1mark"],
            "2": self.button_icons["2mark"],
            "3": self.button_icons["3mark"],
            "4": self.button_icons["4mark"],
            "C": self.button_icons["Cmark"],
            "D": self.button_icons["Dmark"]
        }
        
        self.safe_spot_img_map = {
            "rl": ctk.CTkImage(Image.open(resource_path("img/rlsafe.png")), size=(60, 60)),
            "ud": ctk.CTkImage(Image.open(resource_path("img/udsafe.png")), size=(60, 60)),
        }

        self.strategy: Strategy = STRATEGIES["09stop"]

        # B창 생성
        self.win_b = WindowB(self)
        self.win_b.transient(self)  # A에 종속

        # A 닫으면 B도 같이 닫기
        self.protocol("WM_DELETE_WINDOW", self.on_close_a)

        # 버튼 저장
        self.buttons: dict[int, ctk.CTkButton] = {}

        # "마지막으로 눌린 버튼" 상태 관리 (그룹별)
        self.last_icon = None       # 1~2
        self.last_btn_3_10 = None   # 3~10
        self.last_updown = None     # 11~12
        self.last_spreadstack = None# 13~14
        self.last_clone = None      # 16~17
        self.last_move = None       # 18~19
        self.last_main = None

        # 교대
        self.toggle_15_on = False

        self.isSpread = 0

        click_control_frame = ctk.CTkFrame(
            self,
            width=160,
            height=80,
            fg_color="#cfeaf8"
        )
        click_control_frame.place(x=180, y=467)

        self.lock_move = ctk.BooleanVar(value=False)
        self.ignore_click = ctk.BooleanVar(value=False)
        self.cb_lock_move = ctk.CTkCheckBox(
            click_control_frame,
            text="위치 잠금",
            variable=self.lock_move,
            command=self.apply_b_controls,
            checkbox_width=20,
            checkbox_height=20,
            border_color="#759bb3",
            hover=False,
            border_width=3
        )
        self.cb_lock_move.place(x=10, y=10)

        cb_ignore_click = ctk.CTkCheckBox(
            click_control_frame,
            text="클릭 무시",
            variable=self.ignore_click,
            command=self.apply_b_controls,
            checkbox_width=20,
            checkbox_height=20,
            border_color="#759bb3",
            hover=False,
            border_width=3
        )
        cb_ignore_click.place(x=10, y=45)

        self._build_ui()
        self.win_b.update_idletasks()
        self.win_b.deiconify()
        self.win_b.lift()

    def apply_b_controls(self):
        if self.ignore_click.get():
            self.lock_move.set(True)  # 클릭 무시 중엔 이동도 잠그기
        self.win_b.set_move_locked(self.lock_move.get())
        self.win_b.set_click_through(self.ignore_click.get())

    def on_strats_changed(self, value: str):
        self.reset_all()
        self.strategy = STRATEGIES[value]
        self.apply_3to10_button_icons_by_strats()
        self.apply_strategy_to_ui()
        
    def apply_3to10_visual(self, n: int):
        mark_key = self.strategy.btn_to_mark.get(n)
        mark_img = self.button_icons.get(mark_key) if mark_key else None

        mode_text = "쉐어" if self.strategy.is_share(n) else "산개"
        self.win_b.set_line_mark(mark_img, mode_text)

        check_img_key = self.strategy.check_img_key_map.get(n)
        img = self.button_icons.get(check_img_key) if check_img_key else None
        self.win_b.set_check_image(img)

    def apply_strategy_to_ui(self):
        self.win_b.set_tower_check_texts(self.strategy.tower_texts)
        self.win_b.set_check_strat_text(self.strategy.check_strat_text)
        self.win_b.set_center_strat_text(self.strategy.where_center)

        # 이미 선택된 게 있으면 화면 재반영
        if self.last_btn_3_10 is not None:
            self.apply_3to10_visual(self.last_btn_3_10)

        if self.last_btn_3_10 is not None and self.isSpread in (1, 2):
            result = self.get_spread_result(self.last_btn_3_10, self.isSpread)
            if result:
                self.apply_spread_visual(result)

        self.update_xplus_strat_label()

    def compute_xplus_strat_text(self) -> str:
        s = self.strategy.key
        p = self.last_main
        icon = self.last_icon

        if icon not in (1, 2) or p not in (21, 22):
            return ""

        table = {
            ("09stop", 21, 1): "12시 → 1시",
            ("09stop", 21, 2): "1시 → 12시",
            ("09stop", 22, 1): "3시 → 5시",
            ("09stop", 22, 2): "5시 → 3시",

            ("game8", 21, 1): "A징 → 1징",
            ("game8", 21, 2): "1징 → A징",
            ("game8", 22, 1): "D징 → 4징",
            ("game8", 22, 2): "4징 → D징",
        }
        return table.get((s, p, icon), "")

    def update_xplus_strat_label(self):
        text = self.compute_xplus_strat_text()
        self.win_b.set_xplus_strat_text(text)

    def _build_ui(self):
        # 타이틀
        title_frame = ctk.CTkFrame(
            self,
            width=330,
            height=80,
            fg_color="#cfeaf8"
        )
        title_frame.place(x=10, y=10)

        ctk.CTkLabel(
            title_frame, 
            text="아르카디아의 꿈 헬퍼", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).place(x=10, y=5)    

        ctk.CTkLabel(
            title_frame, 
            text="Idyllic Dream Helper", 
            font=ctk.CTkFont(size=15)
        ).place(x=10, y=27)     

        ctk.CTkLabel(
            title_frame, 
            text="외워야 할 기믹들을 버튼을 눌러 기록할 수 있습니다.", 
            font=ctk.CTkFont(size=13)
        ).place(x=10, y=50)

        ctk.CTkLabel(
            self, 
            text="Ro Mary@Chocobo", 
            font=ctk.CTkFont(size=13),
            text_color="#6eb6e1"
        ).place(x=220, y=707)      

        # ---------------------- 처리법 선택 ------------------------

        strats_frame = ctk.CTkFrame(
            self,
            width=160,
            height=70,
            fg_color="#cfeaf8"
        )
        strats_frame.place(x=180, y=100)

        strats_box = ctk.CTkComboBox(
            strats_frame,
            values=["09stop", "game8"],
            command=self.on_strats_changed,
            button_color="#a7d4ee",
            border_color="#a7d4ee",
            button_hover_color="#6eb6e1",
            state="readonly",
        )
        strats_box.set("09stop")
        strats_box.place(x=5, y=35)

        ctk.CTkLabel(
            strats_frame,
            text="처리법 선택",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)

        # -----------메인 or 서브 조-----------
        
        main_button = ctk.CTkButton(
            self,
            text="메인조",
            text_color="#000000",
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=2,
            border_color="#759bb3",
            text_color_disabled="#000000",
            width=77, 
            height=30,
            command=lambda: self.handle_button(21)
        )
        main_button.place(x=180, y=175)
        self.buttons[21] = main_button

        sub_button = ctk.CTkButton(
            self,
            text="서브조",
            text_color="#000000",
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=2,
            border_color="#759bb3",
            text_color_disabled="#000000",
            width=77, 
            height=30,
            command=lambda: self.handle_button(22)
        )
        sub_button.place(x=263, y=175)
        self.buttons[22] = sub_button

        # ---------------------- 십자, X자 체크 ------------------------
        first_frame = ctk.CTkFrame(
            self,
            width=160,
            height=105,
            fg_color="#cfeaf8"
        )
        first_frame.place(x=10, y=100)

        ctk.CTkLabel(
            first_frame,
            text="십자, X자 체크",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)

        plus_button = ctk.CTkButton(
            first_frame,
            image=self.button_icons["plus"],
            text="",
            command=lambda: self.handle_button(1),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        plus_button.place(x=10, y=35)
        self.buttons[1] = plus_button

        x_button = ctk.CTkButton(
            first_frame,
            image=self.button_icons["xmark"],
            text="",
            command=lambda: self.handle_button(2),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        x_button.place(x=80, y=35)
        self.buttons[2] = x_button

        # ---------------------- 분신 확인 ------------------------
        macro_frame = ctk.CTkFrame(
            self,
            width=227,
            height=240,
            fg_color="#cfeaf8"
        )
        macro_frame.place(x=10, y=215)
        
        ctk.CTkLabel(
            macro_frame,
            text="분신 확인하기",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)        

        _Amark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["Amark"],
            text="",
            command=lambda: self.handle_button(3),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _Amark.place(x=80, y=35)
        self.buttons[3] = _Amark

        _1mark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["1mark"],
            text="",
            command=lambda: self.handle_button(4),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _1mark.place(x=150, y=35)
        self.buttons[4] = _1mark

        _Bmark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["Bmark"],
            text="",
            command=lambda: self.handle_button(5),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _Bmark.place(x=150, y=100)
        self.buttons[5] = _Bmark

        _2mark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["2mark"],
            text="",
            command=lambda: self.handle_button(6),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _2mark.place(x=150, y=165)
        self.buttons[6] = _2mark

        _Cmark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["Cmark"],
            text="",
            command=lambda: self.handle_button(7),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _Cmark.place(x=80, y=165)
        self.buttons[7] = _Cmark

        _3mark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["3mark"],
            text="",
            command=lambda: self.handle_button(8),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _3mark.place(x=10, y=165)
        self.buttons[8] = _3mark

        _Dmark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["Dmark"],
            text="",
            command=lambda: self.handle_button(9),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _Dmark.place(x=10, y=100)
        self.buttons[9] = _Dmark

        _4mark = ctk.CTkButton(
            macro_frame,
            image=self.button_icons["4mark"],
            text="",
            command=lambda: self.handle_button(10),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        _4mark.place(x=10, y=35)
        self.buttons[10] = _4mark

        # 심상 안전지대
        updown_frame = ctk.CTkFrame(
            self,
            width=95,
            height=190,
            fg_color="#cfeaf8"
        )
        updown_frame.place(x=245, y=215)

        ctk.CTkLabel(
            updown_frame,
            text="AC확인",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5) 

        upSafe = ctk.CTkButton(
            updown_frame,
            image=self.button_icons["Amark"],
            text="",
            command=lambda: self.handle_button(11),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=70, 
            height=70
        )
        upSafe.place(x=12, y=35)
        self.buttons[11] = upSafe

        downSafe = ctk.CTkButton(
            updown_frame,
            image=self.button_icons["Cmark"],
            text="",
            command=lambda: self.handle_button(12),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=70, 
            height=70
        )
        downSafe.place(x=12, y=110)
        self.buttons[12] = downSafe

        # 산개쉐어 확인
        isSpread_frame = ctk.CTkFrame(
            self,
            width=160,
            height=105,
            fg_color="#cfeaf8"
        )
        isSpread_frame.place(x=10, y=466)

        ctk.CTkLabel(
            isSpread_frame,
            text="12시 징 확인",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)     

        spread_button = ctk.CTkButton(
            isSpread_frame,
            image=self.button_icons["spread"],
            text="",
            command=lambda: self.handle_button(13),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        spread_button.place(x=10, y=35)
        self.buttons[13] = spread_button

        stack_button = ctk.CTkButton(
            isSpread_frame,
            image=self.button_icons["stack"],
            text="",
            command=lambda: self.handle_button(14),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        stack_button.place(x=80, y=35)
        self.buttons[14] = stack_button

        swap_button = ctk.CTkButton(
            self,
            text="교대?",
            text_color="black",
            font=ctk.CTkFont(size=18),
            command=lambda: self.handle_button(15),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=95, 
            height=45
        )
        swap_button.place(x=245, y=410)
        self.buttons[15] = swap_button

        line_frame = ctk.CTkFrame(
            self,
            width=330,
            height=4,
            fg_color="#7EA0B6"
        )
        line_frame.place(x=10, y=580)

        leftone_frame = ctk.CTkFrame(
            self,
            width=160,
            height=105,
            fg_color="#cfeaf8"
        )
        leftone_frame.place(x=10, y=595)

        ctk.CTkLabel(
            leftone_frame,
            text="필드에 남은 분신",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)     

        ALeft = ctk.CTkButton(
            leftone_frame,
            image=self.button_icons["Amark"],
            text="",
            command=lambda: self.handle_button(16),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        ALeft.place(x=10, y=35)
        self.buttons[16] = ALeft

        CLeft = ctk.CTkButton(
            leftone_frame,
            image=self.button_icons["Cmark"],
            text="",
            command=lambda: self.handle_button(17),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        CLeft.place(x=80, y=35)
        self.buttons[17] = CLeft


        where_frame = ctk.CTkFrame(
            self,
            width=160,
            height=105,
            fg_color="#cfeaf8"
        )
        where_frame.place(x=180, y=595)

        ctk.CTkLabel(
            where_frame,
            text="이동한 섬 확인",
            font=ctk.CTkFont(size=15)
        ).place(x=8, y=5)

        Bsafe = ctk.CTkButton(
            where_frame,
            image=self.button_icons["Bmark"],
            text="",
            command=lambda: self.handle_button(18),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        Bsafe.place(x=80, y=35)
        self.buttons[18] = Bsafe

        Dsafe = ctk.CTkButton(
            where_frame,
            image=self.button_icons["Dmark"],
            text="",
            command=lambda: self.handle_button(19),
            fg_color="#a7d4ee",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=50, 
            height=50
        )
        Dsafe.place(x=10, y=35)
        self.buttons[19] = Dsafe
       
        reset_button = ctk.CTkButton(
            self,
            text="초기화",
            text_color="#000000",
            command=lambda: self.handle_button(20),
            fg_color="#cfeaf8",
            hover_color="#6eb6e1",
            border_width=3,
            border_color="#759bb3",
            width=120, 
            height=30
        )
        reset_button.place(x=10, y=705)
        self.buttons[20] = reset_button

        self.disable_btn(21)
        self.enable_btn(22)
        self.last_main = 21
        self.apply_strategy_to_ui()

    
    def on_close_a(self):
        try:
            if self.win_b.winfo_exists():
                self.win_b.destroy()
        except Exception:
            pass
        self.destroy()

    # ----------------------------
    # 공통 유틸
    # ----------------------------
    def disable_btn(self, n: int):
        btn = self.buttons.get(n)
        if btn:
            btn.configure(state="disabled", fg_color="#4ea4da", hover_color="#2d93d2", border_color="#435864")

    def enable_btn(self, n: int):
        btn = self.buttons.get(n)
        if not btn:
            return
        if n == 20:  # 초기화 버튼 원래 스타일
            btn.configure(state="normal", fg_color="#cfeaf8", hover_color="#6eb6e1", border_color="#759bb3")
        else:
            btn.configure(state="normal", fg_color="#a7d4ee", hover_color="#6eb6e1", border_color="#759bb3")

    def _on_app_restore(self, event=None):
        # B창이 존재하면 topmost 재적용
        if hasattr(self, "win_b") and self.win_b.winfo_exists():
            self.win_b.after(0, self.win_b.ensure_on_top)
            self.win_b.after(50, self.apply_b_controls)
            
    def append_fix(self):
        self.win_b.append_line("----------(수정)----------")

    def apply_3to10_button_icons_by_strats(self):
        mapping = self.strategy.btn_icon_map

        for btn_num in range(3, 11):
            btn = self.buttons.get(btn_num)
            if not btn:
                continue

            icon_key = mapping.get(btn_num)
            if icon_key:
                btn.configure(
                    image=self.button_icons[icon_key],
                    text=""
                )

    #(A,B) 같은 2개 중 하나만 비활성화되는 "상호배타" 로직 공통 처리.
    def handle_exclusive_pair(self, new_n: int, last_attr: str, other_n: int, fix_on_switch: bool = True):
        last = getattr(self, last_attr)

        if last == other_n:
            if fix_on_switch:
                self.win_b.append_line("----------(수정)----------")
            self.enable_btn(other_n)

        self.disable_btn(new_n)
        setattr(self, last_attr, new_n)

    def reset_all(self):
        for n in self.buttons.keys():
            if n in (21, 22):
                continue
            self.enable_btn(n)
        self.win_b.clear()
        self.win_b.set_4_icons([None, None, None, None], ["", "", "", ""])
        self.win_b.set_check_image(None)
        self.win_b.set_xplus_image(None)
        self.win_b.set_safe_isl_image(None)
        self.win_b.set_simsang_image(None)
        self.win_b.set_shift_status(False)
        self.win_b.set_safe_spot_image(None)
        self.win_b.set_line_mark(None, "")       
        self.last_icon = None
        self.last_btn_3_10 = None
        self.last_updown = None
        self.last_spreadstack = None
        self.last_clone = None
        self.last_move = None
        self.isSpread = 0
        self.toggle_15_on = False
        self.update_xplus_strat_label()

    def set_is_spread(self, value: int):
        self.isSpread = value
        if self.isSpread in (1, 2):
            result = self.get_spread_result(self.last_btn_3_10, self.isSpread)
            if result is not None:
                self.win_b.append_line(result)
                self.apply_spread_visual(result)
            else:
                self.win_b.append_line("(!)표식 선택 필요.")
    
    def get_3to10_label(self, n: int) -> str:
        return self.strategy.text_3_10.get(n, f"버튼 {n}")

    def get_spread_result(self, last_btn_3_10: int | None, is_spread: int) -> str | None:
        if last_btn_3_10 is None:
            return None
        table = self.strategy.spread_map_1 if is_spread == 1 else self.strategy.spread_map_2
        return table.get(last_btn_3_10)
    
    def apply_spread_visual(self, result_text: str):
        tokens = [t.strip() for t in result_text.split("-")]
        tokens = (tokens + [None, None, None, None])[:4]

        icons = []
        captions = []

        strat_key = self.strategy.key  # "09stop" or "game8"

        for t in tokens:
            if t is None:
                icons.append(None)
                captions.append("")
                continue

            token = t

            # 아이콘
            icons.append(self.marker_move_icons_map.get(token))

            # 캡션
            if token == "center":
                captions.append("")
            elif strat_key == "09stop":
                # 1,2 => 쉐어 / C,D => 산개
                if token in ("1", "2"):
                    captions.append("쉐어")
                elif token in ("C", "D"):
                    captions.append("산개")
                else:
                    captions.append("")  # 혹시 모르는 토큰 대비
            else:  # game8
                # 3,4 => 쉐어 / 1,2 => 산개
                if token in ("3", "4"):
                    captions.append("쉐어")
                elif token in ("1", "2"):
                    captions.append("산개")
                else:
                    captions.append("")

        self.win_b.set_4_icons(icons, captions)

        # 버튼마다 다른 텍스트 출력
    def handle_3_to_10(self, n: int):
        self.win_b.append_line(self.get_3to10_label(n))

        if self.last_btn_3_10 is not None and self.last_btn_3_10 != n:
            self.win_b.append_line("----------(수정)----------")
            self.enable_btn(self.last_btn_3_10)

        self.disable_btn(n)
        self.last_btn_3_10 = n

        self.apply_3to10_visual(n)

        if self.isSpread in (1, 2):
            result = self.get_spread_result(self.last_btn_3_10, self.isSpread)
            if result:
                self.win_b.append_line(result)
                self.apply_spread_visual(result)

    def update_safe_spot_image_by_state(self):
        u = self.last_updown   # 11 or 12 or None
        c = self.last_clone    # 16 or 17 or None

        if u is None or c is None:
            self.win_b.set_safe_spot_image(None)
            return

        if (u == 11 and c == 16) or (u == 12 and c == 17):
            self.win_b.set_safe_spot_image(self.safe_spot_img_map["rl"])
        elif (u == 11 and c == 17) or (u == 12 and c == 16):
            self.win_b.set_safe_spot_image(self.safe_spot_img_map["ud"])
        else:
            self.win_b.set_safe_spot_image(None)

    # 버튼 핸들러
    def handle_button(self, n: int):
        if n == 1:
            self.handle_exclusive_pair(
                new_n=1,
                last_attr="last_icon",
                other_n=2
            )
            self.win_b.append_line("십자")
            self.win_b.set_xplus_image(self.display_map.get(1))
            self.update_xplus_strat_label()

        elif n == 2:
            self.handle_exclusive_pair(
                new_n=2,
                last_attr="last_icon",
                other_n=1
            )
            self.win_b.append_line("X자")
            self.win_b.set_xplus_image(self.display_map.get(2))
            self.update_xplus_strat_label()

        elif 3 <= n <= 10:
            self.handle_3_to_10(n)

        elif n == 11:            
            self.handle_exclusive_pair(
                new_n=11,
                last_attr="last_updown",
                other_n=12
            )
            self.win_b.append_line("위쪽 안전")
            self.win_b.set_simsang_image(self.display_map.get(3))
            self.update_safe_spot_image_by_state()

        elif n == 12:         
            self.handle_exclusive_pair(
                new_n=12,
                last_attr="last_updown",
                other_n=11
            )
            self.win_b.append_line("아래쪽 안전")
            self.win_b.set_simsang_image(self.display_map.get(4))
            self.update_safe_spot_image_by_state()

        elif n == 13:
            self.handle_exclusive_pair(
                new_n=13,
                last_attr="last_spreadstack",
                other_n=14
            )
            self.win_b.append_line("산개")
            self.set_is_spread(1)

        elif n == 14:
            self.handle_exclusive_pair(
                new_n=14,
                last_attr="last_spreadstack",
                other_n=13
            )
            self.win_b.append_line("쉐어")
            self.set_is_spread(2)

        elif n == 15:
            self.toggle_15_on = not self.toggle_15_on
            self.win_b.set_shift_status(self.toggle_15_on)
            self.win_b.append_line("교대" if self.toggle_15_on else "교대 해제")

        elif n == 16:
            self.handle_exclusive_pair(
                new_n=16,
                last_attr="last_clone",
                other_n=17,
            )
            self.win_b.append_line("A 남음")
            self.update_safe_spot_image_by_state()

        elif n == 17:
            self.handle_exclusive_pair(
                new_n=17,
                last_attr="last_clone",
                other_n=16,
            )
            self.win_b.append_line("C 남음")
            self.update_safe_spot_image_by_state()

        elif n == 18:
            self.handle_exclusive_pair(
                new_n=18,
                last_attr="last_move",
                other_n=19
            )
            self.win_b.append_line("오른쪽 이동")
            self.win_b.set_safe_isl_image(self.button_icons["Bmark"])

        elif n == 19:
            self.handle_exclusive_pair(
                new_n=19,
                last_attr="last_move",
                other_n=18
            )
            self.win_b.append_line("왼쪽 이동")
            self.win_b.set_safe_isl_image(self.button_icons["Dmark"])

        elif n == 20:
            self.reset_all()

        elif n == 21:
            self.handle_exclusive_pair(
                new_n=21,
                last_attr="last_main",
                other_n=22,
            )
            self.win_b.append_line("메인조 변경")
            self.update_xplus_strat_label()

        elif n == 22:
            self.handle_exclusive_pair(
                new_n=22,
                last_attr="last_main",
                other_n=21,
            )
            self.win_b.append_line("서브조 변경")
            self.update_xplus_strat_label()

        else:
            self.win_b.append_line(f"{n}번 버튼 눌림")

if __name__ == "__main__":
    app = App()
    app.mainloop()
