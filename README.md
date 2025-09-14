# tetris


# 🎮 Tetris (Python + Pygame)

Un classico **Tetris** realizzato in **Python** usando la libreria **Pygame**.
I pezzi cadono dall’alto, puoi muoverli, ruotarli e completare righe per guadagnare punti.

---

## 📂 Struttura del progetto

```
tetris/
│
├── tetris.py     # script principale del gioco
└── README.md     # questo file
```

---

## ⚙️ Installazione

1. Assicurati di avere **Python 3.9+** installato.
2. Installa **pygame** se non lo hai già:

```bash
pip install pygame
```

---

## ▶️ Avvio

Esegui il gioco con:

```bash
python tetris.py
```

---

## 🎮 Comandi

* ⬅️ **Freccia sinistra** → sposta il pezzo a sinistra
* ➡️ **Freccia destra** → sposta il pezzo a destra
* ⬇️ **Freccia giù** → accelera la caduta del pezzo
* ⬆️ **Freccia su** → ruota il pezzo
* ❌ **Chiudi finestra** → esci dal gioco

---

## 🕹️ Regole del gioco

* I tetramini cadono dall’alto.
* Puoi muoverli e ruotarli finché non toccano il fondo o altri blocchi.
* Quando una riga è completamente piena, viene eliminata e guadagni **10 punti**.
* Il gioco termina se i blocchi raggiungono la parte superiore della griglia.

---

## 📌 Caratteristiche

* ✅ 7 forme di tetramini classici (I, J, L, O, S, T, Z)
* ✅ Rotazione dei pezzi
* ✅ Eliminazione righe complete
* ✅ Conteggio punteggio in tempo reale
* ✅ Game Over al riempimento della griglia

---

## 🔮 Idee future

* Aggiungere livelli con velocità crescente
* Inserire musica ed effetti sonori
* Mostrare l’anteprima del prossimo pezzo nella GUI
* Salvataggio **High Score** su file

---

