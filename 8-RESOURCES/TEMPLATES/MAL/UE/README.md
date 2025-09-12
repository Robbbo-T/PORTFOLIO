# MAL-UE (Unit Element Service)

Shared Unit Element service for typed primitives, unit operations, and safety-checked kernels across all domains.

## Purpose

MAL-UE provides canonical, reusable primitives with type safety and unit validation.

## Key Operations

- `transform` - Geometric and coordinate transformations
- `aggregate` - Data collection and summarization
- `validate_units` - Unit consistency checking and conversion
- Safety-wrapped kernel operations

## Configuration Template

```yaml
mal_ue:
  service_type: "unit_element"
  primitives:
    geometry: ["transform", "project", "intersect"]
    units: ["convert", "validate", "normalize"]
    safety: ["bounds_check", "type_verify", "kernel_wrap"]
  type_system:
    strict_typing: true
    unit_enforcement: true
    safety_wrappers: "mandatory"
  kernels:
    approved_only: true
    safety_certified: true
    performance_verified: true
  
# Integration points
integration:
  all_layers: ["CB", "QB", "FE", "FWD", "QS"]
  type_checking: "compile_time"
```

## Safety Features

- Typed kernel operations with bounds checking
- Unit consistency validation across all operations
- Safety wrapper enforcement for critical calculations

## Usage

Use for all fundamental operations requiring type safety and unit validation in aerospace calculations.