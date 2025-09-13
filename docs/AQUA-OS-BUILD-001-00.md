Módulo de Datos Técnicos: Procedimiento de Compilación y Despliegue del Kernel de AQUA OS
DMC (Data Module Code): AQUA-OS-BUILD-001-00 Título: Procedimiento de Compilación y Despliegue del Kernel de AQUA OS Sistema / Subsistema: AQUA OS / Sistema de Compilación (Build System) Fecha de Emisión: 2025-09-13 Versión: 1.0
1. Propósito y Alcance
Este documento describe el procedimiento para utilizar el script Build_aqua_os_kernel.py. Esta herramienta gestiona el ciclo de vida completo del kernel de AQUA OS, incluyendo la creación del esqueleto del proyecto, la compilación idempotente de artefactos, el despliegue en diversos entornos de ejecución y la ejecución de pruebas de validación (smoke tests).
El script está diseñado para ser la herramienta de línea de comandos (CLI) de referencia para los ingenieros de sistemas y los pipelines de Integración Continua (CI), garantizando la trazabilidad y la reproducibilidad desde la configuración de diseño hasta el despliegue operativo.
2. Prerrequisitos
Antes de utilizar el script, asegúrese de que el entorno cumple con los siguientes requisitos:
•Software Principal:
•Python 3.11 o superior.
•Dependencias de Python: pycryptodome (recomendado para hashing Keccak-256).
•Entorno de Contenedores (para despliegue clásico):
•Docker Engine.
•Herramientas de Kubernetes (kubectl, helm) si se utiliza el runtime k8s.
•SDKs Cuánticos (para desarrollo y pruebas cuánticas):
•Qiskit
•Cirq
•Braket
Se puede verificar la configuración del entorno utilizando el comando info.
3. Descripción del Proceso
El script opera sobre un archivo de configuración central, aqua.config.json, que define los perfiles, los objetivos y las políticas del proyecto. La lógica principal se basa en dos conceptos clave:
•Canonicalización Determinista: Todas las configuraciones se convierten a un formato JSON canónico (claves ordenadas, sin espacios innecesarios) antes de cualquier operación. Esto asegura que la misma configuración siempre produce la misma representación en bytes.
•Idempotencia Basada en Hash: El script calcula un hash criptográfico (Keccak-256 o fallback) de la configuración canónica. Las operaciones de build solo se ejecutan si el hash actual difiere del último hash almacenado en .aqua/state.json, evitando compilaciones redundantes.
4. Procedimientos Operativos
A continuación se detallan los comandos disponibles.
4.1. info - Diagnóstico del Entorno
Muestra información sobre el entorno de ejecución, incluyendo la versión de Python, la pila de contenedores detectada, los SDKs cuánticos disponibles y el resultado de una prueba de hashing.
python Build_aqua_os_kernel.py info 
4.2. scaffold - Creación del Esqueleto del Proyecto
Crea la estructura de directorios y archivos inicial para un proyecto AQUA OS en la ruta especificada.
•aqua.config.json: Archivo de configuración principal.
•Dockerfile: Definición para el contenedor del runtime clásico.
•k8s/deployment.yaml: Manifiesto de despliegue para Kubernetes.
•.aqua/state.json: Archivo de estado para operaciones idempotentes.
•.gitignore: Archivo estándar para ignorar artefactos de compilación.
<!-- end list -->
python Build_aqua_os_kernel.py scaffold --path ./mi_proyecto_aqua 
4.3. build - Compilación de Artefactos
Compila los artefactos del kernel basados en el perfil (--profile) y el objetivo (--target) seleccionados. La operación es idempotente.
•--apply: Si se especifica, ejecuta acciones con efectos secundarios, como la construcción de la imagen Docker (docker build).
<!-- end list -->
python Build_aqua_os_kernel.py build --config ./mi_proyecto_aqua/aqua.config.json --target both --profile AIR --apply 
Resultado: Genera un directorio dist/ con los artefactos de compilación y, si se usa --apply, una imagen Docker local aqua-os:latest.
4.4. deploy - Despliegue en un Entorno de Ejecución
Despliega el kernel compilado en el entorno de ejecución (--runtime) especificado.
•--apply: Ejecuta los comandos de despliegue. Si no se especifica, solo los muestra (dry-run).
<!-- end list -->
# Ejemplo de despliegue en Docker python Build_aqua_os_kernel.py deploy --config ./mi_proyecto_aqua/aqua.config.json --target classical --runtime docker --apply  # Ejemplo de despliegue en Kubernetes (dry-run) python Build_aqua_os_kernel.py deploy --config ./mi_proyecto_aqua/aqua.config.json --target classical --runtime k8s 
4.5. test - Ejecución de Pruebas
Ejecuta suites de pruebas predefinidas. Actualmente, solo está disponible la suite smoke.
•--quantum-backend: Permite seleccionar el backend para las pruebas cuánticas (simulador por defecto, Qiskit, Cirq, etc.).
<!-- end list -->
python Build_aqua_os_kernel.py test --config ./mi_proyecto_aqua/aqua.config.json --suite smoke --quantum-backend qiskit 
Resultado: Ejecuta un circuito de estado de Bell y muestra los resultados de la medición.
4.6. clean - Limpieza de Artefactos
Elimina los directorios y archivos generados por el proceso de compilación (.aqua, dist, __pycache__).
python Build_aqua_os_kernel.py clean --path ./mi_proyecto_aqua 
5. Flujo de Trabajo Integrado (CI/CD)
El script está optimizado para su uso en pipelines de CI/CD. Un flujo de trabajo típico sería:
```
graph TD     A[Git Push en repo] --> B{¿Configuración modificada?};     B --> |Sí| C[build --apply];     B --> |No| G[Finalizar - Idempotente];     C --> D[test --suite smoke];     D --> E{¿Tests OK?};     E --> |Sí| F[deploy --apply];     E --> |No| H[Notificar Fallo];     F --> G;     H --> G;      style A fill:#e6f2ff,stroke:#0b3d91,stroke-width:2px     style C fill:#d5f5e3,stroke:#27ae60,stroke-width:2px     style D fill:#d5f5e3,stroke:#27ae60,stroke-width:2px     style F fill:#d5f5e3,stroke:#27ae60,stroke-width:2px     style H fill:#fadedb,stroke:#c0392b,stroke-width:2px ```
1-CAX-METHODOLOGY/Activación: Un git push activa el pipeline.
2-DOMAINS-LEVELS/Compilación: El comando build se ejecuta. Gracias a la idempotencia, solo actuará si hay cambios relevantes en aqua.config.json.
3-PROJECTS-USE-CASES/Prueba: El comando test valida la integridad del build, incluyendo la conectividad con los backends cuánticos.
4-RESEARCH-DEVELOPMENT/Despliegue: Si las pruebas son exitosas, el comando deploy actualiza el entorno correspondiente (ej. staging o producción).
6. Notas de Implementación
•El script incluye un fallback a sha256 si no se encuentra una implementación de keccak256 o sha3_256, aunque se recomienda la primera para compatibilidad con ecosistemas como Ethereum.
•El docstring del script menciona explícitamente la necesidad de extender la funcionalidad con "UTCS/FE hooks", indicando que la seguridad y la federación deben ser integradas a través de extensiones personalizadas.
