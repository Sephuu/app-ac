import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json
from datetime import datetime, timedelta
import shutil

class PopupTemporizado:
    def __init__(self, parent, mensaje, duracion=2000):
        self.parent = parent
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("")
        self.ventana.geometry("300x100")
        self.ventana.resizable(False, False)
        
        # Centrar el popup en la ventana principal
        # Posicionar el popup en la esquina inferior derecha
        parent.update_idletasks()
        popup_width = 300
        popup_height = 100
        margin = 20
        x = parent.winfo_x() + parent.winfo_width() - popup_width - margin
        y = parent.winfo_y() + parent.winfo_height() - popup_height - margin
        self.ventana.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        # Configurar ventana
        self.ventana.configure(bg="#4CAF50")
        self.ventana.overrideredirect(True)  # Quitar bordes
        
        # Crear el mensaje
        label = tk.Label(
            self.ventana, 
            text=mensaje,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 11, "bold"),
            wraplength=280
        )
        label.pack(expand=True)
        
        # Hacer que se desvanezca automáticamente
        self.ventana.after(duracion, self.cerrar)
        
        # Hacer que se pueda cerrar haciendo clic
        self.ventana.bind("<Button-1>", lambda e: self.cerrar())
        label.bind("<Button-1>", lambda e: self.cerrar())
        
    def cerrar(self):
        self.ventana.destroy()

class EtiquetasPanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Etiquetas de Pan - Sephu")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables de panadería
        self.panaderia_seleccionada = None
        self.etiquetas_base_dir = None
        
        # Configuración
        self.config_file = "config_etiquetas.json"
        self.plantilla_imagen = None
        
        # Variables
        self.spacing = 6
        self.dpi = 300
        self.cols, self.rows = 5, 4
        self.etiquetas_base = {}
        self.etiquetas_con_fecha = []
        
        # Tamaños fijos por panadería
        self.tamanos_fuente = {
            "MaxiRico": 65,
            "Nanas": 55
        }
        self.font_size = 45  # Valor inicial temporal
        
        # Coordenadas actualizadas para centrado (x, y, ancho, alto)
        self.recuadros = {
            "MaxiRico": {
                "lote": (220, 1250, 400, 150),  # x, y, ancho, alto
                "vence": (1150, 1250, 400, 150)
            },
            "Nanas": {
                "lote": (200, 1300, 400, 150),
                "vence": (780, 1300, 400, 150)
            }
        }
        
        self.verificar_carpetas_panaderias()
        self.mostrar_selector_panaderia()

    def verificar_carpetas_panaderias(self):
        carpetas_necesarias = ["MaxiRico", "Nanas"]
        carpetas_faltantes = []
        
        for carpeta in carpetas_necesarias:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
                carpetas_faltantes.append(carpeta)
        
        if carpetas_faltantes:
            messagebox.showinfo("Carpetas creadas", 
                              f"Se crearon las carpetas: {', '.join(carpetas_faltantes)}\n"
                              "Coloca las imágenes de etiquetas en sus respectivas carpetas.")

    def mostrar_selector_panaderia(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame_selector = ttk.Frame(self.root, padding=40)
        frame_selector.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(frame_selector, text="Seleccionar Panadería", 
                         font=("Helvetica", 18, "bold"))
        titulo.pack(pady=20)
        
        subtitulo = ttk.Label(frame_selector, text="Selecciona la panadería para generar etiquetas:", 
                            font=("Helvetica", 11))
        subtitulo.pack(pady=10)
        
        frame_botones = ttk.Frame(frame_selector)
        frame_botones.pack(pady=30)
        
        btn_maxirico = ttk.Button(frame_botones, text="MaxiRico", 
                                command=lambda: self.seleccionar_panaderia("MaxiRico"))
        btn_maxirico.pack(pady=10, ipadx=30, ipady=10)
        
        btn_nanas = ttk.Button(frame_botones, text="Nanas", 
                             command=lambda: self.seleccionar_panaderia("Nanas"))
        btn_nanas.pack(pady=10, ipadx=30, ipady=10)
        
        info = ttk.Label(frame_selector, 
                        text="Las etiquetas se cargarán automáticamente\ndesde la carpeta correspondiente",
                        font=("Helvetica", 9), foreground="gray")
        info.pack(pady=20)

    def seleccionar_panaderia(self, panaderia):
        self.panaderia_seleccionada = panaderia
        self.etiquetas_base_dir = panaderia
        self.font_size = self.tamanos_fuente.get(panaderia, 45)
        
        self.root.title(f"Generador de Etiquetas de Pan - Sephu ({panaderia})")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("TNotebook", background="#f0f0f0")
        
        self.cargar_config()
        self.crear_interfaz()
        self.cargar_etiquetas_base()

    def crear_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.frame_base = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_base, text="Etiquetas Base")
        self.crear_pestaña_base()
        
        self.frame_fechas = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_fechas, text="Añadir Fechas")
        self.crear_pestaña_fechas()
        
        self.frame_pdf = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_pdf, text="Generar PDF")
        self.crear_pestaña_pdf()
        
        self.frame_config = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_config, text="Configuración")
        self.crear_pestaña_config()

    def crear_pestaña_base(self):
        titulo_panaderia = ttk.Label(self.frame_base, 
                                   text=f"Etiquetas Base - {self.panaderia_seleccionada}", 
                                   style="Title.TLabel")
        titulo_panaderia.pack(pady=10)
        
        frame_botones = ttk.Frame(self.frame_base)
        frame_botones.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(frame_botones, text="Recargar Etiquetas", 
                 command=self.cargar_etiquetas_base).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Añadir Nueva Etiqueta", 
                 command=self.añadir_nueva_etiqueta).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Eliminar Seleccionada", 
                 command=self.eliminar_etiqueta).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cambiar Panadería", 
                 command=self.cambiar_panaderia).pack(side=tk.RIGHT, padx=5)
        
        info_carpeta = ttk.Label(self.frame_base, 
                               text=f"Carpeta actual: {self.etiquetas_base_dir}/",
                               foreground="blue")
        info_carpeta.pack(anchor=tk.W, padx=20)
        
        frame_contenido = ttk.Frame(self.frame_base)
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        frame_lista = ttk.Frame(frame_contenido)
        frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(frame_lista, text="Etiquetas Base Disponibles:").pack(anchor=tk.W)
        
        scrollbar_base = ttk.Scrollbar(frame_lista)
        scrollbar_base.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_base = tk.Listbox(frame_lista, yscrollcommand=scrollbar_base.set,
                                   selectmode=tk.SINGLE, font=("Helvetica", 9),
                                   width=30, height=20)
        self.lista_base.pack(fill=tk.Y, expand=True)
        self.lista_base.bind('<<ListboxSelect>>', self.mostrar_vista_previa_base)
        scrollbar_base.config(command=self.lista_base.yview)
        
        frame_vista_previa = ttk.Frame(frame_contenido)
        frame_vista_previa.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(frame_vista_previa, text="Vista Previa:").pack(anchor=tk.W)
        
        self.canvas_previa = tk.Canvas(frame_vista_previa, bg="white", width=400, height=400)
        self.canvas_previa.pack(fill=tk.BOTH, expand=True)
        
        self.imagen_previa = None

    def cambiar_panaderia(self):
        if messagebox.askyesno("Cambiar Panadería", 
                             "¿Deseas cambiar de panadería?\nSe perderán las etiquetas con fecha generadas."):
            self.etiquetas_con_fecha = []
            self.mostrar_selector_panaderia()

    def mostrar_vista_previa_base(self, event):
        seleccion = self.lista_base.curselection()
        if seleccion:
            nombre = self.lista_base.get(seleccion[0])
            ruta_imagen = self.etiquetas_base[nombre]
            
            try:
                imagen = Image.open(ruta_imagen)
                img_width, img_height = imagen.size
                max_size = 400
                
                if img_width > img_height:
                    new_width = max_size
                    new_height = int(img_height * (max_size / img_width))
                else:
                    new_height = max_size
                    new_width = int(img_width * (max_size / img_height))
                
                imagen = imagen.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                self.imagen_previa = ImageTk.PhotoImage(imagen)
                self.canvas_previa.delete("all")
                self.canvas_previa.create_image(
                    max_size//2, max_size//2, 
                    image=self.imagen_previa, 
                    anchor=tk.CENTER
                )
                
            except Exception as e:
                print(f"Error al mostrar vista previa: {e}")

    def crear_pestaña_fechas(self):
        ttk.Label(self.frame_fechas, text="Añadir Fechas a Etiquetas", 
                 style="Title.TLabel").pack(pady=10)
        
        frame_principal = ttk.Frame(self.frame_fechas)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        frame_izquierdo = ttk.Frame(frame_principal)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        frame_seleccion = ttk.LabelFrame(frame_izquierdo, text="Seleccionar Etiqueta Base")
        frame_seleccion.pack(fill=tk.X, pady=5)
        
        self.combo_etiquetas = ttk.Combobox(frame_seleccion, state="readonly")
        self.combo_etiquetas.pack(fill=tk.X, padx=10, pady=5)
        
        frame_fechas = ttk.LabelFrame(frame_izquierdo, text="Configurar Fechas")
        frame_fechas.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_fechas, text="Fecha de producción:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.fecha_lote = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha_lote = ttk.Entry(frame_fechas, textvariable=self.fecha_lote, width=15)
        self.entry_fecha_lote.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_fechas, text="Fecha de vencimiento:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.fecha_vence = tk.StringVar(value=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y"))
        self.entry_fecha_vence = ttk.Entry(frame_fechas, textvariable=self.fecha_vence, width=15)
        self.entry_fecha_vence.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_fechas, text="Hojas a generar:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.dias_generar = tk.StringVar(value="1")
        self.entry_dias = ttk.Entry(frame_fechas, textvariable=self.dias_generar, width=10)
        self.entry_dias.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(frame_fechas, text="Generar Etiquetas con Fechas", 
                  command=self.generar_etiquetas_fecha).grid(row=3, column=0, columnspan=2, pady=10)
        
        frame_lista = ttk.LabelFrame(frame_izquierdo, text="Etiquetas con Fecha Generadas")
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar_fecha = ttk.Scrollbar(frame_lista)
        scrollbar_fecha.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_con_fecha = tk.Listbox(frame_lista, yscrollcommand=scrollbar_fecha.set,
                                        selectmode=tk.SINGLE, font=("Helvetica", 9),
                                        height=10)
        self.lista_con_fecha.pack(fill=tk.BOTH, expand=True)
        self.lista_con_fecha.bind('<<ListboxSelect>>', self.mostrar_vista_previa_fecha)
        scrollbar_fecha.config(command=self.lista_con_fecha.yview)
        
        frame_botones_lista = ttk.Frame(frame_izquierdo)
        frame_botones_lista.pack(pady=5)
        
        ttk.Button(frame_botones_lista, text="Eliminar Seleccionada", 
                  command=self.eliminar_etiqueta_seleccionada).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_botones_lista, text="Limpiar Todas", 
                  command=self.limpiar_etiquetas_fecha).pack(side=tk.LEFT, padx=2)
        
        frame_derecho = ttk.Frame(frame_principal)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(frame_derecho, text="Vista Previa con Fechas:").pack(anchor=tk.W)
        
        self.canvas_previa_fecha = tk.Canvas(frame_derecho, bg="white", width=500, height=500)
        self.canvas_previa_fecha.pack(fill=tk.BOTH, expand=True)
        
        self.imagen_previa_fecha = None

    def eliminar_etiqueta_seleccionada(self):
        seleccion = self.lista_con_fecha.curselection()
        if seleccion:
            indice = seleccion[0]
            nombre_etiqueta = self.lista_con_fecha.get(indice)
            
            if messagebox.askyesno("Confirmar eliminación", 
                                 f"¿Estás seguro que deseas eliminar la etiqueta:\n'{nombre_etiqueta}'?"):
                del self.etiquetas_con_fecha[indice]
                self.actualizar_lista_con_fecha()
                self.canvas_previa_fecha.delete("all")
                PopupTemporizado(self.root, "Etiqueta eliminada correctamente", 1500)
        else:
            messagebox.showwarning("Sin selección", "Por favor selecciona una etiqueta para eliminar")

    def mostrar_vista_previa_fecha(self, event):
        seleccion = self.lista_con_fecha.curselection()
        if seleccion and seleccion[0] < len(self.etiquetas_con_fecha):
            etiqueta = self.etiquetas_con_fecha[seleccion[0]]
            
            try:
                img_width, img_height = etiqueta['imagen'].size
                max_size = 500
                
                if img_width > img_height:
                    new_width = max_size
                    new_height = int(img_height * (max_size / img_width))
                else:
                    new_height = max_size
                    new_width = int(img_width * (max_size / img_height))
                
                imagen = etiqueta['imagen'].resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                self.imagen_previa_fecha = ImageTk.PhotoImage(imagen)
                self.canvas_previa_fecha.delete("all")
                self.canvas_previa_fecha.create_image(
                    max_size//2, max_size//2, 
                    image=self.imagen_previa_fecha, 
                    anchor=tk.CENTER
                )
                
            except Exception as e:
                print(f"Error al mostrar vista previa: {e}")

    def crear_pestaña_pdf(self):
        ttk.Label(self.frame_pdf, text="Generar PDF de Etiquetas", 
                 style="Title.TLabel").pack(pady=10)
        
        frame_grid = ttk.LabelFrame(self.frame_pdf, text="Configuración de Cuadrícula")
        frame_grid.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(frame_grid, text="Columnas:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_cols = tk.StringVar(value=str(self.cols))
        ttk.Entry(frame_grid, textvariable=self.entry_cols, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_grid, text="Filas:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_rows = tk.StringVar(value=str(self.rows))
        ttk.Entry(frame_grid, textvariable=self.entry_rows, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_grid, text="Espaciado:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_spacing = tk.StringVar(value=str(self.spacing))
        ttk.Entry(frame_grid, textvariable=self.entry_spacing, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(self.frame_pdf, orient=tk.HORIZONTAL, 
                                      length=300, mode='determinate')
        self.progress.pack(pady=20)
        
        self.btn_generar = ttk.Button(self.frame_pdf, text="Generar PDF", 
                                    command=self.generar_pdf)
        self.btn_generar.pack(pady=10)
        
        self.status = ttk.Label(self.frame_pdf, text="Listo para generar PDF")
        self.status.pack(pady=10)

    def crear_pestaña_config(self):
        ttk.Label(self.frame_config, text="Configuración", 
                 style="Title.TLabel").pack(pady=10)
        
        frame_plantilla = ttk.LabelFrame(self.frame_config, text="Plantilla de Imagen")
        frame_plantilla.pack(fill=tk.X, padx=20, pady=10)
        
        self.plantilla_label = ttk.Label(frame_plantilla, text="Ninguna plantilla seleccionada")
        self.plantilla_label.pack(pady=5)
        
        ttk.Button(frame_plantilla, text="Seleccionar Plantilla", 
                  command=self.seleccionar_plantilla).pack(pady=5)
        ttk.Button(frame_plantilla, text="Quitar Plantilla", 
                  command=self.quitar_plantilla).pack(pady=5)
        
        frame_fuente = ttk.LabelFrame(self.frame_config, text="Configuración de Texto")
        frame_fuente.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(frame_fuente, 
                text=f"Tamaño de fuente actual: {self.font_size} (automático por panadería)").pack()
        
        self.entry_font_size = ttk.Entry(frame_fuente, state='readonly', width=10)
        self.entry_font_size.pack(pady=5)
        self.entry_font_size.insert(0, str(self.font_size))
        
        frame_config_btn = ttk.Frame(self.frame_config)
        frame_config_btn.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(frame_config_btn, text="Guardar Configuración", 
                  command=self.guardar_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_config_btn, text="Cargar Configuración", 
                  command=self.cargar_config).pack(side=tk.LEFT, padx=5)

    def cargar_carpeta_etiquetas(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta con etiquetas base")
        if carpeta:
            try:
                archivos_copiados = 0
                for archivo in os.listdir(carpeta):
                    if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                        origen = os.path.join(carpeta, archivo)
                        destino = os.path.join(self.etiquetas_base_dir, archivo)
                        shutil.copy2(origen, destino)
                        archivos_copiados += 1
                
                self.cargar_etiquetas_base()
                PopupTemporizado(self.root, f"Se copiaron {archivos_copiados} etiquetas correctamente", 2000)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar carpeta: {str(e)}")

    def añadir_nueva_etiqueta(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar nueva etiqueta",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if archivo:
            try:
                nombre_archivo = os.path.basename(archivo)
                destino = os.path.join(self.etiquetas_base_dir, nombre_archivo)
                shutil.copy2(archivo, destino)
                self.cargar_etiquetas_base()
                PopupTemporizado(self.root, f"Etiqueta '{nombre_archivo}' añadida correctamente", 2000)
            except Exception as e:
                messagebox.showerror("Error", f"Error al añadir etiqueta: {str(e)}")

    def eliminar_etiqueta(self):
        seleccion = self.lista_base.curselection()
        if seleccion:
            nombre = self.lista_base.get(seleccion[0])
            if messagebox.askyesno("Confirmar", f"¿Eliminar la etiqueta '{nombre}'?"):
                try:
                    archivo = os.path.join(self.etiquetas_base_dir, nombre)
                    os.remove(archivo)
                    self.cargar_etiquetas_base()
                    PopupTemporizado(self.root, f"Etiqueta '{nombre}' eliminada correctamente", 2000)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def cargar_etiquetas_base(self):
        self.etiquetas_base = {}
        if hasattr(self, 'lista_base'):
            self.lista_base.delete(0, tk.END)
        
        if not self.etiquetas_base_dir:
            return
            
        if os.path.exists(self.etiquetas_base_dir):
            archivos_encontrados = 0
            for archivo in os.listdir(self.etiquetas_base_dir):
                if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                    ruta_completa = os.path.join(self.etiquetas_base_dir, archivo)
                    self.etiquetas_base[archivo] = ruta_completa
                    if hasattr(self, 'lista_base'):
                        self.lista_base.insert(tk.END, archivo)
                    archivos_encontrados += 1
            
            if archivos_encontrados == 0:
                if hasattr(self, 'lista_base'):
                    self.lista_base.insert(tk.END, "No hay imágenes en esta carpeta")
                messagebox.showwarning("Carpeta vacía", 
                                     f"No se encontraron imágenes en la carpeta '{self.etiquetas_base_dir}'.\n"
                                     "Añade archivos de imagen (.jpg, .png, etc.) en esta carpeta.")
        else:
            messagebox.showerror("Error", f"No se encontró la carpeta '{self.etiquetas_base_dir}'")
        
        if hasattr(self, 'combo_etiquetas'):
            nombres = list(self.etiquetas_base.keys())
            self.combo_etiquetas['values'] = nombres
            if nombres:
                self.combo_etiquetas.set(nombres[0])

    def generar_etiquetas_fecha(self):
        if not self.combo_etiquetas.get():
            messagebox.showerror("Error", "Selecciona una etiqueta base")
            return
        
        try:
            fecha_lote = datetime.strptime(self.fecha_lote.get(), "%d/%m/%Y")
            fecha_vence = datetime.strptime(self.fecha_vence.get(), "%d/%m/%Y")
            dias = int(self.dias_generar.get())
            
            nombre_base = self.combo_etiquetas.get()
            ruta_base = self.etiquetas_base[nombre_base]
            
            for i in range(dias):
                fecha_lote_actual = fecha_lote + timedelta(days=i)
                fecha_vence_actual = fecha_vence + timedelta(days=i)
                
                fecha_lote_str = fecha_lote_actual.strftime("%d/%m/%Y")
                fecha_vence_str = fecha_vence_actual.strftime("%d/%m/%Y")
                
                imagen_con_fecha = self.añadir_fechas_a_imagen(ruta_base, fecha_lote_str, fecha_vence_str)
                
                etiqueta_info = {
                    'nombre': f"{nombre_base} - Prod: {fecha_lote_str} Venc: {fecha_vence_str}",
                    'imagen': imagen_con_fecha,
                    'fecha_lote': fecha_lote_str,
                    'fecha_vence': fecha_vence_str
                }
                self.etiquetas_con_fecha.append(etiqueta_info)
            
            self.actualizar_lista_con_fecha()
            PopupTemporizado(self.root, f"Se generaron {dias} etiquetas con fechas", 2000)
            
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD/MM/YYYY")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar etiquetas: {str(e)}")

    def añadir_fechas_a_imagen(self, ruta_imagen, fecha_lote_str, fecha_vence_str):
        try:
            imagen = Image.open(ruta_imagen).convert('RGBA')
            
            if self.plantilla_imagen:
                plantilla = Image.open(self.plantilla_imagen).convert('RGBA')
                plantilla = plantilla.resize(imagen.size, Image.Resampling.LANCZOS)
                imagen = Image.alpha_composite(imagen, plantilla)
            
            draw = ImageDraw.Draw(imagen)
            
            # Lista de posibles nombres y rutas de fuentes (Windows y Mac)
            font_names = [
                "arialbd.ttf",
                "Arial Bold.ttf",
                "Arial.ttf",
                "/Library/Fonts/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
            
            font = None
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, self.font_size)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            recuadros = self.recuadros.get(self.panaderia_seleccionada, {})
            
            def dibujar_texto_centrado(texto, recuadro):
                x, y, ancho, alto = recuadro
                bbox = draw.textbbox((0, 0), texto, font=font)
                texto_ancho = bbox[2] - bbox[0]
                texto_alto = bbox[3] - bbox[1]
                x_pos = x + (ancho - texto_ancho) // 2
                y_pos = y + (alto - texto_alto) // 2
                draw.text((x_pos, y_pos), texto, fill="black", font=font)
            
            dibujar_texto_centrado(fecha_lote_str, recuadros["lote"])
            dibujar_texto_centrado(fecha_vence_str, recuadros["vence"])
            
            return imagen.convert('RGB')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al añadir fechas: {str(e)}")
            return Image.open(ruta_imagen).convert('RGB')

    def actualizar_lista_con_fecha(self):
        self.lista_con_fecha.delete(0, tk.END)
        for etiqueta in self.etiquetas_con_fecha:
            self.lista_con_fecha.insert(tk.END, etiqueta['nombre'])

    def limpiar_etiquetas_fecha(self):
        if len(self.etiquetas_con_fecha) > 0:
            if messagebox.askyesno("Confirmar", "¿Estás seguro que deseas limpiar la lista de etiquetas con fecha?"):
                self.etiquetas_con_fecha = []
                self.actualizar_lista_con_fecha()
                PopupTemporizado(self.root, "Lista de etiquetas limpiada", 1500)
        else:
            messagebox.showinfo("Información", "La lista de etiquetas con fecha ya está vacía")

    def seleccionar_plantilla(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar plantilla de imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if archivo:
            self.plantilla_imagen = archivo
            self.plantilla_label.config(text=f"Plantilla: {os.path.basename(archivo)}")
            PopupTemporizado(self.root, "Plantilla cargada correctamente", 1500)

    def quitar_plantilla(self):
        self.plantilla_imagen = None
        self.plantilla_label.config(text="Ninguna plantilla seleccionada")
        PopupTemporizado(self.root, "Plantilla eliminada", 1500)

    def generar_pdf(self):
        if not self.etiquetas_con_fecha:
            messagebox.showerror("Error", "No hay etiquetas con fecha para generar")
            return
        
        output_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar PDF como",
            initialfile="etiquetas_pan.pdf"
        )
        
        if not output_pdf:
            return
        
        try:
            self.cols = int(self.entry_cols.get())
            self.rows = int(self.entry_rows.get())
            self.spacing = int(self.entry_spacing.get())
            
            self.status.config(text="Generando PDF...")
            self.progress["value"] = 0
            self.btn_generar.config(state=tk.DISABLED)
            self.root.update()
            
            points_per_inch = 72
            page_width = 11 * points_per_inch
            page_height = 8.5 * points_per_inch
            
            scaling_factor = self.dpi / points_per_inch
            page_width_px = int(page_width * scaling_factor)
            page_height_px = int(page_height * scaling_factor)
            spacing_px = int(self.spacing * scaling_factor)
            
            cell_width = (page_width_px - (spacing_px * (self.cols + 1))) // self.cols + 2
            cell_height = (page_height_px - (spacing_px * (self.rows + 1))) // self.rows + 2
            
            c = canvas.Canvas(output_pdf, pagesize=(page_width, page_height))
            c.setPageCompression(0)
            
            total = len(self.etiquetas_con_fecha)
            for i, etiqueta_info in enumerate(self.etiquetas_con_fecha):
                self.progress["value"] = (i + 1) / total * 100
                self.status.config(text=f"Procesando {i+1} de {total}...")
                self.root.update()
                
                imagen = etiqueta_info['imagen']
                page_img = Image.new('RGB', (page_width_px, page_height_px), 'white')
                
                for row in range(self.rows):
                    for col in range(self.cols):
                        x = spacing_px + col * (cell_width + spacing_px - 2)
                        y = spacing_px + row * (cell_height + spacing_px - 2)
                        
                        img_copy = imagen.copy()
                        img_copy.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
                        
                        paste_x = x + (cell_width - img_copy.width) // 2
                        paste_y = y + (cell_height - img_copy.height) // 2
                        page_img.paste(img_copy, (paste_x, paste_y))
                
                temp_img = f"temp_page_{i}.tiff"
                page_img.save(temp_img, format="TIFF", dpi=(self.dpi, self.dpi))
                
                c.drawImage(ImageReader(temp_img), 0, 0, width=page_width, height=page_height)
                c.showPage()
                os.remove(temp_img)
            
            c.save()
            PopupTemporizado(self.root, f"PDF generado con éxito:\n{os.path.basename(output_pdf)}", 3000)
            self.status.config(text=f"PDF generado con {total} etiqueta(s)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF:\n{str(e)}")
            self.status.config(text="Error al generar PDF")
        finally:
            self.progress["value"] = 0
            self.btn_generar.config(state=tk.NORMAL)

    def cargar_config(self):
        try:
            config_panaderia = f"config_{self.panaderia_seleccionada.lower()}.json" if self.panaderia_seleccionada else self.config_file
            if os.path.exists(config_panaderia):
                with open(config_panaderia, 'r') as f:
                    config = json.load(f)
                    self.plantilla_imagen = config.get('plantilla_imagen')
                    if hasattr(self, 'entry_font_size') and 'font_size' in config:
                        self.entry_font_size.delete(0, tk.END)
                        self.entry_font_size.insert(0, str(config['font_size']))
                    if hasattr(self, 'plantilla_label') and self.plantilla_imagen:
                        self.plantilla_label.config(text=f"Plantilla: {os.path.basename(self.plantilla_imagen)}")
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def guardar_config(self):
        try:
            config_panaderia = f"config_{self.panaderia_seleccionada.lower()}.json" if self.panaderia_seleccionada else self.config_file
            config = {
                'panaderia': self.panaderia_seleccionada,
                'plantilla_imagen': self.plantilla_imagen,
                'font_size': self.font_size
            }
            with open(config_panaderia, 'w') as f:
                json.dump(config, f, indent=2)
            PopupTemporizado(self.root, f"Configuración guardada para {self.panaderia_seleccionada}", 2000)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EtiquetasPanApp(root)
    root.mainloop()