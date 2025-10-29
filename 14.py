import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, Frame, messagebox
import csv
import random
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk, ImageDraw
import os

# --- Configuración Base de Datos ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root',
    'database': 'empleados_db'
}

# Rutas a los recursos provistos en el contenedor
FONDO_PATH = "fondo.png"      # imagen de fondo provista
GIF_SALUDO_PATH = "saludo.gif"  # gif de saludo provisto

class EmployeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Empleados v2.0 - Ejercicio 14")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        # --- IMAGEN DE FONDO ---
        try:
            self.bg_image = Image.open(FONDO_PATH)
            self.bg_image = self.bg_image.resize((900, 650), Image.LANCZOS)
            
            # Crear una versión semitransparente para los frames
            self.bg_overlay = self.bg_image.copy()
            overlay = Image.new('RGBA', self.bg_overlay.size, (0, 0, 0, 180))  # Oscurecer fondo
            self.bg_overlay = Image.alpha_composite(self.bg_overlay.convert('RGBA'), overlay)
            
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_overlay_photo = ImageTk.PhotoImage(self.bg_overlay)
            
            self.bg_label = Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error al cargar fondo ({FONDO_PATH}): {e}")
            self.root.config(bg="#2C3E50")

        # --- CONTENEDOR PRINCIPAL con fondo semitransparente ---
        self.main_frame = Frame(self.root, bg="#2C3E50", bd=3, relief="ridge")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=800, height=550)

        # Crear un canvas para el fondo semitransparente del main frame
        self.main_canvas = tk.Canvas(self.main_frame, width=800, height=550, highlightthickness=0)
        self.main_canvas.place(x=0, y=0)
        self.main_canvas.create_image(0, 0, image=self.bg_overlay_photo, anchor="nw")

        title_label = Label(self.main_frame, text="Sistema de Gestión de Empleados",
                            font=("Fixedsys", 20, "bold"), bg="#2C3E50", fg="white",
                            bd=0, highlightthickness=0)
        title_label.place(relx=0.5, y=20, anchor=tk.CENTER)

        # --- FORMULARIO ---
        form_frame = Frame(self.main_frame, bg="#2C3E50", bd=0, highlightthickness=0)
        form_frame.place(relx=0.5, y=100, anchor=tk.CENTER, width=700, height=200)

        fields = [("Nombre:", "nombre"),
                  ("Apellido:", "apellido"),
                  ("Cargo:", "cargo"),
                  ("Departamento:", "departamento")]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            # Frame para cada campo
            field_frame = Frame(form_frame, bg="#2C3E50", bd=0, highlightthickness=0)
            field_frame.pack(fill=tk.X, pady=8)

            # Label
            label = Label(field_frame, text=label_text, font=("Consolas", 12, "bold"),
                         bg="#2C3E50", fg="white", width=15, anchor="e",
                         bd=0, highlightthickness=0)
            label.pack(side=tk.LEFT, padx=(0, 10))

            # Entry con estilo mejorado
            entry = Entry(field_frame, font=("Consolas", 11), bg="white",
                         relief="solid", bd=2, width=30, highlightthickness=1,
                         highlightcolor="#3498DB", highlightbackground="#34495E")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field_name] = entry

        # --- BOTONES Y AREA DEL GIF ---
        buttons_container = Frame(self.main_frame, bg="#2C3E50", bd=0, highlightthickness=0)
        buttons_container.place(relx=0.5, y=380, anchor=tk.CENTER, width=750, height=200)

        # Frame izquierdo para botones
        self.left_buttons_frame = Frame(buttons_container, bg="#2C3E50", bd=0, highlightthickness=0)
        self.left_buttons_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Configurar grid para el frame izquierdo
        self.left_buttons_frame.columnconfigure(0, weight=1)
        self.left_buttons_frame.columnconfigure(1, weight=1)

        # Frame derecho para GIF
        self.gif_frame = Frame(buttons_container, bg="#2C3E50", bd=2, relief="sunken",
                              width=300, height=180)
        self.gif_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        self.gif_frame.pack_propagate(False)

        # Botones en el frame izquierdo
        self.btn_guardar = Button(self.left_buttons_frame, text="Guardar Empleado",
                                 font=("Fixedsys", 12, "bold"),
                                 command=self.guardar_empleado)
        self.estilo_boton_pixel(self.btn_guardar, "#27AE60", "#2ECC71")
        self.btn_guardar.grid(row=0, column=0, padx=10, pady=8, sticky="ew")

        self.btn_hackear = Button(self.left_buttons_frame,
                                 text="Hackear Ilegalmente la Base de Datos",
                                 font=("Fixedsys", 10, "bold"),
                                 command=self.hackear_base_datos)
        self.estilo_boton_pixel(self.btn_hackear, "#C0392B", "#E74C3C")
        self.btn_hackear.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        self.btn_mensaje = Button(self.left_buttons_frame,
                                 text="Click aquí para mensaje interesante",
                                 font=("Fixedsys", 10, "bold"),
                                 command=self.toggle_gif_display)
        self.estilo_boton_pixel(self.btn_mensaje, "#2980B9", "#3498DB")
        self.btn_mensaje.grid(row=1, column=0, columnspan=2, padx=10, pady=8, sticky="ew")

        # Botón Cerrar especial que se mueve - inicialmente en una posición aleatoria
        self.btn_cerrar = Button(self.left_buttons_frame,
                                text="Cerrar",
                                font=("Fixedsys", 12, "bold"),
                                command=self.root.destroy)
        self.estilo_boton_pixel(self.btn_cerrar, "#F39C12", "#F1C40F")
        
        # Posición inicial aleatoria del botón cerrar
        self.mover_boton_cerrar_aleatorio()

        # Variables para animación del GIF
        self.gif_frames = []
        self.gif_label = None
        self.gif_anim_id = None
        self.gif_playing = False
        self.current_gif_frame = 0

        # precargar frames del gif para respuesta ágil (si existe)
        self._preload_gif_frames()

        # Seguimiento del mouse para el botón cerrar (se mueve aleatoriamente)
        self.root.bind("<Motion>", self.evitar_cierre)
        
        # Timer para movimiento automático adicional del botón cerrar
        self.auto_move_id = None
        self.iniciar_movimiento_automatico()

    def iniciar_movimiento_automatico(self):
        """Inicia el movimiento automático periódico del botón cerrar"""
        self.mover_automaticamente()

    def mover_automaticamente(self):
        """Mueve el botón automáticamente cada cierto tiempo"""
        if random.random() < 0.3:  # 30% de probabilidad de moverse
            self.mover_boton_cerrar_aleatorio()
        
        # Programar próximo movimiento automático
        self.auto_move_id = self.root.after(2000, self.mover_automaticamente)  # Cada 2 segundos

    def mover_boton_cerrar_aleatorio(self):
        """Mueve el botón cerrar a una posición aleatoria dentro del frame"""
        try:
            parent = self.left_buttons_frame
            btn_width = 120  # Ancho aproximado del botón
            btn_height = 45  # Alto aproximado del botón
            
            max_x = parent.winfo_width() - btn_width - 10
            max_y = parent.winfo_height() - btn_height - 10
            
            if max_x > 0 and max_y > 0:
                new_x = random.randint(5, max_x)
                new_y = random.randint(5, max_y)
                self.btn_cerrar.place(x=new_x, y=new_y)
            else:
                # Fallback si no se pueden obtener las dimensiones
                self.btn_cerrar.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        except:
            # Fallback a grid si hay error
            self.btn_cerrar.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

    def estilo_boton_pixel(self, boton, color_normal, color_hover):
        """Aplica estilo pixel art con hover"""
        boton.config(
            bg=color_normal,
            fg="white",
            padx=20,
            pady=12,
            relief="raised",
            borderwidth=4,
            cursor="hand2",
            activebackground=color_hover,
            activeforeground="white"
        )
        boton.config(highlightbackground=color_normal, highlightcolor=color_normal)
        
        # Mejorar el efecto hover
        def on_enter(e):
            boton.config(bg=color_hover, relief="sunken")
        def on_leave(e):
            boton.config(bg=color_normal, relief="raised")
            
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)

    def evitar_cierre(self, event):
        """Hace que el botón Cerrar se mueva cuando el mouse se acerca"""
        try:
            # Solo procesar si el evento es del root o del main_frame
            if event.widget in [self.root, self.main_frame, self.left_buttons_frame]:
                btn_x = self.btn_cerrar.winfo_rootx()
                btn_y = self.btn_cerrar.winfo_rooty()
                btn_width = self.btn_cerrar.winfo_width()
                btn_height = self.btn_cerrar.winfo_height()

                btn_center_x = btn_x + btn_width / 2
                btn_center_y = btn_y + btn_height / 2

                mouse_x = event.x_root
                mouse_y = event.y_root

                distancia = ((mouse_x - btn_center_x) ** 2 + (mouse_y - btn_center_y) ** 2) ** 0.5

                # Si el mouse está muy cerca (80 pixels), mover el botón
                if distancia < 80:
                    self.mover_boton_cerrar_aleatorio()
                    
        except Exception as e:
            # Silenciar errores para no interrumpir la experiencia
            pass

    # --- FUNCIONES DB ---
    def connect_db(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None

    def guardar_empleado(self):
        nombre = self.entries["nombre"].get().strip()
        apellido = self.entries["apellido"].get().strip()
        cargo = self.entries["cargo"].get().strip()
        departamento = self.entries["departamento"].get().strip()

        if not all([nombre, apellido, cargo, departamento]):
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        conn = self.connect_db()
        if not conn:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return

        try:
            cursor = conn.cursor()
            query = "INSERT INTO empleados (nombre, apellido, cargo, departamento) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, apellido, cargo, departamento))
            conn.commit()

            messagebox.showinfo("Éxito", f"Empleado {nombre} {apellido} guardado correctamente")

            # Limpiar campos
            for entry in self.entries.values():
                entry.delete(0, tk.END)

        except Error as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
        finally:
            try:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
            except Exception:
                pass

    def hackear_base_datos(self):
        """Exporta todos los registros a CSV"""
        conn = self.connect_db()
        if not conn:
            messagebox.showerror("Error", "Fallo en la conexión de 'hackeo'")
            return

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, nombre, apellido, cargo, departamento FROM empleados"
            cursor.execute(query)
            registros = cursor.fetchall()

            if not registros:
                messagebox.showinfo("Hackeo", "La base de datos está vacía")
                return

            with open("registros_hackeados.csv", "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=registros[0].keys())
                escritor.writeheader()
                escritor.writerows(registros)

            messagebox.showinfo("¡Hackeo Exitoso!",
                               "Todos los registros fueron exportados a 'registros_hackeados.csv'")

        except Error as e:
            messagebox.showerror("Error", f"Fallo en el 'hackeo': {e}")
        finally:
            try:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
            except Exception:
                pass

    # --- GIF MEJORADO ---
    def _preload_gif_frames(self):
        """Carga los frames del GIF en memoria para animar rápido cuando se pida"""
        self.gif_frames = []
        if not os.path.exists(GIF_SALUDO_PATH):
            print(f"GIF no encontrado en: {GIF_SALUDO_PATH}")
            return
            
        try:
            gif = Image.open(GIF_SALUDO_PATH)
            frame_count = 0
            
            try:
                while True:
                    # Convertir a RGBA para mejor calidad
                    frame = gif.convert('RGBA')
                    
                    # Redimensionar manteniendo aspecto
                    original_width, original_height = frame.size
                    target_width = 280
                    target_height = 160
                    
                    # Calcular nuevo tamaño manteniendo proporción
                    ratio = min(target_width / original_width, target_height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    
                    # Redimensionar con alta calidad
                    frame = frame.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Crear fondo transparente del tamaño objetivo
                    background = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
                    
                    # Centrar el frame en el fondo
                    x_offset = (target_width - new_width) // 2
                    y_offset = (target_height - new_height) // 2
                    background.paste(frame, (x_offset, y_offset), frame)
                    
                    photo_frame = ImageTk.PhotoImage(background)
                    self.gif_frames.append(photo_frame)
                    frame_count += 1
                    
                    gif.seek(gif.tell() + 1)
                    
            except EOFError:
                pass
                
            print(f"GIF cargado: {frame_count} frames")
            
        except Exception as e:
            print(f"Error precargando GIF: {e}")
            self.gif_frames = []

    def toggle_gif_display(self):
        """Muestra u oculta el GIF dentro de self.gif_frame"""
        if self.gif_playing:
            self._stop_gif()
            self.btn_mensaje.config(text="Click aquí para mensaje interesante")
        else:
            self._show_gif()
            self.btn_mensaje.config(text="Ocultar mensaje")

    def _show_gif(self):
        """Crear la etiqueta y comenzar la animación"""
        # Limpiar contenedor previo
        for widget in self.gif_frame.winfo_children():
            widget.destroy()

        if not self.gif_frames:
            # fallback: mostrar mensaje de error
            error_label = Label(self.gif_frame, 
                               text="GIF no disponible\n(saludo.gif no encontrado)",
                               font=("Consolas", 10), bg="#2C3E50", fg="white",
                               justify=tk.CENTER)
            error_label.pack(expand=True)
            self.gif_label = error_label
            self.gif_playing = True
            return

        self.gif_label = Label(self.gif_frame, bg="black", bd=0)
        self.gif_label.pack(expand=True, fill="both")
        self.gif_playing = True
        self.current_gif_frame = 0
        # iniciar animación
        self._animate_gif()

    def _animate_gif(self):
        if not self.gif_playing or not self.gif_label:
            return
            
        if self.current_gif_frame >= len(self.gif_frames):
            self.current_gif_frame = 0
            
        frame = self.gif_frames[self.current_gif_frame]
        self.gif_label.config(image=frame)
        self.current_gif_frame += 1
        
        # Programar siguiente frame (velocidad ajustable)
        self.gif_anim_id = self.root.after(50, self._animate_gif)  # 20 FPS

    def _stop_gif(self):
        """Detener animación y eliminar la etiqueta"""
        self.gif_playing = False
        
        if self.gif_anim_id:
            self.root.after_cancel(self.gif_anim_id)
            self.gif_anim_id = None
            
        if self.gif_label:
            self.gif_label.destroy()
            self.gif_label = None
            
        # Limpiar el frame del GIF
        for widget in self.gif_frame.winfo_children():
            widget.destroy()

    def __del__(self):
        """Limpiar timers al destruir la aplicación"""
        if self.auto_move_id:
            self.root.after_cancel(self.auto_move_id)
        if self.gif_anim_id:
            self.root.after_cancel(self.gif_anim_id)

# --- INICIALIZACIÓN ---
if __name__ == "__main__":
    # Crear directorio si no existe
    os.makedirs("media", exist_ok=True)

    root = tk.Tk()
    app = EmployeeApp(root)
    
    try:
        root.mainloop()
    finally:
        # Limpieza final
        if hasattr(app, 'auto_move_id') and app.auto_move_id:
            root.after_cancel(app.auto_move_id)
        if hasattr(app, 'gif_anim_id') and app.gif_anim_id:
            root.after_cancel(app.gif_anim_id)