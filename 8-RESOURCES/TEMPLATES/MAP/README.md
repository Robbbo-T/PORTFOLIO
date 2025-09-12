# MAP (Master Application Program) Templates

MAP templates provide domain-specific application program structures that wire together TFA templates into complete domain applications.

## Structure

Each domain gets a MAP template that includes:
- Domain Interface (DI) API specifications  
- Integration patterns for the domain's TFA layers
- Configuration templates for domain-specific requirements
- Validation and testing frameworks

## Available MAP Templates

Create domain-specific directories as needed:
- `AAA/` - Aerodynamics and Airframes Architectures
- `CQH/` - Cryogenics, Quantum and H2
- `EDI/` - Engineering Data Intelligence  
- `LCC/` - Lifecycle Control
- `PPP/` - Propulsion Power and Performance
- ... (other domain codes)

## Usage

1. Copy the relevant MAP template to your domain
2. Wire the DI APIs to your domain's specific requirements
3. Configure integration with MAL services as needed
4. Validate the complete MAP configuration

See the main 8-RESOURCES README for detailed usage instructions.