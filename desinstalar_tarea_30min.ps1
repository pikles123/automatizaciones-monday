# Quita la tarea programada "Monday Copiar Columnas API".
# Ejecutar: .\desinstalar_tarea_30min.ps1

$nombreTarea = "Monday Copiar Columnas API"
$tarea = Get-ScheduledTask -TaskName $nombreTarea -ErrorAction SilentlyContinue
if ($tarea) {
    Unregister-ScheduledTask -TaskName $nombreTarea -Confirm:$false
    Write-Host "Tarea '$nombreTarea' desinstalada." -ForegroundColor Green
} else {
    Write-Host "No existe la tarea '$nombreTarea'." -ForegroundColor Yellow
}
