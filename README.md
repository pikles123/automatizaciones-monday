# Automatización Monday – Copiar columnas a API

Copia los valores de 3 columnas del board **leads evaluaciones** a otras 3 columnas (las “API”):

| Origen           | Destino            |
|------------------|--------------------|
| INST FINANCIERA  | Inst Financiera API |
| MAXIMO PUNTAJE   | Max Ptje API       |
| ESTADO ACTUAL    | Estado Actual API  |

Los valores se copian como texto o número según corresponda.

## Requisitos

- Python 3.8+
- Token de API de Monday.com

## Instalación

1. Clona o copia este proyecto en tu equipo.

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configuración:
   - Copia `.env.example` a `.env`.
   - En `.env`:
     - **MONDAY_API_TOKEN**: tu token de API (Monday.com → Perfil → Developers → API).
     - **BOARD_ID**: ID del board “leads evaluaciones” (el número que aparece en la URL del board).

5. (Opcional) Si los nombres de las columnas en tu board son distintos, edita `config_columnas.json` y ajusta el mapeo `"nombre_origen": "nombre_destino"`.

## Uso

Ejecuta el script para copiar en una sola pasada todos los ítems del board:

```bash
python copiar_columnas_api.py
```

El script:

1. Obtiene las columnas del board y localiza las 6 (3 origen + 3 destino) por nombre.
2. Lee todos los ítems con sus valores en esas columnas.
3. **Solo actualiza las filas donde algún valor de las 3 columnas origen es distinto** al valor actual de la columna API correspondiente. Así se evitan actualizaciones innecesarias.

Puedes ejecutarlo a mano cuando quieras o usar la tarea programada (cada 30 minutos).

---

## Tarea programada cada 30 minutos

Para que el script se ejecute **cada 30 minutos** y solo toque filas con cambios:

1. Instala la tarea (solo una vez). En PowerShell, desde la carpeta del proyecto:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
   .\instalar_tarea_30min.ps1
   ```
   O clic derecho en `instalar_tarea_30min.ps1` → **Ejecutar con PowerShell**.

2. La tarea **"Monday Copiar Columnas API"** quedará en el Programador de tareas de Windows y se ejecutará cada 30 min.

3. Para quitarla más adelante:
   ```powershell
   .\desinstalar_tarea_30min.ps1
   ```
   O: Panel de control → Herramientas administrativas → Programador de tareas → buscar la tarea y eliminarla.

---

## Subir a GitHub

El proyecto ya está inicializado con Git. Para subirlo a GitHub:

1. Crea un repositorio nuevo en [github.com](https://github.com/new):
   - Nombre sugerido: `automatizacion-monday`
   - Sin README, sin .gitignore (ya los tienes en el proyecto)
   - Público o privado, como prefieras

2. En la carpeta del proyecto, enlaza el remoto y sube (sustituye `TU_USUARIO` por tu usuario de GitHub):

   ```bash
   git remote add origin https://github.com/TU_USUARIO/automatizacion-monday.git
   git branch -M main
   git push -u origin main
   ```

3. **Importante:** el archivo `.env` con tu token y BOARD_ID no se sube (está en `.gitignore`). Quien clone el repo debe crear su propio `.env` a partir de `.env.example`.
