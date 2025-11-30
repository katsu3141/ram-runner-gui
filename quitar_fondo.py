from PIL import Image, ImageSequence
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

def remove_background(input_gif, output_gif, bg_color=(255, 255, 255), tolerance=30, progress_callback=None):
    """
    Elimina el fondo de un GIF animado y lo hace transparente.
    
    Args:
        input_gif: Ruta del GIF de entrada
        output_gif: Ruta del GIF de salida
        bg_color: Color del fondo a eliminar (R, G, B)
        tolerance: Tolerancia para la detección del color (0-255)
        progress_callback: Función para actualizar el progreso
    """
    img = Image.open(input_gif)
    
    frames = []
    durations = []
    
    total_frames = getattr(img, 'n_frames', 1)
    
    for idx, frame in enumerate(ImageSequence.Iterator(img)):
        if progress_callback:
            progress_callback(idx + 1, total_frames)
        
        frame = frame.convert('RGBA')
        data = np.array(frame)
        
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        mask = (
            (np.abs(r - bg_color[0]) <= tolerance) &
            (np.abs(g - bg_color[1]) <= tolerance) &
            (np.abs(b - bg_color[2]) <= tolerance)
        )
        
        data[:,:,3] = np.where(mask, 0, 255)
        
        new_frame = Image.fromarray(data, 'RGBA')
        frames.append(new_frame)
        durations.append(frame.info.get('duration', 100))
    
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=img.info.get('loop', 0),
        disposal=2,
        transparency=0,
        optimize=False
    )

class GifBackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eliminar Fondo de GIF")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        
        self.input_file = ""
        self.output_file = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title = ttk.Label(main_frame, text="🎬 Eliminar Fondo de GIF", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Seleccionar archivo de entrada
        ttk.Label(main_frame, text="Archivo GIF:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_label = ttk.Label(main_frame, text="No seleccionado", foreground="gray")
        self.input_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        btn_input = ttk.Button(main_frame, text="Seleccionar GIF", command=self.select_input)
        btn_input.grid(row=2, column=2, pady=(0, 10))
        
        # Color de fondo
        ttk.Label(main_frame, text="Color de fondo a eliminar:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        self.color_var = tk.StringVar(value="white")
        ttk.Radiobutton(color_frame, text="Blanco", variable=self.color_var, value="white").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="Verde", variable=self.color_var, value="green").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="Negro", variable=self.color_var, value="black").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="Personalizado", variable=self.color_var, value="custom").pack(side=tk.LEFT, padx=5)
        
        # Color personalizado
        custom_frame = ttk.Frame(main_frame)
        custom_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(custom_frame, text="RGB personalizado:").pack(side=tk.LEFT)
        self.r_var = tk.StringVar(value="255")
        self.g_var = tk.StringVar(value="255")
        self.b_var = tk.StringVar(value="255")
        
        ttk.Label(custom_frame, text="R:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(custom_frame, textvariable=self.r_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(custom_frame, text="G:").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Entry(custom_frame, textvariable=self.g_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(custom_frame, text="B:").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Entry(custom_frame, textvariable=self.b_var, width=5).pack(side=tk.LEFT, padx=2)
        
        # Tolerancia
        ttk.Label(main_frame, text="Tolerancia (0-100):", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        tolerance_frame = ttk.Frame(main_frame)
        tolerance_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.tolerance_var = tk.IntVar(value=30)
        self.tolerance_scale = ttk.Scale(tolerance_frame, from_=0, to=100, variable=self.tolerance_var, orient=tk.HORIZONTAL)
        self.tolerance_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.tolerance_label = ttk.Label(tolerance_frame, text="30")
        self.tolerance_label.pack(side=tk.LEFT)
        
        self.tolerance_var.trace('w', self.update_tolerance_label)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=3, pady=15, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(main_frame, text="", foreground="blue")
        self.progress_label.grid(row=9, column=0, columnspan=3)
        
        # Botón procesar
        self.btn_process = ttk.Button(main_frame, text="🚀 Procesar GIF", command=self.process_gif, state=tk.DISABLED)
        self.btn_process.grid(row=10, column=0, columnspan=3, pady=20)
    
    def update_tolerance_label(self, *args):
        self.tolerance_label.config(text=str(self.tolerance_var.get()))
    
    def select_input(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar GIF",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.input_file = filename
            self.input_label.config(text=os.path.basename(filename), foreground="black")
            
            # Sugerir nombre de salida
            base = os.path.splitext(filename)[0]
            self.output_file = f"{base}_sin_fondo.gif"
            
            self.btn_process.config(state=tk.NORMAL)
    
    def get_bg_color(self):
        color_choice = self.color_var.get()
        
        if color_choice == "white":
            return (255, 255, 255)
        elif color_choice == "green":
            return (0, 255, 0)
        elif color_choice == "black":
            return (0, 0, 0)
        else:  # custom
            try:
                r = int(self.r_var.get())
                g = int(self.g_var.get())
                b = int(self.b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValueError
                
                return (r, g, b)
            except:
                messagebox.showerror("Error", "Los valores RGB deben ser números entre 0 y 255")
                return None
    
    def update_progress(self, current, total):
        progress_percent = (current / total) * 100
        self.progress['value'] = progress_percent
        self.progress_label.config(text=f"Procesando frame {current} de {total}...")
        self.root.update_idletasks()
    
    def process_gif(self):
        if not self.input_file:
            messagebox.showerror("Error", "Por favor selecciona un archivo GIF")
            return
        
        bg_color = self.get_bg_color()
        if bg_color is None:
            return
        
        tolerance = self.tolerance_var.get()
        
        # Preguntar dónde guardar
        output_file = filedialog.asksaveasfilename(
            title="Guardar GIF como",
            defaultextension=".gif",
            initialfile=os.path.basename(self.output_file),
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        try:
            self.btn_process.config(state=tk.DISABLED)
            self.progress['value'] = 0
            self.progress_label.config(text="Iniciando...")
            
            remove_background(
                self.input_file,
                output_file,
                bg_color=bg_color,
                tolerance=tolerance,
                progress_callback=self.update_progress
            )
            
            self.progress['value'] = 100
            self.progress_label.config(text="¡Completado!", foreground="green")
            
            messagebox.showinfo("Éxito", f"GIF guardado exitosamente en:\n{output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el GIF:\n{str(e)}")
            self.progress_label.config(text="Error en el proceso", foreground="red")
        
        finally:
            self.btn_process.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = GifBackgroundRemoverApp(root)
    root.mainloop()