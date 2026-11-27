# Pendiente: regenerar las voces de los 40 relatos

**Estado (27/11/2026):** detenido por pedido del usuario. Las voces generadas con ElevenLabs **v3** no suenan como
Cristian Cornejo (salieron más agudas y actuadas: 160–198 Hz contra ~150 Hz de los misterios). Los videos ya
renderizados en `historias nuevas/` (3, 4, 5, 7, 10, 12, 14, 15, 16, 30 y las pruebas de Hachiko) **no se publican**.

**Cuándo:** al renovarse los créditos de ElevenLabs (plan Starter, ~30.000 créditos, renovación ≈ 26/12/2026).

**Cómo:**
1. Regenerar los 40 audios con la voz `ClNifCEVq1smkl4M3aTk` (Cristian Cornejo), **una sola toma cada uno**, con el
   modelo que el usuario apruebe (probar primero v2 — `eleven_multilingual_v2` — sin etiquetas de emoción).
   Lista: 3 4 5 7 10 12 14 15 16 23 28 32 34 36 41 42 43 44 45 46 51 54 57 58 59 62 63 64 65 68 72 75 81 84 85 87 88 96 97 100.
2. Guardar como `audios/relatos/relato_NNN.mp3` (reemplazando los de v3) y borrar su `.palabras.json`.
3. Renderizar: `bash relatos_hf/lote.sh <números>` (planes visuales ya listos en `relatos_hf/planes/`).
4. Miniaturas: `python3 relatos_hf/miniaturas.py <números>` (no reemplaza las que hizo el usuario).

El motor ya no deforma la voz: ritmo casi intacto (±6 %), sin EQ ni de-esser, solo limpieza de graves y -14 LUFS.
