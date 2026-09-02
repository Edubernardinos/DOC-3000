$ws = New-Object -ComObject WScript.Shell
$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Atalho na Área de Trabalho
$desktop = [Environment]::GetFolderPath('Desktop')
$scDesktop = $ws.CreateShortcut((Join-Path $desktop "DOC_EDITOR_3000.lnk"))
$scDesktop.TargetPath = (Join-Path $currentDir "DOC_EDITOR_3000.vbs")
$scDesktop.WorkingDirectory = $currentDir
$scDesktop.IconLocation = (Join-Path $currentDir "app_icon.ico")
$scDesktop.Description = "DOC_EDITOR_3000 - Editor Profissional de Documentos e Fotos"
$scDesktop.Save()

# Atalho no Menu Iniciar
$programs = [Environment]::GetFolderPath('Programs')
$scStart = $ws.CreateShortcut((Join-Path $programs "DOC_EDITOR_3000.lnk"))
$scStart.TargetPath = (Join-Path $currentDir "DOC_EDITOR_3000.vbs")
$scStart.WorkingDirectory = $currentDir
$scStart.IconLocation = (Join-Path $currentDir "app_icon.ico")
$scStart.Description = "DOC_EDITOR_3000 - Editor Profissional de Documentos e Fotos"
$scStart.Save()

Write-Host "[SUCESSO] Atalho DOC_EDITOR_3000 criado com sucesso na Area de Trabalho e no Menu Iniciar!" -ForegroundColor Green
