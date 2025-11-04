# Chibi Garden Guardians

Prototyp gry 2D typu horde survival, w którym bronimy ogródka pełnego chibi roślin i warzyw.

## Wymagania

- Python 3.10+
- `pip`

## Instalacja i uruchomienie

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py            # uruchomienie z dźwiękiem

# Przydatne przełączniki
# python main.py --mute        # start w trybie bez dźwięku (przydatne gdy brak urządzenia audio)
# python main.py --fullscreen  # okno wypełni cały ekran
```

Gra uruchamia się w oknie 960x540 i jest gotowa do zabawy od razu po pobraniu.

## Sterowanie

- `WASD` lub strzałki – ruch bohatera.
- Mysz – celowanie i strzał.
- `ESC` – powrót do menu wyboru broni.
- `R` – restart po przegranej.

## Funkcje

- 3 rodzaje broni do wyboru na starcie (Seed Blaster, Thorn Fork, Solar Beam).
- 3 unikalnych przeciwników: Sproutling, Root Beast, Sporeshroom.
- Podstawowa grafika w stylu chibi roślin/warzyw oraz dynamiczna siatka tła.
- Efekty cząsteczkowe przy trafieniach i eliminacjach.
- Podstawowa ścieżka dźwiękowa oraz efekty strzału/obrażeń generowane proceduralnie przy starcie gry (brak plików binarnych).
- Opcjonalny tryb bez dźwięku i pełnoekranowy przełączany parametrami wiersza poleceń.

## Struktura projektu

```
game/
  __init__.py
  audio.py       # generowanie i odtwarzanie efektów oraz muzyki
  settings.py    # konfiguracja gry
  entities.py    # logika gracza, przeciwników, pocisków i świata gry
main.py          # pętla gry, menu, obsługa zdarzeń
requirements.txt
```

Miłej zabawy w ogródku!
