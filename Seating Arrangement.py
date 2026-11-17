import tkinter as tk
from tkinter import font, filedialog, messagebox, simpledialog, colorchooser
import random
import json
import os
import math
import webbrowser
from PIL import Image, ImageDraw, ImageFont

class SeatingChartApp:
    def __init__(self, root):
        self.root = root
        
        self.root.resizable(True, True)
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        init_w = min(1280, int(screen_w * 0.92))
        init_h = min(850, int(screen_h * 0.88))
        self.root.geometry(f"{init_w}x{init_h}")
        self.root.minsize(850, 580)
        self.root.configure(bg="#2C3E50")
        
        self.base_dir = "seating_data"
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.title_font = font.Font(family="Segoe UI", size=20, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=11)
        
        # =========================================================================
        # CONFIGURACIÓN BÁSICA DE CUADRÍCULA
        # =========================================================================
        self.rows = 10
        self.cols = 12
        self.cell_w = 85
        self.cell_h = 70
        self.grid_offset_y = 55 
        
        # Opciones visuales para Proyector
        self.card_color = "#FFFFFF"        
        self.card_text_color = "#000000"   
        self.font_mode = tk.StringVar(value="auto")  
        self.fixed_font_size = tk.IntVar(value=12)
        
        self.classroom_name = ""
        self.mode = tk.StringVar(value="edit") 
        self.desks = set() 
        self.assignments = {} 
        self.unassigned = [] 
        self.unassigned_bboxes = []
        
        self.selected_student = None 
        self.drag_data = None
        self.has_dragged = False
        
        # SISTEMA DE IDIOMAS (Inicia en Inglés por defecto)
        self.current_lang = tk.StringVar(value="en")
        self.translations = {
            "es": {
                "title_main": "ASIGNADOR DE ASIENTOS",
                "btn_create": "Crear Nueva Aula",
                "btn_load": "Cargar Aula Guardada",
                "btn_about": "Acerca del Autor / Donar",
                "msg_new_class": "Nueva Aula",
                "msg_enter_name": "Ingresa el nombre del Aula/Curso:",
                "title_load": "Cargar Aula",
                "msg_no_class": "No se encontraron aulas guardadas.",
                "btn_back": "⬅ Volver",
                "btn_back_menu": "⬅ Volver al Menú",
                "btn_rename": "✏️ Renombrar",
                "btn_delete": "🗑️ Borrar",
                "msg_rename": "Renombrar",
                "msg_enter_new_name": "Ingresa el nuevo nombre:",
                "msg_confirm": "Confirmar",
                "msg_confirm_del": "¿Seguro que quieres eliminar el aula '{}'?",
                "msg_save_success": "Aula '{}' guardada con éxito.",
                "msg_saved": "Guardado",
                "lbl_mode": "Modo:",
                "rb_draw": "1. Dibujar Bancos",
                "rb_move": "2. Mover Alumnos",
                "btn_save": "💾 Guardar",
                "btn_export": "📷 Exportar PNG",
                "lbl_course": "Curso: {}",
                "lbl_style": "📽️ Estilo Tarjetas (Proyector)",
                "lf_vis": "Visibilidad",
                "lbl_bg": "Fondo:",
                "lbl_text": "Texto:",
                "lbl_font_size": "Tamaño de Letra:",
                "rb_auto": "Automático (Llena el asiento)",
                "rb_fixed": "Fijo:",
                "lbl_student_list": "Lista de Alumnos",
                "btn_load_deck": "🗂 Cargar al Mazo",
                "btn_random": "🔀 Orden Aleatorio",
                "btn_clear_all": "🧹 Vaciar Todos",
                "title_warn": "Aviso",
                "msg_no_desks": "No has dibujado ningún banco en el aula.",
                "title_color_card": "Elige color de tarjeta",
                "title_color_font": "Elige color de letra",
                "title_exported": "Exportado",
                "msg_exported": "La imagen del aula ha sido generada correctamente.",
                "board": "PIZARRA",
                "unassigned": "Alumnos sin asignar: {}",
                "about_title": "Acerca del Autor",
                "about_author": "Autor: Rodolfo Velasco",
                "about_donate": "Si te fue útil, considera invitarme un café:",
                "btn_close": "Cerrar"
            },
            "en": {
                "title_main": "SEATING ARRANGEMENT",
                "btn_create": "Create New Classroom",
                "btn_load": "Load Saved Classroom",
                "btn_about": "About the Author / Donate",
                "msg_new_class": "New Classroom",
                "msg_enter_name": "Enter the name of the Classroom/Course:",
                "title_load": "Load Classroom",
                "msg_no_class": "No saved classrooms found.",
                "btn_back": "⬅ Back",
                "btn_back_menu": "⬅ Back to Menu",
                "btn_rename": "✏️ Rename",
                "btn_delete": "🗑️ Delete",
                "msg_rename": "Rename",
                "msg_enter_new_name": "Enter the new name:",
                "msg_confirm": "Confirm",
                "msg_confirm_del": "Are you sure you want to delete classroom '{}'?",
                "msg_save_success": "Classroom '{}' successfully saved.",
                "msg_saved": "Saved",
                "lbl_mode": "Mode:",
                "rb_draw": "1. Draw Desks",
                "rb_move": "2. Move Students",
                "btn_save": "💾 Save",
                "btn_export": "📷 Export PNG",
                "lbl_course": "Class: {}",
                "lbl_style": "📽️ Card Style (Projector)",
                "lf_vis": "Visibility",
                "lbl_bg": "Background:",
                "lbl_text": "Text:",
                "lbl_font_size": "Font Size:",
                "rb_auto": "Auto (Fills the seat)",
                "rb_fixed": "Fixed:",
                "lbl_student_list": "Student List",
                "btn_load_deck": "🗂 Load to Deck",
                "btn_random": "🔀 Random Order",
                "btn_clear_all": "🧹 Clear All",
                "title_warn": "Warning",
                "msg_no_desks": "You haven't drawn any desks in the classroom.",
                "title_color_card": "Choose card color",
                "title_color_font": "Choose font color",
                "title_exported": "Exported",
                "msg_exported": "The classroom image has been successfully generated.",
                "board": "WHITEBOARD",
                "unassigned": "Unassigned students: {}",
                "about_title": "About the Author",
                "about_author": "Author: Rodolfo Velasco",
                "about_donate": "If you found this useful, consider buying me a coffee:",
                "btn_close": "Close"
            }
        }
        
        self.current_frame = None
        self.show_main_menu()

    def t(self, key):
        return self.translations.get(self.current_lang.get(), {}).get(key, key)

    def clear_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root, bg="#2C3E50")
        self.current_frame.pack(fill="both", expand=True)

    # --- MENÚ PRINCIPAL ---
    def show_main_menu(self):
        self.root.title(self.t("title_main"))
        self.clear_screen()
        
        container = tk.Frame(self.current_frame, bg="#2C3E50")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text=self.t("title_main"), font=("Segoe UI", 36, "bold"), bg="#2C3E50", fg="white").pack(pady=(0, 40))
        tk.Button(container, text=self.t("btn_create"), font=self.title_font, bg="#27AE60", fg="white", width=24, relief="flat", command=self.create_new_classroom).pack(pady=10)
        tk.Button(container, text=self.t("btn_load"), font=self.title_font, bg="#3498DB", fg="white", width=24, relief="flat", command=self.show_load_menu).pack(pady=10)
        tk.Button(container, text=self.t("btn_about"), font=self.normal_font, bg="#8E44AD", fg="white", width=24, relief="flat", command=self.show_about).pack(pady=(20, 10), ipady=4)

        # Selector de Idiomas
        lang_frame = tk.Frame(self.current_frame, bg="#2C3E50")
        lang_frame.pack(side="bottom", pady=20)
        tk.Label(lang_frame, text="🌍 Idioma / Language:", font=self.normal_font, bg="#2C3E50", fg="white").pack(side="left", padx=10)
        tk.Radiobutton(lang_frame, text="Español", variable=self.current_lang, value="es", bg="#2C3E50", fg="white", selectcolor="#34495E", font=self.normal_font, command=self.show_main_menu).pack(side="left", padx=5)
        tk.Radiobutton(lang_frame, text="English", variable=self.current_lang, value="en", bg="#2C3E50", fg="white", selectcolor="#34495E", font=self.normal_font, command=self.show_main_menu).pack(side="left", padx=5)

    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title(self.t("about_title"))
        about_win.geometry("450x320")
        about_win.configure(bg="#34495E")
        about_win.resizable(False, False)
        
        about_win.transient(self.root)
        about_win.grab_set()

        tk.Label(about_win, text=self.t("about_author"), font=("Segoe UI", 18, "bold"), bg="#34495E", fg="white").pack(pady=(30, 10))
        tk.Label(about_win, text=self.t("about_donate"), font=("Segoe UI", 11), bg="#34495E", fg="#BDC3C7").pack(pady=(5, 20))

        btn_cafecito = tk.Button(about_win, text="☕ Cafecito (ARS)", font=("Segoe UI", 12, "bold"), bg="#00A8FF", fg="white", relief="flat", cursor="hand2", 
                                 command=lambda: webbrowser.open_new("https://cafecito.app/rodolfovelasco"))
        btn_cafecito.pack(pady=5, ipadx=10, ipady=5, fill="x", padx=100)

        btn_kofi = tk.Button(about_win, text="☕ Ko-fi (USD)", font=("Segoe UI", 12, "bold"), bg="#FF5E5B", fg="white", relief="flat", cursor="hand2", 
                             command=lambda: webbrowser.open_new("https://ko-fi.com/rodolfovelasco"))
        btn_kofi.pack(pady=5, ipadx=10, ipady=5, fill="x", padx=100)
        
        tk.Button(about_win, text=self.t("btn_close"), font=("Segoe UI", 10), bg="#7F8C8D", fg="white", relief="flat", command=about_win.destroy).pack(pady=(25, 10), ipadx=20)

    def create_new_classroom(self):
        name = simpledialog.askstring(self.t("msg_new_class"), self.t("msg_enter_name"), parent=self.root)
        if not name: return
        self.classroom_name = name
        self.desks.clear()
        self.assignments.clear()
        self.unassigned.clear()
        self.mode.set("edit")
        self.selected_student = None
        self.show_workspace()

    # --- MENÚ DE CARGA ---
    def show_load_menu(self):
        self.clear_screen()
        
        tk.Label(self.current_frame, text=self.t("title_load"), font=("Segoe UI", 34, "bold"), bg="#2C3E50", fg="white").pack(pady=(60, 30))
        
        files = [f.replace(".json", "") for f in os.listdir(self.base_dir) if f.endswith(".json")]
        
        if not files:
            tk.Label(self.current_frame, text=self.t("msg_no_class"), font=self.title_font, bg="#2C3E50", fg="#BDC3C7").pack(pady=40)
            tk.Button(self.current_frame, text=self.t("btn_back"), font=self.title_font, bg="#E74C3C", fg="white", command=self.show_main_menu, relief="flat", width=15).pack(pady=30)
            return

        if len(files) <= 6:
            list_frame = tk.Frame(self.current_frame, bg="#2C3E50")
            list_frame.pack(pady=10)
            
            for f_name in files:
                item_f = tk.Frame(list_frame, bg="#2C3E50")
                item_f.pack(pady=10)
                
                tk.Button(item_f, text=f_name, font=("Segoe UI", 16, "bold"), width=25, bg="#34495E", fg="white", 
                          relief="flat", anchor="center", cursor="hand2",
                          command=lambda n=f_name: self.load_classroom(n)).pack(side="left", padx=5, ipady=5)
                
                tk.Button(item_f, text=self.t("btn_rename"), font=("Segoe UI", 14), bg="#F39C12", fg="white", 
                          relief="flat", width=12, cursor="hand2",
                          command=lambda n=f_name: self.rename_classroom(n)).pack(side="left", padx=4, ipady=5)
                
                tk.Button(item_f, text=self.t("btn_delete"), font=("Segoe UI", 14), bg="#E74C3C", fg="white", 
                          relief="flat", width=10, cursor="hand2",
                          command=lambda n=f_name: self.delete_classroom(n)).pack(side="left", padx=4, ipady=5)
        else:
            scroll_container = tk.Frame(self.current_frame, bg="#2C3E50")
            scroll_container.pack(pady=10)

            list_canvas = tk.Canvas(scroll_container, bg="#2C3E50", highlightthickness=0, width=750, height=450)
            scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=list_canvas.yview)
            scrollable_frame = tk.Frame(list_canvas, bg="#2C3E50")
            
            scrollable_frame.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
            list_canvas.create_window((375, 0), window=scrollable_frame, anchor="n")
            list_canvas.configure(yscrollcommand=scrollbar.set)
            
            list_canvas.pack(side="left")
            scrollbar.pack(side="right", fill="y")
            
            for f_name in files:
                item_f = tk.Frame(scrollable_frame, bg="#2C3E50")
                item_f.pack(pady=8)
                
                tk.Button(item_f, text=f_name, font=("Segoe UI", 16, "bold"), width=25, bg="#34495E", fg="white", 
                          relief="flat", anchor="center", cursor="hand2",
                          command=lambda n=f_name: self.load_classroom(n)).pack(side="left", padx=8, ipady=6)
                
                tk.Button(item_f, text=self.t("btn_rename"), font=("Segoe UI", 14), bg="#F39C12", fg="white", 
                          relief="flat", width=12, cursor="hand2",
                          command=lambda n=f_name: self.rename_classroom(n)).pack(side="left", padx=4, ipady=5)
                
                tk.Button(item_f, text=self.t("btn_delete"), font=("Segoe UI", 14), bg="#E74C3C", fg="white", 
                          relief="flat", width=10, cursor="hand2",
                          command=lambda n=f_name: self.delete_classroom(n)).pack(side="left", padx=4, ipady=5)

        tk.Button(self.current_frame, text=self.t("btn_back_menu"), font=self.title_font, bg="#E74C3C", fg="white", 
                  command=self.show_main_menu, relief="flat", width=20, cursor="hand2").pack(pady=30, ipady=2)

    def rename_classroom(self, old_name):
        new_name = simpledialog.askstring(self.t("msg_rename"), self.t("msg_enter_new_name"), initialvalue=old_name, parent=self.root)
        if new_name and new_name != old_name:
            with open(os.path.join(self.base_dir, f"{old_name}.json"), "r", encoding='utf-8') as f:
                data = json.load(f)
            data["name"] = new_name
            with open(os.path.join(self.base_dir, f"{new_name}.json"), "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            os.remove(os.path.join(self.base_dir, f"{old_name}.json"))
            self.show_load_menu()

    def delete_classroom(self, name):
        if messagebox.askyesno(self.t("msg_confirm"), self.t("msg_confirm_del").format(name)):
            os.remove(os.path.join(self.base_dir, f"{name}.json"))
            self.show_load_menu()

    def load_classroom(self, name):
        with open(os.path.join(self.base_dir, f"{name}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.classroom_name = data.get("name", name)
        self.desks = set(tuple(x) for x in data["desks"])
        self.assignments = {}
        for key, val in data.get("assignments", {}).items():
            r, c = map(int, key.split(","))
            self.assignments[(r, c)] = val
            
        self.card_color = data.get("card_color", "#FFFFFF")
        self.card_text_color = data.get("card_text_color", "#000000")
        self.font_mode.set(data.get("font_mode", "auto"))
        self.fixed_font_size.set(data.get("fixed_font_size", 12))
        
        self.unassigned = []
        self.show_workspace()
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", data.get("students", ""))
        self.mode.set("assign")
        self.selected_student = None
        self.update_unassigned_deck()

    def save_classroom(self):
        data = {
            "name": self.classroom_name,
            "desks": list(self.desks),
            "assignments": {f"{r},{c}": name for (r, c), name in self.assignments.items()},
            "students": self.text_area.get("1.0", tk.END),
            "card_color": self.card_color,
            "card_text_color": self.card_text_color,
            "font_mode": self.font_mode.get(),
            "fixed_font_size": self.fixed_font_size.get()
        }
        filename = os.path.join(self.base_dir, f"{self.classroom_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        messagebox.showinfo(self.t("msg_saved"), self.t("msg_save_success").format(self.classroom_name))

    # --- ESPACIO DE TRABAJO ---
    def show_workspace(self):
        self.clear_screen()
        
        top_panel = tk.Frame(self.current_frame, bg="#34495E", pady=6, padx=12)
        top_panel.pack(fill="x", side="top")
        
        tk.Button(top_panel, text=self.t("btn_back"), font=self.normal_font, bg="#E74C3C", fg="white", relief="flat", command=self.show_main_menu).pack(side="left")
        
        tk.Label(top_panel, text=self.t("lbl_mode"), font=("Segoe UI", 11, "bold"), bg="#34495E", fg="#F1C40F").pack(side="left", padx=(15, 5))
        tk.Radiobutton(top_panel, text=self.t("rb_draw"), variable=self.mode, value="edit", 
                       font=self.normal_font, bg="#34495E", fg="white", selectcolor="#2C3E50", 
                       command=self.handle_mode_change).pack(side="left", padx=4)
        tk.Radiobutton(top_panel, text=self.t("rb_move"), variable=self.mode, value="assign", 
                       font=self.normal_font, bg="#34495E", fg="white", selectcolor="#2C3E50", 
                       command=self.handle_mode_change).pack(side="left", padx=4)

        tk.Button(top_panel, text=self.t("btn_save"), font=self.normal_font, bg="#2980B9", fg="white", relief="flat", command=self.save_classroom).pack(side="right", padx=4)
        tk.Button(top_panel, text=self.t("btn_export"), font=self.normal_font, bg="#8E44AD", fg="white", relief="flat", command=self.export_image).pack(side="right", padx=4)
        tk.Label(top_panel, text=self.t("lbl_course").format(self.classroom_name), font=("Segoe UI", 12, "bold"), bg="#34495E", fg="white").pack(side="right", padx=10)

        workspace_body = tk.Frame(self.current_frame, bg="#2C3E50")
        workspace_body.pack(fill="both", expand=True)

        canvas_container = tk.Frame(workspace_body, bg="#BDC3C7")
        canvas_container.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(canvas_container, bg="#ECF0F1", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_window_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Panel Lateral Derecho
        right_panel_container = tk.Frame(workspace_body, bg="#34495E", width=340)
        right_panel_container.pack(side="right", fill="y", padx=(0, 8), pady=8)
        right_panel_container.pack_propagate(False)

        right_canvas = tk.Canvas(right_panel_container, bg="#34495E", highlightthickness=0)
        right_scroll = tk.Scrollbar(right_panel_container, orient="vertical", command=right_canvas.yview)
        right_content = tk.Frame(right_canvas, bg="#34495E")

        right_content.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
        right_canvas.create_window((0, 0), window=right_content, anchor="nw", width=320)
        right_canvas.configure(yscrollcommand=right_scroll.set)

        right_canvas.pack(side="left", fill="both", expand=True)
        right_scroll.pack(side="right", fill="y")

        tk.Label(right_content, text=self.t("lbl_style"), font=("Segoe UI", 11, "bold"), bg="#34495E", fg="#F1C40F").pack(pady=(6, 3))
        
        style_box = tk.LabelFrame(right_content, text=self.t("lf_vis"), font=("Segoe UI", 9, "bold"), bg="#2C3E50", fg="white", padx=8, pady=6)
        style_box.pack(fill="x", padx=8, pady=4)

        c_row1 = tk.Frame(style_box, bg="#2C3E50")
        c_row1.pack(fill="x", pady=2)
        tk.Label(c_row1, text=self.t("lbl_bg"), font=("Segoe UI", 9), bg="#2C3E50", fg="white").pack(side="left")
        self.btn_card_color = tk.Button(c_row1, text="      ", bg=self.card_color, relief="groove", command=self.pick_card_color)
        self.btn_card_color.pack(side="left", padx=6)
        for c in ["#FFFFFF", "#F1C40F", "#2ECC71", "#3498DB"]:
            tk.Button(c_row1, bg=c, width=2, relief="flat", command=lambda col=c: self.set_card_color_quick(col)).pack(side="left", padx=1)

        c_row2 = tk.Frame(style_box, bg="#2C3E50")
        c_row2.pack(fill="x", pady=2)
        tk.Label(c_row2, text=self.t("lbl_text"), font=("Segoe UI", 9), bg="#2C3E50", fg="white").pack(side="left")
        self.btn_text_color = tk.Button(c_row2, text="      ", bg=self.card_text_color, relief="groove", command=self.pick_text_color)
        self.btn_text_color.pack(side="left", padx=6)
        for tc in ["#000000", "#FFFFFF", "#1B4F72"]:
            tk.Button(c_row2, bg=tc, width=2, relief="flat", command=lambda col=tc: self.set_text_color_quick(col)).pack(side="left", padx=1)

        tk.Label(style_box, text=self.t("lbl_font_size"), font=("Segoe UI", 9, "bold"), bg="#2C3E50", fg="white").pack(anchor="w", pady=(4, 0))
        tk.Radiobutton(style_box, text=self.t("rb_auto"), variable=self.font_mode, value="auto",
                       font=("Segoe UI", 8), bg="#2C3E50", fg="white", selectcolor="#34495E",
                       command=self.draw_grid).pack(anchor="w")
        
        fixed_row = tk.Frame(style_box, bg="#2C3E50")
        fixed_row.pack(fill="x")
        tk.Radiobutton(fixed_row, text=self.t("rb_fixed"), variable=self.font_mode, value="fixed",
                       font=("Segoe UI", 8), bg="#2C3E50", fg="white", selectcolor="#34495E",
                       command=self.draw_grid).pack(side="left")
        tk.Spinbox(fixed_row, from_=8, to=26, textvariable=self.fixed_font_size, width=4, font=("Segoe UI", 9), command=self.draw_grid).pack(side="left", padx=4)

        tk.Label(right_content, text=self.t("lbl_student_list"), font=("Segoe UI", 11, "bold"), bg="#34495E", fg="#F1C40F").pack(pady=(10, 2))
        
        self.text_area = tk.Text(right_content, font=("Segoe UI", 10), width=26, height=10, wrap="word")
        self.text_area.pack(pady=4, fill="x", padx=8)
        
        tk.Button(right_content, text=self.t("btn_load_deck"), font=self.normal_font, bg="#27AE60", fg="white", relief="flat", command=self.update_unassigned_deck).pack(fill="x", padx=8, pady=3)
        tk.Button(right_content, text=self.t("btn_random"), font=self.normal_font, bg="#F39C12", fg="white", relief="flat", command=self.randomize_students).pack(fill="x", padx=8, pady=3)
        tk.Button(right_content, text=self.t("btn_clear_all"), font=self.normal_font, bg="#E74C3C", fg="white", relief="flat", command=self.clear_assignments).pack(fill="x", padx=8, pady=(8, 15))

    def on_window_resize(self, event):
        new_w = event.width
        new_h = event.height
        
        espacio_alto_grilla = new_h * 0.82 - self.grid_offset_y
        espacio_ancho_grilla = new_w - 20
        
        self.cell_w = max(70, int(espacio_ancho_grilla // self.cols))
        self.cell_h = max(55, int(espacio_alto_grilla // self.rows))
        
        self.draw_grid()

    def pick_card_color(self):
        col = colorchooser.askcolor(initialcolor=self.card_color, title=self.t("title_color_card"))[1]
        if col: self.set_card_color_quick(col)

    def set_card_color_quick(self, col):
        self.card_color = col
        self.btn_card_color.config(bg=col)
        self.draw_grid()

    def pick_text_color(self):
        col = colorchooser.askcolor(initialcolor=self.card_text_color, title=self.t("title_color_font"))[1]
        if col: self.set_text_color_quick(col)

    def set_text_color_quick(self, col):
        self.card_text_color = col
        self.btn_text_color.config(bg=col)
        self.draw_grid()

    def handle_mode_change(self):
        self.selected_student = None
        self.draw_grid()

    def calculate_font_size(self, text, max_w, max_h):
        if self.font_mode.get() == "fixed":
            return max(6, self.fixed_font_size.get())
            
        max_possible = max(10, int(max_h * 0.48))
        for size in range(max_possible, 7, -1):
            test_f = font.Font(family="Segoe UI", size=size, weight="bold")
            if test_f.measure(text) <= (max_w - 6) and test_f.metrics("linespace") <= (max_h - 4):
                return size
        return 8

    def draw_grid(self):
        self.canvas.delete("all")
        is_edit = self.mode.get() == "edit"
        self.unassigned_bboxes.clear()
        
        total_grid_w = self.cols * self.cell_w
        
        pizarra_w = min(480, int(total_grid_w * 0.55))
        pizarra_x1 = (total_grid_w - pizarra_w) / 2
        self.canvas.create_rectangle(pizarra_x1, 8, pizarra_x1 + pizarra_w, 42, fill="#FFFFFF", outline="#BDC3C7", width=2)
        self.canvas.create_text(total_grid_w / 2, 25, text=self.t("board"), font=("Segoe UI", 12, "bold"), fill="#2C3E50")
        
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_w, r * self.cell_h + self.grid_offset_y
                x2, y2 = x1 + self.cell_w, y1 + self.cell_h
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#BDC3C7", dash=(2, 4))
                
        for (r, c) in self.desks:
            x1, y1 = c * self.cell_w + 2, r * self.cell_h + self.grid_offset_y + 2
            x2, y2 = x1 + self.cell_w - 4, y1 + self.cell_h - 4
            bw = self.cell_w - 4
            bh = self.cell_h - 4
            
            fill_color = "#3498DB" if is_edit else "#BDC3C7"
            outline_col = "#2C3E50"
            border_w = 2
            
            if self.selected_student and self.selected_student["source"] == "desk" and self.selected_student["r"] == r and self.selected_student["c"] == c:
                fill_color = "#E67E22"
                outline_col = "white"
                border_w = 3
            elif (r, c) in self.assignments:
                fill_color = self.card_color
                
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_col, width=border_w)
            
            if (r, c) in self.assignments:
                name = self.assignments[(r, c)]
                font_sz = self.calculate_font_size(name, bw, bh)
                card_f = font.Font(family="Segoe UI", size=font_sz, weight="bold")
                
                display_name = name
                while len(display_name) > 3 and card_f.measure(display_name) > (bw - 4):
                    display_name = display_name[:-2] + "…"
                    
                self.canvas.create_text(
                    x1 + bw // 2, 
                    y1 + bh // 2, 
                    text=display_name, 
                    font=card_f, 
                    fill=self.card_text_color
                )

        self.deck_area_y = self.grid_offset_y + (self.rows * self.cell_h) + 12
        
        if not is_edit:
            self.canvas.create_text(15, self.deck_area_y + 8, text=self.t("unassigned").format(len(self.unassigned)), font=("Segoe UI", 11, "bold"), fill="#2C3E50", anchor="w")
            
            deck_start_y = self.deck_area_y + 25
            card_w = max(85, int(self.cell_w * 1.05))
            card_h = max(30, int(self.cell_h * 0.52))
            cols_unassigned = max(1, (total_grid_w - 20) // (card_w + 6))
            
            for i, name in enumerate(self.unassigned):
                row = i // cols_unassigned
                col = i % cols_unassigned
                
                x1 = 15 + col * (card_w + 6)
                y1 = deck_start_y + row * (card_h + 6)
                x2 = x1 + card_w
                y2 = y1 + card_h
                
                is_selected = (self.selected_student and self.selected_student["source"] == "deck" and self.selected_student["idx"] == i)
                fill_color = "#E67E22" if is_selected else self.card_color
                outline_col = "white" if is_selected else "#2C3E50"
                width = 3 if is_selected else 1
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_col, width=width)
                
                font_sz = self.calculate_font_size(name, card_w, card_h)
                d_font = font.Font(family="Segoe UI", size=min(12, font_sz), weight="bold")
                
                display_name = name
                while len(display_name) > 3 and d_font.measure(display_name) > (card_w - 4):
                    display_name = display_name[:-2] + "…"
                    
                text_col = "white" if is_selected else self.card_text_color
                self.canvas.create_text(x1 + card_w//2, y1 + card_h//2, text=display_name, font=d_font, fill=text_col)
                self.unassigned_bboxes.append((x1, y1, x2, y2, i, name))

    def update_unassigned_deck(self):
        raw_names = self.text_area.get("1.0", tk.END).split("\n")
        all_names = [n.strip() for n in raw_names if n.strip()]
        seated_names = list(self.assignments.values())
        
        self.unassigned = [n for n in all_names if n not in seated_names]
        self.mode.set("assign")
        self.selected_student = None
        self.draw_grid()

    def randomize_students(self):
        raw_names = self.text_area.get("1.0", tk.END).split("\n")
        names = [n.strip() for n in raw_names if n.strip()]
        
        if not names: return
        if not self.desks:
            messagebox.showwarning(self.t("title_warn"), self.t("msg_no_desks"))
            return
            
        random.shuffle(names)
        desk_list = list(self.desks)
        random.shuffle(desk_list) 
        
        self.assignments.clear()
        self.unassigned.clear()
        
        for i, name in enumerate(names):
            if i < len(desk_list):
                self.assignments[desk_list[i]] = name
            else:
                self.unassigned.append(name)
                
        self.mode.set("assign")
        self.selected_student = None
        self.draw_grid()

    def clear_assignments(self):
        self.assignments.clear()
        self.update_unassigned_deck()

    def _remove_selected_from_source(self):
        s = self.selected_student
        if s["source"] == "desk":
            del self.assignments[(s["r"], s["c"])]
        elif s["source"] == "deck":
            self.unassigned.pop(s["idx"])
            
    def _put_in_source(self, name, source_data):
        if source_data["source"] == "desk":
            self.assignments[(source_data["r"], source_data["c"])] = name
        else:
            self.unassigned.insert(source_data["idx"], name)

    def on_press(self, event):
        canvas_x, canvas_y = event.x, event.y

        if self.mode.get() == "edit":
            if canvas_y >= self.grid_offset_y and canvas_y < self.grid_offset_y + (self.rows * self.cell_h):
                c = int(canvas_x // self.cell_w)
                r = int((canvas_y - self.grid_offset_y) // self.cell_h)
                if 0 <= c < self.cols and 0 <= r < self.rows:
                    if (r, c) in self.desks:
                        self.desks.remove((r, c))
                        if (r, c) in self.assignments: del self.assignments[(r, c)]
                    else:
                        self.desks.add((r, c))
                    self.draw_grid()
            return

        if self.mode.get() == "assign":
            c = int(canvas_x // self.cell_w)
            r = int((canvas_y - self.grid_offset_y) // self.cell_h)
            
            clicked_desk = None
            if 0 <= c < self.cols and 0 <= r < self.rows and (r, c) in self.desks:
                clicked_desk = (r, c)
                
            clicked_deck_idx = None
            for (x1, y1, x2, y2, idx, name) in self.unassigned_bboxes:
                if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                    clicked_deck_idx = idx
                    break

            if self.selected_student:
                if clicked_desk:
                    self._remove_selected_from_source()
                    if clicked_desk in self.assignments:
                        occupant = self.assignments[clicked_desk]
                        self._put_in_source(occupant, self.selected_student)
                    self.assignments[clicked_desk] = self.selected_student["name"]
                    self.selected_student = None
                    self.draw_grid()
                    return
                elif clicked_deck_idx is not None or canvas_y >= self.deck_area_y:
                    self._remove_selected_from_source()
                    self.unassigned.append(self.selected_student["name"])
                    self.selected_student = None
                    self.draw_grid()
                    return
                self.selected_student = None
                self.draw_grid()
                return

            if clicked_desk and clicked_desk in self.assignments:
                name = self.assignments[clicked_desk]
                self.selected_student = {"source": "desk", "r": r, "c": c, "name": name}
            elif clicked_deck_idx is not None:
                name = self.unassigned[clicked_deck_idx]
                self.selected_student = {"source": "deck", "idx": clicked_deck_idx, "name": name}
            else:
                return

            self.draw_grid()
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            self.has_dragged = False
            self.drag_data = None

    def on_drag(self, event):
        canvas_x, canvas_y = event.x, event.y

        if self.mode.get() == "assign" and self.selected_student:
            if not self.has_dragged:
                if abs(canvas_x - self.drag_start_x) > 5 or abs(canvas_y - self.drag_start_y) > 5:
                    self.has_dragged = True
                    self._remove_selected_from_source()
                    self.draw_grid() 
                    
                    w = int(self.cell_w * 0.45)
                    h = int(self.cell_h * 0.4)
                    self.canvas.create_rectangle(canvas_x-w, canvas_y-h, canvas_x+w, canvas_y+h, fill=self.card_color, outline="#2C3E50", width=2, tags="drag_group")
                    self.canvas.create_text(canvas_x, canvas_y, text=self.selected_student["name"][:12], font=("Segoe UI", 10, "bold"), fill=self.card_text_color, tags="drag_group")
                    self.drag_data = {"mouse_x": canvas_x, "mouse_y": canvas_y}
            else:
                dx = canvas_x - self.drag_data["mouse_x"]
                dy = canvas_y - self.drag_data["mouse_y"]
                self.canvas.move("drag_group", dx, dy)
                self.drag_data["mouse_x"] = canvas_x
                self.drag_data["mouse_y"] = canvas_y

    def on_release(self, event):
        canvas_x, canvas_y = event.x, event.y

        if self.mode.get() == "assign" and self.selected_student and self.has_dragged:
            self.canvas.delete("drag_group")
            
            c = int(canvas_x // self.cell_w)
            r = int((canvas_y - self.grid_offset_y) // self.cell_h)
            
            if 0 <= c < self.cols and 0 <= r < self.rows and (r, c) in self.desks:
                occupant = self.assignments.get((r, c))
                if occupant:
                    self._put_in_source(occupant, self.selected_student)
                self.assignments[(r, c)] = self.selected_student["name"]
            else:
                self.unassigned.append(self.selected_student["name"])
                
            self.selected_student = None
            self.drag_data = None
            self.draw_grid()

    def export_image(self):
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], initialfile=f"{self.classroom_name}_mapa")
        if not filename: return

        img_w = self.cols * self.cell_w
        img_h = (self.rows * self.cell_h) + self.grid_offset_y
        img = Image.new("RGB", (img_w, img_h), "#ECF0F1")
        draw = ImageDraw.Draw(img)

        pizarra_w = int(img_w * 0.5)
        pizarra_x1 = (img_w - pizarra_w) / 2
        draw.rectangle([pizarra_x1, 10, pizarra_x1 + pizarra_w, 45], fill="#FFFFFF", outline="#BDC3C7", width=2)
        
        try: font_title = ImageFont.truetype("arialbd.ttf", 16)
        except: font_title = ImageFont.load_default()
        
        t_bbox = draw.textbbox((0, 0), self.t("board"), font=font_title)
        tw, th = t_bbox[2] - t_bbox[0], t_bbox[3] - t_bbox[1]
        draw.text((pizarra_x1 + (pizarra_w - tw)/2, 10 + (35 - th)/2), self.t("board"), fill="#2C3E50", font=font_title)

        for r in range(self.rows + 1):
            y = r * self.cell_h + self.grid_offset_y
            draw.line([(0, y), (img_w, y)], fill="#BDC3C7")
        for c in range(self.cols + 1):
            x = c * self.cell_w
            draw.line([(x, self.grid_offset_y), (x, img_h)], fill="#BDC3C7")

        for (r, c) in self.desks:
            x1 = c * self.cell_w + 3
            y1 = r * self.cell_h + self.grid_offset_y + 3
            x2 = x1 + self.cell_w - 6
            y2 = y1 + self.cell_h - 6
            bw = self.cell_w - 6
            bh = self.cell_h - 6
            
            fill_col = self.card_color if (r, c) in self.assignments else "#BDC3C7"
            draw.rectangle([x1, y1, x2, y2], fill=fill_col, outline="#2C3E50", width=2)
            
            if (r, c) in self.assignments:
                name = self.assignments[(r, c)]
                
                font_pt = 12
                if self.font_mode.get() == "fixed":
                    font_pt = self.fixed_font_size.get()
                else:
                    max_pt = max(10, int(bh * 0.48))
                    for pt in range(max_pt, 7, -1):
                        try: tf = ImageFont.truetype("arialbd.ttf", pt)
                        except: tf = ImageFont.load_default()
                        tb = draw.textbbox((0, 0), name, font=tf)
                        if (tb[2]-tb[0]) <= (bw - 6) and (tb[3]-tb[1]) <= (bh - 6):
                            font_pt = pt
                            break

                try: card_font = ImageFont.truetype("arialbd.ttf", font_pt)
                except: card_font = ImageFont.load_default()

                text_bbox = draw.textbbox((0, 0), name, font=card_font)
                tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
                
                display_name = name
                while len(display_name) > 3 and tw > (bw - 6):
                    display_name = display_name[:-2] + "…"
                    text_bbox = draw.textbbox((0, 0), display_name, font=card_font)
                    tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

                tx = x1 + (bw - tw) / 2
                ty = y1 + (bh - th) / 2
                draw.text((tx, ty), display_name, fill=self.card_text_color, font=card_font)

        img.save(filename)
        messagebox.showinfo(self.t("title_exported"), self.t("msg_exported"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SeatingChartApp(root)
    root.mainloop()