import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Configuración Global de Estilo
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Generador de Etiquetas - Sephu Modern")
        self.geometry("1100x700")
        
        # Variables de estado
        self.panaderia_seleccionada = None
        self.etiquetas_base_dir = None
        self.etiquetas_base = {}
        self.etiquetas_con_fecha = []
        self.plantilla_imagen = None
        self.font_size = 45
        self.config_file = "config_etiquetas.json"
        
        # Variables de PDF
        self.spacing = 6
        self.dpi = 300
        self.cols, self.rows = 5, 4

        # Variables de UI
        self.imagen_previa = None
        
        # Configuración específica por panadería
        self.tamanos_fuente = {"MaxiRico": 65, "Nanas": 55}
        self.recuadros = {
            "MaxiRico": {
                "lote": (220, 1250, 400, 150),
                "vence": (1150, 1250, 400, 150)
            },
            "Nanas": {
                "lote": (200, 1300, 400, 150),
                "vence": (780, 1300, 400, 150)
            }
        }

        # Inicialización
        self.verificar_carpetas_panaderias()
        self.crear_layout_principal()
        self.cargar_config()

        # Si no hay panadería seleccionada, mostrar selector
        if not self.panaderia_seleccionada:
            self.show_frame("selector")
        else:
            self.actualizar_interfaz_panaderia()
            self.show_frame("editor")

    def verificar_carpetas_panaderias(self):
        for carpeta in ["MaxiRico", "Nanas"]:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)

    def crear_layout_principal(self):
        # Grid layout 1x2 (Sidebar | Contenido)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Sephu\nEtiquetas", 
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_btn_home = ctk.CTkButton(self.sidebar_frame, text="Inicio / Panadería", 
                                            command=lambda: self.show_frame("selector"))
        self.sidebar_btn_home.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_btn_editor = ctk.CTkButton(self.sidebar_frame, text="Editor de Fechas", 
                                              command=lambda: self.show_frame("editor"))
        self.sidebar_btn_editor.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_btn_pdf = ctk.CTkButton(self.sidebar_frame, text="Generar PDF", 
                                           command=lambda: self.show_frame("pdf"))
        self.sidebar_btn_pdf.grid(row=3, column=0, padx=20, pady=10)
        
        self.sidebar_btn_config = ctk.CTkButton(self.sidebar_frame, text="Configuración", 
                                           command=lambda: self.show_frame("config"))
        self.sidebar_btn_config.grid(row=4, column=0, padx=20, pady=10)

        # Footer Sidebar
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                           values=["System", "Light", "Dark"],
                                                           command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        # --- Frames de Contenido ---
        self.frames = {}
        
        # 1. Selector de Panadería
        self.frames["selector"] = self.crear_frame_selector()
        
        # 2. Editor
        self.frames["editor"] = self.crear_frame_editor()
        
        # 3. PDF
        self.frames["pdf"] = self.crear_frame_pdf()
        
        # 4. Config
        self.frames["config"] = self.crear_frame_config()

    def show_frame(self, name):
        # Ocultar todos
        for frame in self.frames.values():
            frame.grid_forget()
        # Mostrar seleccionado
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        
        # Actualizar estado botones
        # (Opcional: resaltar botón activo)

    # --- PANTALLAS ---

    def crear_frame_selector(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="Selecciona tu Panadería", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.btn_iso_maxi = ctk.CTkButton(btn_frame, text="MaxiRico", width=200, height=100,
                                        font=ctk.CTkFont(size=20),
                                        command=lambda: self.seleccionar_panaderia("MaxiRico"))
        self.btn_iso_maxi.pack(side="left", padx=20)

        self.btn_iso_nanas = ctk.CTkButton(btn_frame, text="Nanas", width=200, height=100,
                                         font=ctk.CTkFont(size=20),
                                         command=lambda: self.seleccionar_panaderia("Nanas"))
        self.btn_iso_nanas.pack(side="left", padx=20)
        
        ctk.CTkLabel(frame, text="Las carpetas se crearán automáticamente si no existen.").pack(pady=20)
        return frame

    def crear_frame_editor(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(1, weight=1) # Columna derecha (preview) expandible
        frame.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(frame, height=50, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.lbl_editor_titulo = ctk.CTkLabel(header, text="Editor de Etiquetas", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_editor_titulo.pack(side="left", padx=20, pady=10)
        
        # Columna Izquierda: Lista de Etiquetas Disponibles y Controles
        left_panel = ctk.CTkFrame(frame, width=350, corner_radius=0)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_panel.grid_rowconfigure(1, weight=1) # La lista se expande
        
        ctk.CTkLabel(left_panel, text="1. Selecciona Etiqueta Base", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Scrollable Frame para simular Grid de Cards
        self.scroll_bases = ctk.CTkScrollableFrame(left_panel, label_text="Imágenes Disponibles")
        self.scroll_bases.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_panel, text="2. Configura Fechas", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        
        form_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        form_frame.pack(fill="x", padx=10, pady=5)
        
        self.entry_fecha_lote = ctk.CTkEntry(form_frame, placeholder_text="Producción (DD/MM/YYYY)")
        self.entry_fecha_lote.pack(fill="x", pady=5)
        self.entry_fecha_lote.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        self.entry_fecha_vence = ctk.CTkEntry(form_frame, placeholder_text="Vencimiento (DD/MM/YYYY)")
        self.entry_fecha_vence.pack(fill="x", pady=5)
        self.entry_fecha_vence.insert(0, (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y"))
        
        self.entry_cantidad = ctk.CTkEntry(form_frame, placeholder_text="Cantidad de hojas")
        self.entry_cantidad.pack(fill="x", pady=5)
        self.entry_cantidad.insert(0, "1")
        
        self.btn_agregar_lista = ctk.CTkButton(left_panel, text="Añadir a la Lista de Impresión", 
                                             command=self.generar_etiqueta_accion)
        self.btn_agregar_lista.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(left_panel, text="Importar Nueva Imagen...", 
                             fg_color="gray", command=self.importar_imagen).pack(fill="x", padx=10, pady=5)

        # Columna Derecha: Vista Previa y Lista de Salida
        right_panel = ctk.CTkFrame(frame, corner_radius=0, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_rowconfigure(0, weight=1) # Panel superior (preview)
        right_panel.grid_rowconfigure(1, weight=1) # Panel inferior (lista)
        
        # Preview Area
        preview_frame = ctk.CTkFrame(right_panel)
        preview_frame.grid(row=0, column=0, sticky="nsew", pady=(0,10))
        
        ctk.CTkLabel(preview_frame, text="Vista Previa").pack(pady=5)
        self.preview_canvas = ctk.CTkLabel(preview_frame, text="Selecciona una imagen", corner_radius=10)
        self.preview_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bottom List (Cola de impresión)
        queue_frame = ctk.CTkFrame(right_panel)
        queue_frame.grid(row=1, column=0, sticky="nsew")
        
        queue_header = ctk.CTkFrame(queue_frame, fg_color="transparent")
        queue_header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(queue_header, text="Cola de Impresión", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(queue_header, text="Limpiar Todo", width=80, fg_color="#FF5555", 
                     command=self.limpiar_cola).pack(side="right")
        
        self.scroll_queue = ctk.CTkScrollableFrame(queue_frame)
        self.scroll_queue.pack(fill="both", expand=True, padx=5, pady=5)

        return frame

    def crear_frame_pdf(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        ctk.CTkLabel(frame, text="Generación de PDF", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        
        settings_frame = ctk.CTkFrame(frame)
        settings_frame.pack(padx=20, pady=20)
        
        # Grid settings
        ctk.CTkLabel(settings_frame, text="Filas").grid(row=0, column=0, padx=10, pady=10)
        self.entry_rows = ctk.CTkEntry(settings_frame, width=60)
        self.entry_rows.insert(0, str(self.rows))
        self.entry_rows.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(settings_frame, text="Columnas").grid(row=0, column=2, padx=10, pady=10)
        self.entry_cols = ctk.CTkEntry(settings_frame, width=60)
        self.entry_cols.insert(0, str(self.cols))
        self.entry_cols.grid(row=0, column=3, padx=10, pady=10)
        
        ctk.CTkLabel(settings_frame, text="Espaciado (puntos)").grid(row=0, column=4, padx=10, pady=10)
        self.entry_spacing = ctk.CTkEntry(settings_frame, width=60)
        self.entry_spacing.insert(0, str(self.spacing))
        self.entry_spacing.grid(row=0, column=5, padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=30)
        
        self.btn_generar_final = ctk.CTkButton(frame, text="Guardar PDF", height=50, 
                                             font=ctk.CTkFont(size=18, weight="bold"),
                                             command=self.generar_pdf_accion)
        self.btn_generar_final.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(frame, text="")
        self.lbl_status.pack(pady=10)
        
        return frame

    def crear_frame_config(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(frame, text="Configuraciones Avanzadas", font=ctk.CTkFont(size=20)).pack(pady=20)
        
        # Plantilla Overlay
        p_frame = ctk.CTkFrame(frame)
        p_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(p_frame, text="Plantilla (Marca de agua/Overlay)").pack(side="left", padx=20)
        self.btn_plantilla = ctk.CTkButton(p_frame, text="Seleccionar...", command=self.seleccionar_plantilla)
        self.btn_plantilla.pack(side="right", padx=20, pady=20)
        self.lbl_plantilla_status = ctk.CTkLabel(p_frame, text="Ninguna", text_color="gray")
        self.lbl_plantilla_status.pack(side="right", padx=10)

        # Tamaño fuente
        f_frame = ctk.CTkFrame(frame)
        f_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(f_frame, text="Tamaño de Fuente").pack(side="left", padx=20)
        self.slider_font = ctk.CTkSlider(f_frame, from_=20, to=100, number_of_steps=80, 
                                       command=self.preview_font_size)
        self.slider_font.pack(side="right", padx=20, pady=20, fill="x", expand=True)
        self.lbl_font_size = ctk.CTkLabel(f_frame, text="45")
        self.lbl_font_size.pack(side="right", padx=10)
        
        ctk.CTkButton(frame, text="Guardar Cambios", command=self.guardar_config).pack(pady=30)
        
        return frame

    # --- LÓGICA DE INTERFAZ MODERNA ---
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def seleccionar_panaderia(self, nombre):
        self.panaderia_seleccionada = nombre
        self.etiquetas_base_dir = nombre
        self.font_size = self.tamanos_fuente.get(nombre, 45)
        self.slider_font.set(self.font_size)
        self.lbl_font_size.configure(text=str(self.font_size))
        
        self.cargar_etiquetas_base()
        self.cargar_config()
        self.show_frame("editor")
        self.actualizar_interfaz_panaderia()

    def actualizar_interfaz_panaderia(self):
        self.lbl_editor_titulo.configure(text=f"Editor - {self.panaderia_seleccionada}")

    def cargar_etiquetas_base(self):
        # Limpiar scrollable frame
        for widget in self.scroll_bases.winfo_children():
            widget.destroy()

        self.etiquetas_base = {}
        self.selected_base = None
        
        if not self.etiquetas_base_dir or not os.path.exists(self.etiquetas_base_dir):
            return

        files = [f for f in os.listdir(self.etiquetas_base_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            ctk.CTkLabel(self.scroll_bases, text="No hay imágenes. Importa una!").pack(pady=20)
            return

        # Grid system simulation in pack
        # Vamos a poner botones con el nombre
        for f in files:
            full_path = os.path.join(self.etiquetas_base_dir, f)
            self.etiquetas_base[f] = full_path
            
            # Crear tarjeta (Button)
            btn = ctk.CTkButton(self.scroll_bases, text=f, 
                              fg_color="transparent", border_width=1, border_color="gray",
                              text_color=("gray10", "gray90"),
                              command=lambda name=f: self.seleccionar_etiqueta_base(name))
            btn.pack(fill="x", pady=2)

    def seleccionar_etiqueta_base(self, nombre):
        self.selected_base = nombre
        # Mostrar preview
        ruta = self.etiquetas_base[nombre]
        self.actualizar_preview_simple(ruta)

    def actualizar_preview_simple(self, ruta):
        try:
            pil_img = Image.open(ruta)
            # Resize
            aspect = pil_img.width / pil_img.height
            target_h = 300
            target_w = int(target_h * aspect)
            
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))
            self.preview_canvas.configure(image=ctk_img, text="")
        except Exception as e:
            print(e)

    def importar_imagen(self):
        file = filedialog.askopenfilename(filetypes=[("Imagenes", "*.jpg *.png *.jpeg")])
        if file and self.etiquetas_base_dir:
            dest = os.path.join(self.etiquetas_base_dir, os.path.basename(file))
            shutil.copy2(file, dest)
            self.cargar_etiquetas_base()

    def generar_etiqueta_accion(self):
        if not hasattr(self, 'selected_base') or not self.selected_base:
            messagebox.showwarning("Atención", "Selecciona una imagen base primero")
            return

        try:
            f_prod = self.entry_fecha_lote.get()
            f_vence = self.entry_fecha_vence.get()
            dias = int(self.entry_cantidad.get())
            
            # Validar fechas
            fecha_lote = datetime.strptime(f_prod, "%d/%m/%Y")
            fecha_vence = datetime.strptime(f_vence, "%d/%m/%Y")
            
            ruta_base = self.etiquetas_base[self.selected_base]
            
            for i in range(dias):
                curr_lote = (fecha_lote + timedelta(days=i)).strftime("%d/%m/%Y")
                curr_vence = (fecha_vence + timedelta(days=i)).strftime("%d/%m/%Y")
                
                img_procesada = self.procesar_imagen(ruta_base, curr_lote, curr_vence)
                
                info = {
                    'nombre': f"{self.selected_base} | {curr_lote}",
                    'imagen': img_procesada,
                    'lote': curr_lote
                }
                self.etiquetas_con_fecha.append(info)
                self.agregar_a_cola_ui(info)
            
            self.show_frame("editor") # Focus
            messagebox.showinfo("Éxito", f"Se añadieron {dias} etiquetas a la cola.")

        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido (DD/MM/YYYY) o número incorrecto")

    def agregar_a_cola_ui(self, info):
        # Añade un item visual a la cola
        frame = ctk.CTkFrame(self.scroll_queue, fg_color=("gray90", "gray20"))
        frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(frame, text=info['nombre']).pack(side="left", padx=10)
        ctk.CTkButton(frame, text="X", width=30, fg_color="red", 
                    command=lambda: self.remover_de_cola(info, frame)).pack(side="right", padx=5)

    def remover_de_cola(self, info, widget):
        if info in self.etiquetas_con_fecha:
            self.etiquetas_con_fecha.remove(info)
        widget.destroy()

    def limpiar_cola(self):
        self.etiquetas_con_fecha = []
        for widget in self.scroll_queue.winfo_children():
            widget.destroy()

    def procesar_imagen(self, ruta, f_lote, f_vence):
        imagen = Image.open(ruta).convert('RGBA')
        
        if self.plantilla_imagen:
            try:
                plant = Image.open(self.plantilla_imagen).convert('RGBA')
                plant = plant.resize(imagen.size, Image.Resampling.LANCZOS)
                imagen = Image.alpha_composite(imagen, plant)
            except: pass

        draw = ImageDraw.Draw(imagen)
        
        # Font Loading (Mac Robust)
        font_names = [
            "arialbd.ttf", "Arial Bold.ttf", "Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf", 
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        ]
        font = None
        for fn in font_names:
            try:
                font = ImageFont.truetype(fn, self.font_size)
                break
            except: continue
        if not font: font = ImageFont.load_default()

        # Dibujar
        rects = self.recuadros.get(self.panaderia_seleccionada, {})
        if "lote" in rects:
            self.dibujar_centrado(draw, f_lote, rects["lote"], font)
        if "vence" in rects:
            self.dibujar_centrado(draw, f_vence, rects["vence"], font)
            
        return imagen.convert('RGB')

    def dibujar_centrado(self, draw, texto, rect, font):
        x, y, w, h = rect
        bbox = draw.textbbox((0, 0), texto, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x + (w - tw)//2, y + (h - th)//2), texto, fill="black", font=font)

    # --- PDF ---
    def generar_pdf_accion(self):
        if not self.etiquetas_con_fecha:
            messagebox.showwarning("Vacío", "La cola de impresión está vacía")
            return
            
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not output: return
        
        try:
            self.btn_generar_final.configure(state="disabled")
            self.lbl_status.configure(text="Generando...")
            self.update()
            
            c_cols = int(self.entry_cols.get())
            c_rows = int(self.entry_rows.get())
            c_spac = int(self.entry_spacing.get())
            
            # Logic from original
            ppi = 72
            pw = 11 * ppi
            ph = 8.5 * ppi
            scale = self.dpi / ppi
            pw_px = int(pw * scale)
            ph_px = int(ph * scale)
            sp_px = int(c_spac * scale)
            
            cw = (pw_px - (sp_px * (c_cols + 1))) // c_cols + 2
            ch = (ph_px - (sp_px * (c_rows + 1))) // c_rows + 2
            
            c = canvas.Canvas(output, pagesize=(pw, ph))
            
            total = len(self.etiquetas_con_fecha)
            for i, info in enumerate(self.etiquetas_con_fecha):
                self.progress_bar.set((i+1)/total)
                self.update()
                
                img = info['imagen']
                page = Image.new('RGB', (pw_px, ph_px), 'white')
                
                # Simple repeating pattern or single logic? 
                # Original logic was creating ONE page per label but filling it? 
                # Wait, original loop: "for i, etiqueta_info in enumerate(self.etiquetas_con_fecha)"
                # "for row in range... for col in range..."
                # It made ONE FULL PAGE of the SAME sticker for EACH entry in the list?
                # Yes. "page_img.paste(img_copy...)" inside nested loops.
                
                for r in range(c_rows):
                    for col in range(c_cols):
                        x = sp_px + col * (cw + sp_px - 2)
                        y = sp_px + r * (ch + sp_px - 2)
                        ic = img.copy()
                        ic.thumbnail((cw, ch), Image.Resampling.LANCZOS)
                        page.paste(ic, (x + (cw - ic.width)//2, y + (ch - ic.height)//2))
                
                tmp = f"temp_{i}.tiff"
                page.save(tmp, dpi=(self.dpi, self.dpi))
                c.drawImage(ImageReader(tmp), 0, 0, width=pw, height=ph)
                c.showPage()
                os.remove(tmp)
            
            c.save()
            messagebox.showinfo("Hecho", "PDF Generado con éxito")
            self.lbl_status.configure(text="Listo")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_generar_final.configure(state="normal")
            self.progress_bar.set(0)

    # --- CONFIG ---
    def seleccionar_plantilla(self):
        f = filedialog.askopenfilename()
        if f:
            self.plantilla_imagen = f
            self.lbl_plantilla_status.configure(text=os.path.basename(f))
            
    def preview_font_size(self, value):
        self.font_size = int(value)
        self.lbl_font_size.configure(text=str(self.font_size))

    def cargar_config(self):
        try:
            cf = f"config_{self.panaderia_seleccionada.lower()}.json" if self.panaderia_seleccionada else self.config_file
            if os.path.exists(cf):
                with open(cf) as f:
                    d = json.load(f)
                    self.plantilla_imagen = d.get('plantilla_imagen')
                    fs = d.get('font_size')
                    if fs: 
                        self.font_size = int(fs)
                        self.slider_font.set(self.font_size)
                        self.lbl_font_size.configure(text=str(self.font_size))
        except: pass

    def guardar_config(self):
        if not self.panaderia_seleccionada: return
        data = {
            'panaderia': self.panaderia_seleccionada,
            'plantilla_imagen': self.plantilla_imagen,
            'font_size': self.font_size
        }
        cf = f"config_{self.panaderia_seleccionada.lower()}.json"
        with open(cf, 'w') as f:
            json.dump(data, f)
        messagebox.showinfo("Guardado", "Configuración guardada")

if __name__ == "__main__":
    app = App()
    app.mainloop()