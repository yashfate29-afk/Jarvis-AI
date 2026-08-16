@echo off
cd /d "C:\Users\yashf\OneDrive\Desktop\Jarvis AI\agent-starter-react"
start "Jarvis Server" cmd /k "pnpm dev"
timeout /t 40 /nobreak
start chrome --app=http://localhost:3000 --window-size=1000,700