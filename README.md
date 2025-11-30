# 🚀 RAM Runner: Widget Animado de Escritorio para Monitoreo de RAM

[![GitHub](https://img.shields.io/badge/GitHub-katsu3141-blue?logo=github)](https://github.com/katsu3141/ram-runner-gui)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)

**RAM Runner** es una aplicación de escritorio ligera y con diseño divertido para Windows que muestra el uso de la memoria RAM a través de un personaje (GIF) animado, cuya **velocidad se ajusta dinámicamente** según la carga del sistema. Cuanta más RAM uses, más rápido se mueve tu "pet widget".

---

## ✨ Características Principales

* **Monitoreo de RAM en Tiempo Real:** Muestra el porcentaje de RAM usada.
* **Velocidad Dinámica:** El GIF animado acelera su movimiento en función del porcentaje de RAM (usa una curva cuadrática para acelerar notablemente con alta RAM).
* **Widget Interactivo:** Ventana siempre encima, sin bordes, con fondo transparente, redimensionable y arrastrable.
* **Integración con Bandeja del Sistema:** Icono en la bandeja del sistema para:
    * Cambiar fácilmente entre diferentes GIFs de la carpeta `assets/`.
    * Habilitar/deshabilitar el inicio automático con Windows.
* **Herramienta de Utilidad Incluida:** Incluye `quitar_fondo.py` para facilitar la preparación de nuevos GIFs haciéndolos transparentes.

---

## 🛠️ Instalación y Requisitos

RAM Runner requiere Python 3.x y las siguientes librerías:

### 1. Requisitos del Sistema

* **Sistema Operativo:** Windows (El módulo `winreg` y las llamadas al explorador son específicas de Windows).
* **Python:** Versión 3.6 o superior (La aplicación fue probada en Python 3.13.9).

### 2. Instalación de Dependencias

Asegúrate de estar en tu entorno virtual (`ram_runner_env`) y ejecuta:

```bash
# ¡NOTA!: Debes tener PyQt5, psutil, y Pillow instalados.
pip install pyqt5 psutil pillow numpy

3. Ejecución
Ejecuta el script principal:
python ram_runner.py

El widget aparecerá en tu escritorio y el icono de control (RAM) estará en la bandeja del sistema.

Personalización de GIFs
Para agregar o cambiar tu pet widget:

Coloca tus archivos GIF animados en la carpeta assets/.

Haz clic derecho en el icono RAM de la bandeja del sistema.

En el menú "Runner", selecciona el GIF que deseas activar.

Herramienta Auxiliar: quitar_fondo.py
Si tu GIF tiene un fondo sólido (ej. blanco o verde) y quieres que sea transparente:

Ejecuta la herramienta de utilidad:

python quitar_fondo.py


Usa la interfaz gráfica (Tkinter) para:

Seleccionar el GIF de entrada.

Especificar el color de fondo a eliminar (ej. Blanco 255, 255, 255).

Ajustar la tolerancia para una mejor detección de bordes.

Autor
Benjamin Nina

GitHub: @katsu3141


