---
# -- Bloque de Identificación y Configuración (Siempre presente) --
id: ASIT-GENESIS-CAx-LLC-STYLEGUIDE-0001-OV
rev: 0
llc: GENESIS
title: "ASI-T · Copilot Agent Styleguide (CAx + LLC Bridges)"
configuration: baseline
classification: "INTERNAL / EVIDENCE-REQUIRED"
version: "1.0.0"
release_date: 2025-01-16
maintainer: "ASI-T Architecture Team"

# -- Bloque de Procedencia y Sello Criptográfico (QS) --
provenance:
  policy_hash: "sha256:POLICY_HASH_PLACEHOLDER"
  model_sha: "sha256:MODEL_HASH_PLACEHOLDER"
  data_manifest_hash: "sha256:DATA_MANIFEST_HASH_PLACEHOLDER"
  operator_id: "UTCS:OP:ASI-T-ARCHITECTURE-TEAM"
  canonical_hash: "sha256:CANONICAL_HASH_PLACEHOLDER"

# -- Bloque de Licenciamiento --
licenses:
  code: "Apache-2.0"
  docs: "CC-BY-4.0"
---

# 📑 ASI-T · Copilot Agent Styleguide (CAx + LLC Bridges)

**id:** `ASIT-GENESIS-CAx-LLC-STYLEGUIDE-0001-OV`  
**llc:** `GENESIS`  
**rev:** 0  
**configuration:** `baseline`  
**classification:** `INTERNAL / EVIDENCE-REQUIRED`  
**version:** `1.0.0`  
**maintainer:** `ASI-T Architecture Team`

---

## Resumen

Este documento establece el estándar normativo para la creación, modificación y gestión de artefactos de conocimiento dentro de la arquitectura ASI-T. Define la gramática de archivos, la estructura de metadatos (UTCS-MI), el ciclo de vida de revisiones (HOV), y las directrices de formato que deben seguir todos los Agentes Copilot y contribuidores humanos. Su cumplimiento es obligatorio y se verifica automáticamente.

---

## 1. Principios Fundamentales (Golden Rules)

1.  **Principio de UIX.v1 (Universal Injection):** Todo agente DEBE importar la última versión del prompt `UIX.v1` antes de cualquier operación de lectura, escritura o modificación. Es la única fuente de verdad sobre el contexto operativo.
2.  **Adherencia Estricta a la Gramática de Paths TFA:** Todos los artefactos DEBEN residir en una ruta que cumpla con la gramática canónica `TFA/<LAYER>/<LLC>/...`. No se permiten rutas fuera de este estándar.
3.  **Operación bajo el Guardián Ético MAL-EEM:** Todas las acciones deben ser validadas por el módulo `MAL-EEM`, asegurando un comportamiento ético, empático y con una política de `fail-closed` ante cualquier ambigüedad.
4.  **Evidencia Determinista UTCS/QS:** Todo cambio (commit/PR) DEBE estar respaldado por evidencia determinista inmutable (un *Quantum Seal* o `QS blob`) y referenciado en la cabecera `UTCS`.
5.  **Ciclo de Vida de Cambios FCR:** El procedimiento para cualquier modificación sigue estrictamente las `Follow-up Chain Rules`: `FCR-1` para la declaración de intención y `FCR-2` para la presentación del `diff` y la evidencia.
6.  **Gestión de Revisiones Canónicas:**
    *   **Baseline (`rev: 0`):** La versión fundamental y estable de un artefacto. Su nombre de archivo no contiene indicadores de revisión.
    *   **Revisiones de Corte (`rev >= 1`):** Modificaciones significativas asociadas a un `Head-Of-Versions` (HOV). Estas DEBEN residir en una subcarpeta `_revisions/REV_<LETRA>/HOV_<DETALLES>/...` para preservar el `baseline` intacto.

## 2. Gramática de Archivos y Rutas (File & Path Grammar)

La estructura de directorios y archivos es canónica y no admite desviaciones.

### Estructura Canónica

```
TFA/
└── <LAYER>/
    └── <LLC>/
        ├── <UTCS-ID>.md                 # Archivo baseline (rev: 0)
        └── _revisions/                  # Directorio para revisiones (rev >= 1)
            └── REV_A/
                └── HOV_MSN1-3_CAD-CAE/
                    └── <UTCS-ID>.md     # Archivo de la revisión A
```

