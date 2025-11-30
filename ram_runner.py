import sys
import psutil
import winreg
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, 
                              QSystemTrayIcon, QMenu, QAction, QActionGroup)
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect, QFileSystemWatcher
from PyQt5.QtGui import QPixmap, QMovie, QColor, QFont, QPainter, QBrush, QIcon, QPainter as QPainterAlias

class RAMRunnerWidget(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        
        # --- Configuración de la ventana ---
        # IMPORTANTE: Estas banderas hacen que la ventana esté SIEMPRE encima
        self.setWindowFlags(
            Qt.FramelessWindowHint |           # Sin bordes de ventana
            Qt.WindowStaysOnTopHint |          # Siempre encima de otras ventanas
            Qt.Tool |                          # No aparece en taskbar
            Qt.WindowStaysOnTopHint |          # Duplicado para forzar prioridad
            Qt.X11BypassWindowManagerHint      # Bypass para máxima prioridad (Windows ignora esto pero no hace daño)
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # Fondo transparente
        
        # Forzar que la ventana siempre esté en el nivel más alto
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        
        # --- Variables de control ---
        self.dragging = False
        self.resizing = False
        self.drag_position = QPoint()
        self.current_width = 320
        self.current_height = 293
        self.resize_handle_size = 15
        
        # --- Parámetros de velocidad (ajustados para mejor percepción) ---
        self.MAX_INTERVAL_MS = 300  # Velocidad base más rápida
        self.MIN_INTERVAL_MS = 30   # Velocidad máxima más controlada
        
        # --- Variables para efecto RGB ---
        self.rgb_hue = 0
        
        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # --- Label para el GIF ---
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setScaledContents(True)
        
        # --- Cargar GIF inicial ---
        self.movie = None
        self.current_gif_path = None
        
        # --- Label para el texto de RAM ---
        self.ram_label = QLabel("RAM: 0.0%", self)
        self.ram_label.setAlignment(Qt.AlignCenter)
        self.ram_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.ram_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #FF0000;
                padding: 5px;
            }
        """)
        
        # --- Agregar widgets al layout ---
        layout.addWidget(self.gif_label)
        layout.addWidget(self.ram_label)
        
        self.setLayout(layout)
        
        # --- Timer para actualizar RAM ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ram_display)
        self.update_timer.start(100)
        
        # --- Timer para efecto RGB ---
        self.rgb_timer = QTimer(self)
        self.rgb_timer.timeout.connect(self.update_rgb_color)
        self.rgb_timer.start(50)
        
        # --- Timer para mantener la ventana siempre encima ---
        # Este timer refresca constantemente la prioridad de la ventana
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self.force_on_top)
        self.top_timer.start(1000)  # Cada segundo reafirma que está encima
        
        # --- Configuración inicial ---
        self.update_size()
        self.move(100, 100)
        
        print("=== RAM Runner GUI - Mejorado ===")
        print("Instrucciones:")
        print("  • Arrastra la ventana con el mouse")
        print("  • Punto rojo (esquina): Redimensionar")
        print("  • Clic derecho en widget: Cerrar widget")
        print("  • Busca el icono en la bandeja del sistema")
        print("=" * 40)
    
    def load_gif(self, gif_path):
        """Carga un GIF específico."""
        if self.movie:
            self.movie.stop()
        
        gif_path = Path(gif_path)
        
        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.gif_label.setMovie(self.movie)
            self.movie.start()
            self.current_gif_path = str(gif_path)
            print(f"✓ GIF cargado: {gif_path.name}")
        else:
            self.gif_label.setText("🦜")
            self.gif_label.setStyleSheet("""
                QLabel {
                    font-size: 72px;
                    background-color: rgba(50, 50, 50, 200);
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            self.movie = None
            print(f"⚠️  GIF no encontrado: {gif_path}")
    
    def update_size(self):
        """Actualiza el tamaño de la ventana y los widgets."""
        total_height = self.current_height + 40
        self.setFixedSize(self.current_width, total_height)
        self.gif_label.setFixedSize(self.current_width, self.current_height)
    
    def update_rgb_color(self):
        """Actualiza el color RGB del texto (efecto arcoíris)."""
        self.rgb_hue += 2
        if self.rgb_hue >= 360:
            self.rgb_hue = 0
        
        color = QColor.fromHsv(self.rgb_hue, 255, 255)
        rgb_string = f"rgb({color.red()}, {color.green()}, {color.blue()})"
        
        self.ram_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {rgb_string};
                padding: 5px;
            }}
        """)
    
    def update_ram_display(self):
        """Actualiza el display de RAM y ajusta la velocidad del GIF."""
        ram_percent = psutil.virtual_memory().percent
        
        self.ram_label.setText(f"RAM: {ram_percent:.1f}%")
        
        # ====================================================================
        # AJUSTE DE VELOCIDAD DEL GIF SEGÚN USO DE RAM
        # ====================================================================
        # Aquí puedes modificar cómo se comporta la velocidad del GIF
        # según el porcentaje de RAM usado.
        #
        # Parámetros actuales:
        # - self.MAX_INTERVAL_MS = 300  (velocidad cuando RAM está en 0%)
        # - self.MIN_INTERVAL_MS = 30   (velocidad cuando RAM está en 100%)
        #
        # Puedes cambiar estos valores en __init__ para ajustar:
        # - Valores MÁS ALTOS = GIF más lento
        # - Valores MÁS BAJOS = GIF más rápido
        #
        # Ejemplos de ajuste:
        # self.MAX_INTERVAL_MS = 500  # GIF muy lento con poca RAM
        # self.MAX_INTERVAL_MS = 200  # GIF más rápido con poca RAM
        # self.MIN_INTERVAL_MS = 50   # Velocidad máxima más controlada
        # self.MIN_INTERVAL_MS = 20   # Velocidad máxima muy rápida
        # ====================================================================
        
        if self.movie:
            interval_ms = self.calculate_animation_interval(ram_percent)
            self.movie.setSpeed(int((self.MAX_INTERVAL_MS / interval_ms) * 100))
    
    def calculate_animation_interval(self, ram_percent):
        """
        Calcula el intervalo de animación basado en el uso de RAM.
        
        Parámetros para ajustar el comportamiento:
        ---------------------------------------
        ram_percent: Porcentaje de RAM usado (0-100)
        
        Comportamiento actual:
        - 0-50% RAM: Velocidad normal (cambio gradual)
        - 50-70% RAM: Velocidad moderada
        - 70-100% RAM: Acelera notablemente (curva cuadrática)
        
        AJUSTES POSIBLES:
        -----------------
        1. Para hacer que 50-70% sea más lento:
           curved_percent = normalized_percent ** 1.5
        
        2. Para hacer que acelere más suave en todo el rango:
           curved_percent = normalized_percent ** 1
           (esto elimina la curva, aceleración lineal)
        
        3. Para que acelere solo después del 80%:
           if normalized_percent < 0.8:
               curved_percent = normalized_percent * 0.5
           else:
               curved_percent = ((normalized_percent - 0.8) / 0.2) ** 2
        
        4. Para que sea siempre rápido y solo se note al 90%+:
           curved_percent = normalized_percent ** 3
        """
        normalized_percent = ram_percent / 100.0
        
        # Curva cuadrática: acelera más notablemente después del 70%
        curved_percent = normalized_percent ** 2
        
        # Si quieres probar diferentes curvas, comenta la línea de arriba
        # y descomenta una de estas:
        
        # curved_percent = normalized_percent ** 1.5  # Aceleración moderada
        # curved_percent = normalized_percent ** 1    # Aceleración lineal
        # curved_percent = normalized_percent ** 3    # Aceleración muy marcada al final
        
        interval_ms = (self.MAX_INTERVAL_MS - self.MIN_INTERVAL_MS) * (1.0 - curved_percent) + self.MIN_INTERVAL_MS
        return interval_ms
    
    def force_on_top(self):
        """Fuerza a que la ventana esté siempre encima de todo."""
        if self.isVisible():
            self.raise_()
            self.activateWindow()
    
    def get_resize_handle_rect(self):
        """Retorna el rectángulo del punto rojo de redimensionamiento."""
        return QRect(
            self.width() - self.resize_handle_size,
            self.height() - self.resize_handle_size,
            self.resize_handle_size,
            self.resize_handle_size
        )
    
    def paintEvent(self, event):
        """Dibuja el punto rojo en la esquina inferior derecha."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QBrush(QColor(255, 0, 0, 200)))
        painter.setPen(Qt.NoPen)
        
        handle_rect = self.get_resize_handle_rect()
        painter.drawEllipse(handle_rect)
    
    # --- Eventos del mouse ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle_rect = self.get_resize_handle_rect()
            
            if handle_rect.contains(event.pos()):
                self.resizing = True
                self.drag_position = event.globalPos()
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            # Clic derecho muestra el menú del tray
            if self.parent_app and self.parent_app.tray_icon:
                menu = self.parent_app.tray_icon.contextMenu()
                if menu:
                    menu.exec_(event.globalPos())
    
    def mouseMoveEvent(self, event):
        if self.resizing and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.drag_position
            
            new_width = max(100, self.current_width + delta.x())
            new_height = max(100, self.current_height + delta.y())
            
            aspect_ratio = 320.0 / 293.0
            new_height = int(new_width / aspect_ratio)
            
            self.current_width = new_width
            self.current_height = new_height
            
            self.update_size()
            self.drag_position = event.globalPos()
            event.accept()
            
        elif self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False


class RAMRunnerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # --- Widget principal ---
        self.widget = RAMRunnerWidget(self)
        
        # --- Vigilar carpeta assets para cambios ---
        self.setup_file_watcher()
        
        # --- System Tray Icon ---
        self.tray_icon = None
        self.create_tray_icon()
        
        # --- Cargar primer GIF disponible ---
        gifs = self.get_available_gifs()
        if gifs:
            self.widget.load_gif(gifs[0])
        
        self.widget.show()
    
    def setup_file_watcher(self):
        """Configura el vigilante de archivos para detectar nuevos GIFs."""
        assets_path = Path("assets")
        if not assets_path.exists():
            assets_path.mkdir(parents=True, exist_ok=True)
        
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(str(assets_path.resolve()))
        self.file_watcher.directoryChanged.connect(self.on_assets_changed)
    
    def on_assets_changed(self, path):
        """Se ejecuta cuando cambia el contenido de la carpeta assets."""
        print(f"🔄 Detectado cambio en carpeta assets")
        # Esperar un poco para que el archivo termine de copiarse
        QTimer.singleShot(500, self.refresh_gif_menu)
    
    def create_icon(self):
        """Crea un icono simple para el tray."""
        # Crear un pixmap de 32x32 con un círculo de color
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dibujar un círculo azul con borde blanco
        painter.setBrush(QBrush(QColor(0, 120, 215)))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(2, 2, 28, 28)
        
        # Dibujar texto "RAM"
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "RAM")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_tray_icon(self):
        """Crea el icono de bandeja del sistema con menú."""
        # Verificar si el sistema soporta tray icons
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("❌ ERROR: El sistema no soporta iconos de bandeja del sistema")
            print("   No se mostrará el menú de configuración")
            return
        
        # Crear icono de bandeja
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Usar icono personalizado
        icon = self.create_icon()
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("RAM Runner - Clic derecho para opciones")
        
        # Crear menú principal
        menu = QMenu()
        
        # --- RUNNER (Submenú para seleccionar GIF) ---
        runner_menu = menu.addMenu("Runner")
        self.gif_action_group = QActionGroup(runner_menu)
        self.gif_action_group.setExclusive(True)
        
        gifs = self.get_available_gifs()
        if gifs:
            for gif_path in gifs:
                gif_name = Path(gif_path).stem.capitalize()
                action = QAction(gif_name, runner_menu)
                action.setCheckable(True)
                action.setData(gif_path)
                action.triggered.connect(lambda checked, path=gif_path: self.change_gif(path))
                self.gif_action_group.addAction(action)
                runner_menu.addAction(action)
            
            # Marcar el primero como seleccionado
            self.gif_action_group.actions()[0].setChecked(True)
        else:
            no_gif_action = QAction("(Sin GIFs disponibles)", runner_menu)
            no_gif_action.setEnabled(False)
            runner_menu.addAction(no_gif_action)
        
        # Separador y opción para abrir carpeta
        runner_menu.addSeparator()
        open_folder_action = QAction("📁 Abrir carpeta de GIFs", runner_menu)
        open_folder_action.triggered.connect(self.open_assets_folder)
        runner_menu.addAction(open_folder_action)
        
        # --- STARTUP (Iniciar con Windows) ---
        self.autostart_action = QAction("Startup", menu)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(self.is_autostart_enabled())
        self.autostart_action.triggered.connect(self.toggle_autostart)
        menu.addAction(self.autostart_action)
        
        menu.addSeparator()
        
        # --- Versión (info) ---
        version_action = QAction("RAM Runner v1.0", menu)
        version_action.setEnabled(False)
        menu.addAction(version_action)
        
        # --- EXIT ---
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        
        # Conectar señales
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # MOSTRAR el icono
        self.tray_icon.show()
        
        print("✓ Icono de bandeja creado y mostrado")
        print("  Busca el icono en la bandeja del sistema (área de notificaciones)")
        print("  Haz clic derecho en el icono para ver las opciones")
    
    def on_tray_icon_activated(self, reason):
        """Maneja los clics en el icono de la bandeja."""
        if reason == QSystemTrayIcon.Trigger:  # Clic izquierdo
            # Mostrar/ocultar el widget
            if self.widget.isVisible():
                self.widget.hide()
            else:
                self.widget.show()
                self.widget.raise_()
                self.widget.activateWindow()
    
    def get_available_gifs(self):
        """Obtiene la lista de GIFs disponibles en la carpeta assets."""
        assets_path = Path("assets")
        if not assets_path.exists():
            assets_path.mkdir(parents=True, exist_ok=True)
            return []
        
        gifs = list(assets_path.glob("*.gif"))
        return sorted([str(gif) for gif in gifs])
    
    def change_gif(self, gif_path):
        """Cambia el GIF que se está mostrando."""
        self.widget.load_gif(gif_path)
        
        # Actualizar el check en el menú
        for action in self.gif_action_group.actions():
            if action.data() == gif_path:
                action.setChecked(True)
                break
    
    def open_assets_folder(self):
        """Abre la carpeta assets en el explorador de archivos."""
        assets_path = Path("assets").resolve()
        if not assets_path.exists():
            assets_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Abrir en el explorador de Windows
            subprocess.Popen(f'explorer "{assets_path}"')
            print(f"📁 Abriendo carpeta: {assets_path}")
        except Exception as e:
            print(f"❌ Error al abrir carpeta: {e}")
    
    def refresh_gif_menu(self):
        """Actualiza el menú de GIFs cuando se detectan cambios."""
        if not self.tray_icon or not self.tray_icon.contextMenu():
            return
        
        menu = self.tray_icon.contextMenu()
        
        # Buscar el submenú Runner
        for action in menu.actions():
            if action.text() == "Runner" and action.menu():
                runner_menu = action.menu()
                
                # Limpiar solo las acciones de GIFs (no la opción de abrir carpeta)
                actions_to_remove = []
                open_folder_action = None
                
                for sub_action in runner_menu.actions():
                    if "Abrir carpeta" in sub_action.text():
                        open_folder_action = sub_action
                    elif not sub_action.isSeparator():
                        actions_to_remove.append(sub_action)
                
                # Remover acciones antiguas
                for sub_action in actions_to_remove:
                    runner_menu.removeAction(sub_action)
                
                # Limpiar separadores
                for sub_action in runner_menu.actions():
                    if sub_action.isSeparator():
                        runner_menu.removeAction(sub_action)
                
                # Remover temporalmente la acción de abrir carpeta
                if open_folder_action:
                    runner_menu.removeAction(open_folder_action)
                
                # Recrear lista de GIFs
                self.gif_action_group = QActionGroup(runner_menu)
                self.gif_action_group.setExclusive(True)
                
                gifs = self.get_available_gifs()
                if gifs:
                    for gif_path in gifs:
                        gif_name = Path(gif_path).stem.capitalize()
                        new_action = QAction(gif_name, runner_menu)
                        new_action.setCheckable(True)
                        new_action.setData(gif_path)
                        new_action.triggered.connect(lambda checked, path=gif_path: self.change_gif(path))
                        self.gif_action_group.addAction(new_action)
                        runner_menu.addAction(new_action)
                    
                    # Marcar el GIF actualmente activo
                    if self.widget.current_gif_path:
                        for new_action in self.gif_action_group.actions():
                            if new_action.data() == self.widget.current_gif_path:
                                new_action.setChecked(True)
                                break
                    else:
                        # Si no hay ninguno activo, marcar el primero
                        self.gif_action_group.actions()[0].setChecked(True)
                else:
                    no_gif_action = QAction("(Sin GIFs disponibles)", runner_menu)
                    no_gif_action.setEnabled(False)
                    runner_menu.addAction(no_gif_action)
                
                # Agregar separador y opción de abrir carpeta
                runner_menu.addSeparator()
                if open_folder_action:
                    runner_menu.addAction(open_folder_action)
                
                print(f"✓ Menú actualizado: {len(gifs)} GIF(s) encontrado(s)")
                break
    
    def toggle_autostart(self, checked):
        """Activa o desactiva el inicio automático con Windows."""
        if checked:
            self.enable_autostart()
        else:
            self.disable_autostart()
    
    def is_autostart_enabled(self):
        """Verifica si el inicio automático está habilitado."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, "RAMRunner")
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except WindowsError:
            return False
    
    def enable_autostart(self):
        """Habilita el inicio automático con Windows."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            exe_path = Path(sys.executable).resolve()
            script_path = Path(__file__).resolve()
            
            # Si está ejecutándose como .py, usar python.exe
            if script_path.suffix == '.py':
                command = f'"{exe_path}" "{script_path}"'
            else:
                command = f'"{script_path}"'
            
            winreg.SetValueEx(key, "RAMRunner", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            print("✓ Inicio automático habilitado")
        except Exception as e:
            print(f"❌ Error al habilitar inicio automático: {e}")
    
    def disable_autostart(self):
        """Deshabilita el inicio automático con Windows."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, "RAMRunner")
                print("✓ Inicio automático deshabilitado")
            except WindowsError:
                pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"❌ Error al deshabilitar inicio automático: {e}")
    
    def exit_app(self):
        """Cierra la aplicación completamente."""
        print("👋 Cerrando RAM Runner...")
        if self.tray_icon:
            self.tray_icon.hide()
        self.widget.close()
        self.app.quit()
    
    def run(self):
        """Ejecuta la aplicación."""
        return self.app.exec_()


def main():
    # Verificar carpeta assets
    assets_path = Path("assets")
    if not assets_path.exists():
        print("⚠️  Creando carpeta 'assets'...")
        assets_path.mkdir(parents=True, exist_ok=True)
    
    gifs = list(assets_path.glob("*.gif"))
    if not gifs:
        print("⚠️  ADVERTENCIA: No se encontraron GIFs en 'assets/'")
        print("   Coloca tus GIFs en la carpeta 'assets/'")
        print("   Ejemplos: cat.gif, parrot.gif, horse.gif")
        print()
    else:
        print(f"✓ Se encontraron {len(gifs)} GIF(s) en assets/:")
        for gif in gifs:
            print(f"  - {gif.name}")
        print()
    
    app = RAMRunnerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()