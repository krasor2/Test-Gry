from __future__ import annotations

import io
import math
import wave
from array import array
from typing import Dict

import pygame


SAMPLE_RATE = 22050

_AUDIO_ENABLED = True
_SOUND_CACHE: Dict[str, pygame.mixer.Sound] = {}
_MUSIC_BYTES: bytes | None = None


def set_audio_enabled(enabled: bool) -> None:
    """Toggle runtime audio playback and clear caches when disabled."""

    global _AUDIO_ENABLED
    _AUDIO_ENABLED = enabled
    if not enabled:
        _SOUND_CACHE.clear()


def is_audio_available() -> bool:
    return _AUDIO_ENABLED and pygame.mixer.get_init() is not None


def play(name: str) -> None:
    if not is_audio_available():
        return
    try:
        sound = _load_sound(name)
        sound.play()
    except pygame.error:
        pass


def start_music(loop: int = -1, volume: float = 0.4) -> None:
    if not is_audio_available():
        return
    try:
        pygame.mixer.music.load(io.BytesIO(_get_music_bytes()))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
    except pygame.error:
        print("Nie udało się wczytać muzyki tła.")


def _load_sound(name: str) -> pygame.mixer.Sound:
    if name not in _SOUND_CACHE:
        _SOUND_CACHE[name] = pygame.mixer.Sound(file=io.BytesIO(_build_sound_bytes(name)))
    return _SOUND_CACHE[name]


def _build_sound_bytes(name: str) -> bytes:
    if name == "shoot":
        samples = _synth_tone(880, 0.12, volume=0.45, harmonics=[1.0, 0.4])
    elif name == "hit":
        samples = _synth_noise(0.18, volume=0.6)
    elif name == "power":
        samples = _synth_chirp(440, 880, 0.38, volume=0.55)
    else:
        raise ValueError(f"Unknown sound asset: {name}")
    return _to_wave_bytes(samples)


def _get_music_bytes() -> bytes:
    global _MUSIC_BYTES
    if _MUSIC_BYTES is None:
        _MUSIC_BYTES = _to_wave_bytes(_synth_music_loop())
    return _MUSIC_BYTES


def _to_wave_bytes(samples: array) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(samples.tobytes())
    return buffer.getvalue()


def _synth_tone(
    frequency: float,
    duration: float,
    *,
    volume: float,
    harmonics: list[float] | None = None,
) -> array:
    harmonics = harmonics or [1.0]
    total_weight = max(1e-6, sum(abs(h) for h in harmonics))
    sample_count = max(1, int(SAMPLE_RATE * duration))
    attack = max(1, int(sample_count * 0.08))
    release = max(1, int(sample_count * 0.2))
    data = array("h")
    for i in range(sample_count):
        t = i / SAMPLE_RATE
        sample = 0.0
        for idx, weight in enumerate(harmonics):
            sample += weight * math.sin(2 * math.pi * frequency * (idx + 1) * t)
        sample = sample / total_weight
        if i < attack:
            sample *= i / attack
        elif i > sample_count - release:
            sample *= max(0.0, (sample_count - i) / release)
        data.append(int(max(-1.0, min(1.0, sample * volume)) * 32767))
    return data


def _synth_noise(duration: float, *, volume: float) -> array:
    sample_count = max(1, int(SAMPLE_RATE * duration))
    decay = 1.0 / sample_count
    data = array("h")
    seed = 0x2C3D
    for i in range(sample_count):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        raw = (seed / 0x7FFFFFFF) * 2.0 - 1.0
        envelope = max(0.0, 1.0 - i * decay)
        sample = raw * envelope * volume
        data.append(int(max(-1.0, min(1.0, sample)) * 32767))
    return data


def _synth_chirp(
    start_freq: float,
    end_freq: float,
    duration: float,
    *,
    volume: float,
) -> array:
    sample_count = max(1, int(SAMPLE_RATE * duration))
    data = array("h")
    for i in range(sample_count):
        progress = i / sample_count
        frequency = start_freq + (end_freq - start_freq) * progress
        t = i / SAMPLE_RATE
        sample = math.sin(2 * math.pi * frequency * t)
        envelope = min(1.0, progress / 0.15) * max(0.0, (1.0 - progress) / 0.2)
        sample *= envelope * volume
        data.append(int(max(-1.0, min(1.0, sample)) * 32767))
    return data


def _note_frequency(name: str) -> float:
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    base_note = name[:-1]
    octave = int(name[-1])
    semitone = notes.index(base_note)
    return 440.0 * 2 ** ((octave - 4) + (semitone - notes.index("A")) / 12)


def _synth_music_loop() -> array:
    bpm = 108
    beat_duration = 60.0 / bpm
    melody = [
        "C5",
        "E5",
        "G5",
        "E5",
        "F5",
        "A5",
        "G5",
        "E5",
        "D5",
        "F5",
        "A5",
        "F5",
        "G5",
        "B5",
        "A5",
        "E5",
    ]
    bass = [
        "C3",
        "C3",
        "C3",
        "C3",
        "F3",
        "F3",
        "F3",
        "F3",
        "G3",
        "G3",
        "G3",
        "G3",
        "F3",
        "F3",
        "F3",
        "F3",
    ]
    beat_samples = max(1, int(SAMPLE_RATE * beat_duration))
    total_samples = beat_samples * len(melody)
    data = array("h")
    for beat_index, note in enumerate(melody):
        bass_note = bass[beat_index]
        for i in range(beat_samples):
            sample_index = beat_index * beat_samples + i
            t = sample_index / SAMPLE_RATE
            env_attack = min(1.0, i / (beat_samples * 0.18))
            env_release = min(1.0, (beat_samples - i) / (beat_samples * 0.28))
            env = env_attack * env_release
            melody_sample = math.sin(2 * math.pi * _note_frequency(note) * t) * env
            bass_env = 0.55 + 0.35 * env
            bass_sample = math.sin(2 * math.pi * _note_frequency(bass_note) * t) * bass_env
            combined = 0.42 * melody_sample + 0.28 * bass_sample
            data.append(int(max(-1.0, min(1.0, combined)) * 32767))
    return data