*   **`<LAYER>`:** Una de las capas ontológicas de TFA (e.g., `SYSTEMS`, `COMPONENTS`, `QUBITS`, `STATES`).
*   **`<LLC>`:** El *Layer Logic Code* de dos letras que clasifica el artefacto dentro de la capa.
*   **`<UTCS-ID>`:** El identificador único del artefacto, sin extensión ni letra de revisión.
*   **`_revisions/REV_<LETRA>/`:** Contenedor para una revisión específica (`A`, `B`, `C`...).
*   **`HOV_<MSN_RANGE>_<PHASES>/`:** Directorio que describe el alcance de la revisión, incluyendo el rango de MSN y las fases CAx aplicadas (unidas por guiones).

### Regex de Validación (POSIX ERE)

Esta expresión regular se usa en los sistemas de CI para validar todas las rutas de los archivos `.md`.

```regex
^TFA/(SYSTEMS|STATIONS|COMPONENTS|BITS|QUBITS|ELEMENTS|WAVES|STATES)/[A-Z]{2}/(?:_revisions/REV_[A-Z]/HOV_[A-Z0-9_-]+/)?([A-Z0-9-]{13})\.md$
```

## 3. Plantilla de Front-Matter (UTCS-MI)

Todo archivo `.md` DEBE comenzar con un bloque YAML (`---`) que contenga los siguientes metadatos.

```yaml
---
# -- Bloque de Identificación y Configuración (Siempre presente) --
id: <DOMAIN-PROGRAM-BLOCKS-ID>          # UTCS-MI, 13 campos, inmutable.
rev: <int>                              # 0 para baseline; >= 1 para revisiones.
llc: <SI|DI|SE|CV|CE|CC|CI|CP>          # Layer Logic Code (2 letras).
title: "<Título descriptivo y conciso>"
configuration: baseline                 # Valor fijo para este estándar.
classification: "INTERNAL / EVIDENCE-REQUIRED"
version: "<semver>"                     # Versionado Semántico del contenido.
release_date: <YYYY-MM-DD>
maintainer: "<Equipo o ID de Agente>"

# -- Bloque de Procedencia y Sello Criptográfico (QS) --
provenance:
  policy_hash: "sha256:<HASH_DE_LA_POLÍTICA_APLICADA>"
  model_sha: "sha256:<HASH_DEL_MODELO_GENERADOR>"
  data_manifest_hash: "sha256:<HASH_DEL_MANIFIESTO_DE_DATOS>"
  operator_id: "UTCS:OP:<handle>"
  canonical_hash: "sha256:<HASH_DEL_CONTENIDO_CANÓNICO>"

# -- Bloque de Licenciamiento --
licenses:
  code: "Apache-2.0"
  docs: "CC-BY-4.0"

# -- Metadata de Revisión (Obligatorio si rev >= 1, PROHIBIDO si rev: 0) --
hov:
  msn_range: "MSN1-3"                   # Rango de Manufacturer Serial Numbers afectado.
  phases: ["CAD","CAE","CAI"]           # Array de fases CAx canónicas, en orden.
  label: "MSN1-3 diseño inicial, ingeniería e integración SW/HW"
  bridge: "CB→QB→UE→FE→FWD→QS"         # Puente lógico que justifica la revisión.
  ethics_guard: "MAL-EEM"               # Guardián ético que validó el cambio.
---
```

## 4. Fases HOV (15 CAx Canónicos)

El ciclo de vida de un producto se modela a través de 15 fases `Computer-Aided X` (CAx) canónicas. El campo `hov.phases` DEBE contener un subconjunto de esta lista, en orden cronológico estricto.

**Orden Cronológico Obligatorio:**

1.  `STRATEGY`
2.  `CAX-METHODOLOGY`
3.  `CAB` (Brainstorming, Assessment & Setting)
4.  `CAIR` (Airworthiness & Certification Requirements)
5.  `CAD` (Design)
6.  `CAE` (Engineering)
7.  `CAI` (Embedding HW·SW·AI)
8.  `CAV` (Verification & Validation)
9.  `CAT` (Testing & Treatment)
10. `CAM` (Manufacturing)
11. `CA-PRO` (Production, Prototyping & Procurement)
12. `CAO` (Organization & PLM/PDM)
13. `CAF` (Finance)
14. `CAS0` (Sustainment & Supply)
15. `CAEPOST` (End-of-Life)

**Ejemplo de uso en path:** para un HOV que abarca las fases de Diseño, Ingeniería, Integración y Fabricación, el path sería:

```
_revisions/REV_B/HOV_MSN4_CAD-CAE-CAI-CAM/<UTCS-ID>.md
```

