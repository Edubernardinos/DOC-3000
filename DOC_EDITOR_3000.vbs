Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Inicia o Python sem janela preta de terminal
pythonExe = currentDir & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonExe) Then
    pythonExe = currentDir & "\.venv\Scripts\python.exe"
End If

WshShell.Run """" & pythonExe & """ -W ignore doc_editor.py", 0, False
