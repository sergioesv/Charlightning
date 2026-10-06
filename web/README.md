# Página web de Charlightning

Un solo servicio Python (FastAPI) que sirve la API y las páginas. Los números
salen de `calculate_risk/`, el mismo motor del programa de escritorio.

```
web/
├── api.py         rutas HTTP (delgadas): /api/evaluar, /api/ng, /api/informe, ...
├── servicio.py    lo que la web le pide al motor, sin nada de HTTP
├── limite.py      límite de peticiones por IP
├── ng_colombia.py genera estatico/ng-colombia.html (python -m web.ng_colombia)
└── estatico/      páginas, robots.txt, sitemap.xml y llms.txt
```

Al agregar una página: ponerla en `sitemap.xml` con su `<link rel="canonical">` (una
prueba lo revisa).

## Probarla en el computador

```
pip install -r requirements.txt
uvicorn web.api:app --reload
```

Abrir <http://localhost:8000>. La documentación de la API queda en `/api/docs`.

## Rutas

| Ruta | Qué hace |
|---|---|
| `POST /api/evaluar` | JSON de un caso (formato de `casos/*.json`) → R1..R4, componentes por zona y avisos |
| `GET /api/ng?lat=&lon=` | N_G desde la climatología LIS/OTD de la NASA, con su procedencia |
| `POST /api/informe` | `{"caso": {...}, "proyecto": {"Proyecto": "..."}}` → memoria de cálculo en PDF (`?medidas=false` para no buscar medidas) |
| `GET /api/ejemplos`, `/api/ejemplos/{nombre}` | los casos de `casos/` |
| `GET /api/validacion` | los ejemplos del Anexo E evaluados en vivo frente a la norma |
| `GET /api/salud` | para el chequeo de Railway |

Si el caso trae `"emplazamiento": {"modo": "coordenadas", ...}`, el servidor
recalcula N_G desde las coordenadas: el número siempre corresponde a la fuente
que dice el informe.

## Publicarla en Railway

1. En Railway: **New Project → Deploy from GitHub repo →** `sergioesv/charlightning`.
2. En el servicio, **Settings → Source → Branch**: `web` (luego `master` cuando se una).
3. **Settings → Deploy**:
   - **Custom Start Command**: `uvicorn web.api:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'`
     (es el mismo del `Procfile`; ponerlo aquí no depende de que Railway lea ese archivo).
   - **Healthcheck Path**: `/api/salud`
4. Railway detecta Python con `requirements.txt` y `.python-version`. Cada `git push`
   a la rama vuelve a publicar.
5. **Settings → Networking → Generate Domain** da una URL `*.up.railway.app` para probar.

Publicada en **https://charlightning.org** (y `www.charlightning.org`), con el DNS en Cloudflare
(dos CNAME en «DNS only» hacia Railway y dos TXT `_railway-verify` de verificación).

Variables opcionales (Settings → Variables):

| Variable | Por omisión | Para qué |
|---|---|---|
| `LIMITE_CALCULOS` | 120 | evaluaciones, consultas de N_G, abrir casos y desgloses por minuto por IP |
| `LIMITE_INFORMES` | 5 | PDF por minuto por IP (cada uno tarda ~10 s) |

## Dominio propio

1. Comprar el dominio (por ejemplo en Cloudflare, Namecheap o un registrador `.co`).
2. En Railway: **Settings → Networking → Custom Domain** → escribir el dominio.
3. Railway muestra un registro `CNAME` (y uno `TXT` de verificación): crearlos en el
   DNS del registrador. Para el dominio raíz (sin `www`) hace falta un DNS que
   permita CNAME en la raíz (Cloudflare lo hace).
4. El certificado HTTPS lo pone Railway solo.

## Código QR para donaciones

`web/estatico/img/qr-breb.png`: el QR de Nequi Negocios,
recortado de la captura de la app. La llave va escrita en `apoyar.html`.

## Supabase (siguiente fase)

No se usa todavía. Cuando haga falta (cuentas, casos guardados, estadísticas),
entra como otra implementación detrás de `servicio.py`, sin tocar el motor.