## 5. Códigos de Error de Validación

Los sistemas de CI y linters utilizarán estos códigos para reportar incumplimientos.

*   `[E1001] PathGrammarError`: La ruta del archivo no cumple con la Regex de validación.
*   `[E2001] SchemaError`: El front-matter YAML es inválido o faltan campos obligatorios.
*   `[E2107] HOVNotAllowed`: Un archivo `baseline` (`rev: 0`) contiene el bloque `hov`.
*   `[E2108] HOVMissing`: Un archivo de revisión (`rev >= 1`) no contiene el bloque `hov`.
*   `[E2110] HOVPhasesInvalid`: El array `hov.phases` contiene valores no canónicos o en el orden incorrecto.
*   `[E2111] HOVPathMismatch`: El directorio `HOV_...` en la ruta no se corresponde con los valores de `msn_range` y `phases` del front-matter.
*   `[E6001] ProvenanceDrift`: Uno o más hashes en el bloque `provenance` no coinciden con los valores del `QS blob` asociado.

## 6. Instrucciones de Formato (para Agentes)

*   **Nombres de Archivo:** DEBEN ser exactamente el `UTCS-ID.md` (e.g., `COMP-DI-S0001-A001.md`).
*   **Front-matter:** DEBE ser el primer elemento del archivo, delimitado por `---`.
*   **Títulos:** Usar `#` para el título principal (que debe coincidir con el `title` del front-matter), `##` para secciones normativas, y `###` para subsecciones.
*   **Bloques de Código:** Usar triple backtick (```) con especificador de lenguaje (`yaml`, `regex`, `bash`, etc.) para garantizar el resaltado de sintaxis.
*   **Citas Normativas:** Usar blockquotes (`>`) exclusivamente para citar reglas, estándares o notas críticas.
*   **Listas:** Usar guiones (`-`) para listas no ordenadas. Usar números (`1.`, `2.`) solo si el orden secuencial es imperativo (como en la lista de fases CAx).
*   **Tablas:** Usar el formato estándar de Markdown para datos tabulares.
*   **Glosario:** Todo artefacto complejo DEBE incluir una sección `## Glosario de Acrónimos` al final para definir la terminología específica del documento.

## 7. Plantilla de Commit y Pull Request

Todo commit debe seguir este formato para ser aceptado por el sistema de control de versiones.

```
feat(CAX): Resumen conciso del cambio en el componente

Descripción más detallada de la modificación, el problema que resuelve y el impacto que tiene en el sistema.

FCR-1: <URL a la issue o documento de intención>
FCR-2: <URL a este mismo PR o al diff canónico>
UTCS: <ID completo del artefacto modificado, e.g., COMP-DI-S0001-A001>
Evidence: EVIDENCE/blobs/<sha256_del_qs_blob>.yaml
Signed-off-by: <Nombre del Agente o Contribuidor <email>>
```

## 8. Glosario General de Acrónimos

*   **ASI-T:** Aerospace Super-Intelligence Transformers. Marco rector para la transición industrial sostenible.
*   **CAx:** Computer-Aided X. Conjunto de 15 fases canónicas que modelan el ciclo de vida digital.
*   **FCR:** Follow-up Chain Rules. Procedimiento de cambios en dos pasos (`FCR-1`: intención, `FCR-2`: diff + evidencia).
*   **HOV:** Head-Of-Versions. Metadatos que definen el alcance de una revisión de corte (`rev >= 1`).
*   **LLC:** Layer Logic Code. Código de dos letras que identifica un sub-dominio lógico dentro de una capa TFA.
*   **MAL-EEM:** Master Application Layer — Ethics & Empathy Module. Guardián de ética y resiliencia.
*   **MSN:** Manufacturer Serial Number. Identifica el rango de unidades físicas a las que se aplica un cambio.
*   **QS:** Quantum State / Quantum Seal. Blob criptográfico que sella un artefacto y su evidencia, garantizando su inmutabilidad.
*   **TFA:** Top Final Algorithm / Traceable Federated Architecture. Árbol de directorios canónico que organiza todo el conocimiento.
*   **UIX:** Universal Injection Prompt. El prompt de sistema que sirve como única fuente de verdad para los agentes.
*   **UTCS:** Universal Traceability & Configuration System. Estándar global para identificadores y metadatos.
*   **UTCS-MI:** UTCS Metadata Identifier. El identificador canónico de 13 campos que inicia cada documento.