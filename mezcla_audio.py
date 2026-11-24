"""
Mezcla final profesional: la VOZ siempre es lo principal.

    from mezcla_audio import mezcla_final
    salida = mezcla_final(voz, efectos)   # arrays float32 (n, 2) a 44.1 kHz

Qué hace:
  1. Normaliza la voz a un nivel fijo (RMS de las partes habladas ≈ -18 dBFS).
  2. Limita suavemente el bus de efectos (golpes fuertes) a -10 dBFS sin apagar el ambiente.
  3. "Ducking": mientras la voz habla, los efectos bajan ~10 dB; en las pausas vuelven suavemente.
  4. Limitador suave al final (sin bajar el volumen general, así la voz no pierde fuerza).
  5. Informe automático: avisa si los efectos quedan demasiado cerca de la voz.
"""
from __future__ import annotations

import numpy as np

SR = 44100
BLOQUE = 441  # 10 ms

OBJETIVO_VOZ_RMS = 0.125      # ≈ -18 dBFS en las partes habladas
PICO_EFECTOS = 0.32           # ≈ -10 dBFS
BAJADA_CON_VOZ = 0.70         # 70 % menos volumen de efectos mientras se habla (≈ -10.5 dB)
MARGEN_MINIMO_DB = 15.0       # los efectos deben quedar al menos 15 dB por debajo de la voz
MARGEN_MAXIMO_DB = 30.0       # más que esto y el ambiente casi no se oye


def _rms_bloques(mono):
    n = len(mono) // BLOQUE
    if n == 0:
        return np.zeros(1, np.float32)
    x = mono[:n * BLOQUE].reshape(n, BLOQUE)
    return np.sqrt((x ** 2).mean(1) + 1e-12)


def _db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def _limitador_suave(x, umbral=0.88, techo=0.98):
    a = np.abs(x)
    sobre = a > umbral
    if not sobre.any():
        return x
    rango = techo - umbral
    y = x.copy()
    y[sobre] = np.sign(x[sobre]) * (umbral + rango * np.tanh((a[sobre] - umbral) / rango))
    return y


def mezcla_final(voz: np.ndarray, efectos: np.ndarray, informe: bool = True, nombre: str = "") -> np.ndarray:
    n = max(len(voz), len(efectos))
    v = np.zeros((n, 2), np.float32)
    e = np.zeros((n, 2), np.float32)
    v[:len(voz)] = voz
    e[:len(efectos)] = efectos

    # 1) voz a nivel fijo, medido solo en las partes habladas
    env_v = _rms_bloques(v.mean(1))
    umbral_habla = max(env_v.max() * 0.08, 1e-4)
    hablado = env_v[env_v > umbral_habla]
    rms_habla = float(np.sqrt((hablado ** 2).mean())) if len(hablado) else 1e-3
    v *= OBJETIVO_VOZ_RMS / max(rms_habla, 1e-6)

    # 2) bus de efectos con pico controlado
    e = PICO_EFECTOS * np.tanh(e / PICO_EFECTOS)  # limita los golpes fuertes sin apagar el ambiente

    # 3) ducking: detectar habla (con margen de 250 ms) y bajar los efectos
    env_v = _rms_bloques(v.mean(1))
    activo = (env_v > OBJETIVO_VOZ_RMS * 0.15).astype(np.float32)
    k = 25
    pad = np.pad(activo, (k, k))
    dil = np.max(np.lib.stride_tricks.sliding_window_view(pad, 2 * k + 1), axis=1)[:len(activo)]
    suav = np.convolve(dil, np.ones(15) / 15, mode="same")
    ganancia = 1.0 - BAJADA_CON_VOZ * np.clip(suav, 0, 1)
    g = np.repeat(ganancia, BLOQUE)
    g = np.concatenate([g, np.full(n - len(g), g[-1] if len(g) else 1.0)])[:n]
    e *= g[:, None]

    mezcla = _limitador_suave(v + e)

    if informe:
        env_e = _rms_bloques(e.mean(1))
        m = min(len(env_e), len(env_v))
        habla = env_v[:m] > OBJETIVO_VOZ_RMS * 0.15
        if habla.any():
            voz_db = _db(np.sqrt((env_v[:m][habla] ** 2).mean()))
            efx_db = _db(np.sqrt((env_e[:m][habla] ** 2).mean()))
            margen = voz_db - efx_db
            estado = ("OK" if MARGEN_MINIMO_DB <= margen <= MARGEN_MAXIMO_DB else
                      "⚠ EFECTOS DEMASIADO ALTOS" if margen < MARGEN_MINIMO_DB else "aviso: ambiente muy suave")
            print(f"   · audio {nombre}: voz {voz_db:.1f} dB | efectos bajo la voz {efx_db:.1f} dB | "
                  f"margen {margen:.1f} dB → {estado}")
    return mezcla.astype(np.float32)
