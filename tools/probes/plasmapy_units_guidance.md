## Units and particle inputs

- Follow the [coding guide](docs/contributing/coding_guide.rst); keep physics
  calculations in SI units and preserve `astropy.units.Quantity` objects.
  Convert explicitly with `.to(...)` / `.to_value(...)` before extracting
  numbers at a numerical-kernel boundary; `.value` alone does not convert units.
- Electron-volts are energy units, not temperature units. Where an API accepts
  energy per particle as temperature, use `u.temperature_energy()` explicitly
  (the relation is `E = k_B T`), and calculate with kelvin internally. Do not
  relabel an eV value as kelvin or enable equivalencies globally.

```python
import astropy.units as u

temperature = (1 * u.eV).to(u.K, equivalencies=u.temperature_energy())
```

- Use `Particle` for a known particle, element, isotope, or ion; `ParticleList`
  for collections; and `CustomParticle` for explicitly supplied mass/charge.
  `ParticleLike` is an input type annotation, not a constructor. State the
  isotope and charge when the calculation needs them; do not guess missing data.
  See the [particle guide](docs/particles/index.rst) for supported representations.

```python
from plasmapy.particles import CustomParticle, Particle, ParticleList

helium_ion = Particle("He-4 +1")
species = ParticleList(["p+", "e-"])
custom = CustomParticle(mass=1e-26 * u.kg, charge=1e-19 * u.C)
```

- Use `@particle_input` with `ParticleLike` / `ParticleListLike` annotations to
  convert supported inputs into particle objects. Specify categorization
  restrictions only when required by the physics. A parameter named `ion` does
  not by itself require nonzero charge; use the documented `require` option.
- Use `@validate_quantities` with unit annotations to convert/check quantities;
  add parameter-specific restrictions such as nonnegative temperature only
  where physically appropriate. Type annotations alone do not validate units.
  Put `@particle_input` outside `@validate_quantities` on instance methods.
  Consult each decorator's documentation before decorating setters or variadic APIs.

```python
from plasmapy.particles import ParticleLike, particle_input
from plasmapy.utils.decorators import validate_quantities

@particle_input
@validate_quantities(
    T={"can_be_negative": False, "equivalencies": u.temperature_energy()}
)
def checked_inputs(T: u.Quantity[u.K], particle: ParticleLike):
    return T, particle
```

- Test equivalent unit representations, scalar/array inputs where supported,
  and rejected units/particle categories. Do not change a public function's
  accepted inputs, broadcasting, or missing-data behavior merely to simplify
  validation; follow the existing API contract and nearby tests.

