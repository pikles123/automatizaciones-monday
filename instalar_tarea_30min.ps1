# Instala la tarea programada que ejecuta la copia de columnas cada 30 minutos.
# Ejecutar una vez: clic derecho -> "Ejecutar con PowerShell" o en PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
#   .\instalar_tarea_30min.ps1

$nombreTarea = "Monday Copiar Columnas API"
$rutaProyecto = $PSScriptRoot
$rutaBat = Join-Path $rutaProyecto "ejecutar_copia.bat"

if (-not (Test-Path $rutaBat)) {
    Write-Host "Error: No se encuentra ejecutar_copia.bat en $rutaProyecto" -ForegroundColor Red
    exit 1
}

# Eliminar tarea si ya existe (para reinstalar)
$tarea = Get-ScheduledTask -TaskName $nombreTarea -ErrorAction SilentlyContinue
if ($tarea) {
    Unregister-ScheduledTask -TaskName $nombreTarea -Confirm:$false
    Write-Host "Tarea anterior eliminada." -ForegroundColor Yellow
}

$accion = New-ScheduledTaskAction -Execute $rutaBat -WorkingDirectory $rutaProyecto
$disparador = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (TimeSpan::FromMinutes(30)) -RepetitionDuration ([TimeSpan]::MaxValue)
$config = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $nombreTarea -Action $accion -Trigger $disparador -Settings $config -Description "Copia columnas origen a API en board leads evaluaciones (solo filas con cambios). Cada 30 min."

Write-Host "Tarea instalada: '$nombreTarea'" -ForegroundColor Green
Write-Host "Se ejecutará cada 30 minutos. Primera ejecución: ahora." -ForegroundColor Green
Write-Host "Para desinstalar: Desinstalar_tarea_30min.ps1 o Panel de control -> Programador de tareas" -ForegroundColor Gray
