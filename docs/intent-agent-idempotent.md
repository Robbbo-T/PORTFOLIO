# Intención → Sistema Agente → Estado Idempotente (ISE)
**Norma canónica para agentes idempotentes en TFA/AQUA**

> Entre la **Intención** (qué) y el **Estado Idempotente** (resultado) se sitúa el **Sistema Agente** (cómo), el medio de *consecutio* que observa, compara y actúa para cerrar el delta de forma segura y repetible.

[Quantum–Classical Bridge](../docs/quantum-classical-bridge.md) · [TFA Architecture](../8-RESOURCES/TFA-ARCHITECTURE.md) · [Plantillas TFA](../8-RESOURCES/TEMPLATES/) · [AQUA App](../services/aqua-webhook/README.md) · [AQUA-OS PRO](../services/aqua-os-pro/AQUA-OS-PRO-SPEC.md)

---

## 1. Resumen
- **Intención**: objetivo **declarativo** del estado final.
- **Sistema Agente (SA)**: lazo **Observar → Comparar → Actuar (OCA)** que ejecuta solo el **delta** necesario.
- **Estado Idempotente**: realidad estabilizada; ejecuciones repetidas no producen cambios.

**Principio**: Si la Intención ya coincide con la Realidad, el SA **no actúa**.

---

## 2. Mapeo ISE ↔ TFA/MAP/MAL
- **Intención**  
  - Se materializa como **manifiestos canónicos** TFA en `TFA/*/META/` (p. ej. FE/QS/CE).  
  - Puede vivir en **FE** (orquestaciones multi-elemento) o **QS** (estados medidos/simulados).  
  - Firmas **EIP-712** para Intenciones de Federación (FE).

- **Sistema Agente (medio de consecutio)**  
  - **MAL-\***: servicios horizontales (CB/QB/UE/FE/FWD/QS) que ejecutan el delta.  
  - **MAP-\***: control de dominio (AAA, PPP, IIS, …) que llama a MAL-\* según políticas.  
  - **AQUA**: valida manifiestos, verifica FE y **desencadena** anclaje UTCS/TEKNIA vía CI.

- **Estado Idempotente**  
  - Artefactos estabilizados en `TFA/STATES/QS/` o configuraciones efectivas en `TFA/*/*`.  
  - Evidencia: pruebas, logs, anclaje **UTCS**, eventos de auditoría AQUA.

---

## 3. Lazo OCA (Observe–Compare–Act)
```mermaid
flowchart LR
  I[Intención (manifest)] --> C{Comparar\nIntención vs Realidad}
  R[Realidad actual] --> C
  C -- Delta = 0 --> N[No acción]
  C -- Delta > 0 --> A[Actuar (transacciones idempotentes)]
  A --> V[Verificar & Registrar]
  V --> R2[Realidad actualizada]
  R2 --> C

Invariantes de Idempotencia
1. Conmutatividad parcial: re-ejecutar acciones no cambia el resultado final.
2. Efecto nulo en convergencia: si Delta=0, no hay efectos laterales.
3. Determinismo observable: misma Intención + misma Realidad ⇒ mismo resultado.
4. Prueba de fijación: la segunda pasada del lazo no produce cambios materiales.
```

⸻

## 4. Contratos (normativos)

### 4.1 Intención (manifest mínimo)

```yaml
artifact_id: "uuid-v4 | nombre-canonico"
llc_code: "FE"           # o QS/CE/…
domain: "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES"
goal:                    # estado deseado (declarativo)
  config: { key: value }
  constraints: [S1000D, MBSE]
timestamp: "RFC3339"
version: "1.0.0"
provenance: { repo_paths: [...], cids: [...] }
fe_signatures:
  - signer: "0xSigner"
    signature: "0x..."
    eip712: { /* types/domain */ }
canonical_hash: "0x..."   # keccak256(JSON canónico)
```

**Reglas**
   •   El goal es declarativo (no procedimental).
   •   canonical_hash debe verificar; la CI bloquea si no.
   •   FE requiere ≥1 firma válida (EIP-712).

### 4.2 Sistema Agente (contrato MAL)

```
agent:
  name: "MAL-FE"
  policy:
    safety: ["dry-run-default", "bounded-rollback", "rate-limit"]
    retries: { max: 2, jitter_ms: 150 }
    quorum: "FE.quorum >= 2/3"
  actions:
    - name: "ensure:config"
      idempotent_key: "domain/llc/config@hash"
      preconditions: ["Delta>0"]
      effect: "mutación mínima que reduce Delta"
  observability:
    emit: ["artifact.validated","fe.signature.verified","delta.applied","state.converged"]
```

### 4.3 Estado Idempotente (evidencias)
   •   tests/ que demuestren segunda pasada nula.
   •   events/ con state.converged.
   •   UTCS anchor (testnet→mainnet) y hash canónico en cadena.

⸻

## 5. Patrones de diseño
   •   Delta mínimo aplicable (DMA): dividir objetivos en mutaciones atómicas con idempotent_key.
   •   Capas protectoras: dry-run, límites de radio de acción, rate-limit.
   •   Lecturas fuertes antes de actuar (evitar TOCTTOU).
   •   Compensaciones declarativas (no “deshacer” implícito).
   •   Detección de drift continua (OPTIMO-DT ↔ QS).

⸻

## 6. Ejemplos

### 6.1 Config línea única (archivo)

Intención: “STATUS=ACTIVE existe exactamente una vez”
Agente: MAL-CB (filesystem)
Estado: archivo converge; re-ejecución no cambia bytes.

### 6.2 Kubernetes (controlador)

Intención: replicas: 3
Agente: controlador MAP-IIS → MAL-UE
Estado: Deployment converge; reconciliaciones posteriores no cambian recursos.

### 6.3 AQUA-OS PRO (rutas)

Intención: “fleet schedule ≤ SLA y rutas válidas”
Agente: MAL-FWD/MAL-FE con PRO orquestador
Estado: plan vigente firmado (FE) + utcs.anchor.requested emitido.

⸻

## 7. CI/CD (validación automática)
   •   Validar JSON Schema + canonical_hash.
   •   Simulación dry-run: Delta esperado = 0 en segunda pasada.
   •   Condiciones de merge: check_run:success + pruebas de idempotencia verdes.
   •   Para FE con utcs_candidate: disparar anchor_utcs (testnet).

⸻

## 8. SLOs de agentes
   •   Convergencia: p95 < X s (por dominio).
   •   Delta cero: ≥ 99.9% en re-ejecución inmediata.
   •   Seguridad: 0 incidentes de “sobre-aplicación” por 10k acciones.
   •   Trazabilidad: 100% eventos state.converged correlables a intención.

⸻

## 9. Plantillas y enlaces
   •   Esquemas: 8-RESOURCES/TEMPLATES/.../artifact-manifest.schema.json
   •   FE/QS: 8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/ELEMENTS/FE/ · .../STATES/QS/
   •   Agentes: services/aqua-webhook/, services/aqua-os-pro/
   •   EIP-712: docs/eip712.md

⸻

## 10. Checklist de calidad (pre-merge)
   •   Manifiesto válido y firmado (si FE)
   •   canonical_hash verificado
   •   Pruebas de segunda pasada = sin cambios
   •   Eventos de auditoría presentes
   •   (Opcional) utcs_candidate preparado para anclaje

⸻

## 11. Glosario mínimo
   •   Medio de consecutio: mecanismo que realiza la transición desde la intención al estado final (el Sistema Agente).
   •   Idempotencia: aplicar una instrucción múltiples veces produce el mismo estado final.
   •   OCA: ciclo Observar–Comparar–Actuar.

⸻
