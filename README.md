# TETRIS

🎮 Tetris in Python (Pygame)

Un clone completo di Tetris, scritto in Python 3 + Pygame, con tutte le funzionalità moderne del gioco classico.

⸻

🚀 Funzionalità
	•	Modalità di gioco
	•	🟢 Marathon → Gioca finché non perdi
	•	⏱ Time Attack → 3 minuti per fare più punti possibile
	•	Gameplay moderno
	•	🎯 Ghost piece (ombra dove cadrebbe il pezzo)
	•	🌀 SRS rotation system (rotazioni e wall kicks standard del Tetris)
	•	🎒 7-bag randomizer (pezzi distribuiti in modo equo)
	•	📦 Hold (C) → puoi tenere un pezzo da usare più tardi
	•	⬇ Soft drop (↓) → abbassi il pezzo più velocemente (+1 punto per cella)
	•	⬇⬇ Hard drop (SPACE) → fa cadere subito il pezzo (+2 punti per cella)
	•	⚡ Line clear animato (flash bianco prima della cancellazione)
	•	🏆 High score salvato in highscore.txt
	•	Extra
	•	🎵 Musica di sottofondo attivabile/disattivabile (M)
	•	⏸ Pausa (P) → blocca il gioco e mostra overlay “PAUSED”
	•	📊 Level up automatico ogni 10 righe → aumenta la velocità
	•	🎨 Interfaccia grafica con pannello laterale (punteggio, livello, prossimo pezzo, hold)

⸻

🎹 Comandi

Tasto	Azione
← / →	Muovi pezzo
↓	Soft drop (+1 punto/cella)
↑	Rotazione CW
Z	Rotazione CCW
X	Rotazione 180°
SPACE	Hard drop (+2 punti/cella)
C	Hold / Swap pezzo
M	Attiva/Disattiva musica
P	Pausa / Riprendi
Esc	Esci


⸻

🏅 Punteggi
	•	Soft drop → +1 punto per ogni cella scesa manualmente
	•	Hard drop → +2 punti per ogni cella scesa
	•	Linee completate:
	•	1 linea → 100 punti
	•	2 linee → 300 punti
	•	3 linee → 500 punti
	•	4 linee (Tetris!) → 800 punti

I punti vengono moltiplicati per il livello corrente.

⸻

🔧 Requisiti
	•	Python 3.9+
	•	Pygame (pip install pygame)

⸻

▶️ Avvio

python tetris.py


⸻

📂 Struttura
	•	tetris.py → codice principale del gioco
	•	highscore.txt → file che salva il punteggio massimo
	•	music/ → (opzionale) cartella con la musica .ogg

⸻

📊 Versioni del codice

Funzionalità	Versione corta	Versione lunga
Ghost piece	✅	✅
Hold (C)	✅	✅
Soft/Hard drop con punti	✅	✅
Line clear animato	✅	✅
High score salvato	✅	✅
Modalità Marathon / Time Attack	✅	✅
Pausa (P)	✅	✅
Rotazioni pezzi	Calcolate al volo (zip)	Scritte tutte esplicitamente
Wall kicks	Semplificati	Completi secondo SRS
Codice	Più corto e compatto	Più lungo ma fedele allo standard

👉 Usa la versione corta se vuoi solo giocare.
👉 Usa la versione lunga se vuoi imparare/studiare il codice del Tetris originale.

⸻

🛠 Roadmap futuri miglioramenti

Ecco alcune idee per rendere il gioco ancora più completo:
	•	🔊 Effetti sonori (su drop, clear, game over)
	•	🎶 Selezione musica con più tracce (N = next track)
	•	🌈 Animazioni grafiche (fade out, particelle quando si cancella una linea)
	•	🕹 Controller support (XBox/PS4 joypad via pygame.joystick)
	•	👥 Multiplayer locale (schermo diviso, 1v1)
	•	🌍 Multiplayer online (socket o WebSocket)
	•	🏅 Modalità Challenge (es. 40 linee nel minor tempo possibile)
	•	⚙️ Menù opzioni (difficoltà, velocità iniziale, skin dei pezzi)
	•	🖼 Temi grafici (colori alternativi, sfondi, stile GameBoy/classico)
	•	💾 Salvataggio impostazioni in file di configurazione

⸻

