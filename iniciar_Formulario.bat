@echo off

:: Mensagem inicial
echo Inicializando o ambiente...

:: Pegando o nome do usuário
set "user=%USERNAME%"

:: Abrir o Portal Único do Siscomex com suporte a depuração remota
start "Portal Siscomex" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\%user%\AppData\Local\Google\Chrome\User Data" https://portalunico.siscomex.gov.br/
echo Abrindo Portal Siscomex...

:: Abrir uma nova aba do Chrome com a URL desejada
start "Nova Aba Chrome" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\%user%\AppData\Local\Google\Chrome\User Data" http://127.0.0.1:5000
echo Abrindo a nova aba no Chrome...

:: Executar o script Python
echo Executando o sistema Python...
python "C:\Users\%user%\OneDrive - Donaldson Company, Inc\Desktop\DUIMP\Plan DUIMP Project\sistemaCTP.py"

:: Pausa para evitar fechamento imediato do console em caso de erro no Python
echo Pressione qualquer tecla para encerrar...
pause

exit
