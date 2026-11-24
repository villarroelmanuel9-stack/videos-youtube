# Aprendizajes del canal "Pasó de Verdad"

Notas que se aplican a cada video nuevo (se actualizan después de cada historia).

## Producción
- **Probar cada escena en fotogramas sueltos ANTES de generar el video completo** (ahorra re-renders de 10 min).
- Todo texto/recuadro debe **ajustar su ancho automáticamente** (error de la tarjeta cortada en Dinosaurios).
- Sincronizar efectos y recuadros con **la palabra exacta** de la voz (reconocimiento de voz), no con porcentajes.
- Los objetos deben **parecer lo que son**: revisar siluetas (los chalecos de Alcatraz parecían panes).
- Barridos de cámara entre escenas + destellos/sacudidas en momentos fuertes = más dinamismo.
- Fondos en capas (parallax) y primer plano dan profundidad.

- Guardar el reconocimiento de voz en caché (`*.palabras.json`) para previsualizar con los tiempos reales.
- Motor común `pro.py` + personajes `humanos.py`: cada historia solo define sus escenas.
- Revisar símbolos culturales (la estrella de Chile salió como pentágono la primera vez).
- Textos formados con objetos (velas → "PAZ") necesitan un refuerzo visual para leerse.

## Calidad de dibujo (desde Wojtek)
- `realista.LienzoReal`: sombreado degradado, contornos finos del color del objeto, textura suave y `pelaje()`.
- `Humano(realista=True, cabeza=0.86)`: personajes con proporciones algo más reales.
- `pro.generar(..., acabado=True)`: curva de color, bloom en las luces y grano fino en cada fotograma.
- Ojo con el grano: con mucho grano el video pesó 111 MB. Grano suave (1.6) que cambia cada 2 fotogramas y
  entregar comprimido (crf 25) → archivos de ~20-30 MB.

## Audio (corregido tras el aviso del usuario: los efectos tapaban la voz)
- **La voz siempre va en una pista aparte** y se mezcla al final con `mezcla_audio.mezcla_final()`; todos los motores
  (cine, caricatura, dinos, alcatraz, pro) pasan por ahí.
- La voz se normaliza a ≈ -18 dBFS; los efectos se limitan a -10 dBFS y bajan ~10 dB mientras se habla (ducking).
- Nunca normalizar todo junto por el pico: un golpe fuerte bajaba también la voz.
- Cada video imprime un informe: **margen voz/efectos entre 15 y 30 dB**. Si sale "⚠ EFECTOS DEMASIADO ALTOS", no se entrega.
- Para arreglar videos ya hechos sin redibujar: `python remezclar.py N`.
- Desde Wojtek: `pro.generar(..., hifi=True)` → efectos con reverberación, paneo estéreo, ambientes envolventes y
  sonidos nuevos (gruñido, camión, bocina de barco, artillería, ducha, botella, pasos, multitud). La voz no se toca.

## Retención
- Gancho en el primer segundo con un dato que choque + imagen fuerte.
- "Loop abierto" temprano ("y eso no es lo más loco…").
- Cambio visual cada 3–5 s; algún momento sorpresa visual a mitad del video.
- Final con una acción concreta para comentar (palabra o SÍ/NO) y pedir suscripción.

## Identidad: cada video debe ser distinto
| Video | Paleta | Recuadros | Palabra activa | Final |
|---|---|---|---|---|
| Dinosaurios | Cálida, día | Tarjetas blancas con emoji | Amarillo | Botón SUSCRIBIRSE con clic + "Comenta «dino»" |
| Alcatraz | Fría, noche | Fichas de expediente + sellos | Celeste | Reja + carteles SE BUSCA + "CASO ABIERTO" + SÍ/NO |
| D. B. Cooper | Retro años 70 (naranja/verde azulado) | Pases de abordar | Naranja | Tablero de detective + comentario escribiéndose + avioneta con cartel |
| 33 mineros | Industrial, roca | Placas metálicas con franja de peligro + contador DÍA N | Caja amarilla | Bandera de Chile + "33" + pin "¿Dónde estabas?" + placa con lámpara |
| Andes | Nieve, tonos fríos | Notas de cuaderno manuscritas | Coral | Página de diario con casillas + lápiz que escribe "suscríbete" |
| Juliane Koepcke | Selva, lluvia, recuerdo en sepia | Libreta de campo | Verde lima | Mapa con la ruta dibujándose + brote que crece con "SUSCRÍBETE" |
| Tregua de Navidad | Noche nevada, velas | Tarjetas navideñas antiguas | Cinta roja | Velas que escriben "PAZ" + regalo que se abre |
| Wojtek (oso soldado) | Semi-realista: desierto, puerto, Montecassino, Escocia | Libretas militares verde oliva con bandera polaca | Subrayado rojo | Estatua de bronce + huellas + sello de huella "SUSCRÍBETE" |
