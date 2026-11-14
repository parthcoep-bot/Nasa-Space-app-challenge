"""
flarex.physics
==============

Combustion transport relations for the Physics Lab module.

THE ONE RULE THIS FILE ENFORCES
-------------------------------
A dimensionless group computed from assumed inputs is a decoration, not a
measurement. Every function here *requires* its inputs explicitly and
returns a `PhysicsResult` that carries the full input set and an
`assumptions` list. There are no default property values. Calling
`grashof()` without a length scale raises; it does not quietly substitute
1 cm.

WHY BUOYANCY SUPPRESSION CHANGES THE PROBLEM
--------------------------------------------
On Earth a flame heats the surrounding gas, the density drops, and gravity
drives that gas upward. The resulting buoyant flow is not a small
correction: for the PMMA rod geometry in these experiments the
flame-induced buoyant velocity is of order 30 cm/s (Link et al. 2018), far
larger than the 0.4-8 cm/s forced flows used in the microgravity tests and
larger than the 0.1 m/s-scale ventilation flows in a spacecraft cabin.

Gravity enters the momentum equation through the body-force term, so the
buoyancy scale goes as Gr ~ g*beta*dT*L^3/nu^2, i.e. linearly in g. In
free fall the effective g is of order 1e-6 g_earth, so Gr collapses by
roughly six orders of magnitude and the buoyant velocity scale
u_b ~ sqrt(g*beta*dT*L) collapses by about three. What is left to move
oxidiser to the reaction zone and heat away from it is forced convection
from the ventilation system, molecular diffusion, and radiation.

Two consequences follow, and both are visible in the data:

  1. Oxygen supply becomes transport-limited at low flow. Below a limiting
     flow velocity the flame cannot be sustained. Link et al. observed no
     spread below about 0.6 cm/s in their tests.

  2. Radiative loss stops being negligible. With a thick boundary layer,
     a standoff flame and no buoyant refreshment, surface re-radiation can
     dominate the solid-phase energy balance and quench the flame. This is
     the radiative / oxygen-transport-limited extinction branch.

These are *published* results (claim level L2); FLARE-X measures features
consistent with them (L3) and derives indices from them (L4).

TEXTBOOK GROUNDING
------------------
  Turns, "An Introduction to Combustion" - diffusion flame structure,
      conserved scalar formulation, the role of transport time scales.
  Glassman, Yetter & Glumac, "Combustion" - soot formation and the
      luminosity of diffusion flames; the physical basis for reading a
      yellow-to-blue shift as a change in the soot contribution.
  Law, "Combustion Physics" - Damkohler-number extinction theory and the
      S-curve; the framework in which a flame blows off or quenches when
      the residence time falls below the chemical time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import math

__all__ = [
    "PhysicsResult",
    "MissingInput",
    "reynolds",
    "grashof",
    "richardson",
    "peclet",
    "lewis",
    "damkohler",
    "buoyant_velocity_scale",
    "diffusion_time",
    "convection_time",
    "G_EARTH",
    "TYPICAL_ISS_G_LEVEL",
]

G_EARTH = 9.80665                 # m/s^2, standard gravity (defined constant)
TYPICAL_ISS_G_LEVEL = 1e-6        # order of magnitude only; see note in docstring


class MissingInput(ValueError):
    """Raised when a group is requested without the data to compute it."""


@dataclass
class PhysicsResult:
    name: str
    value: float
    inputs: dict[str, Any]
    formula: str
    assumptions: list[str] = field(default_factory=list)
    interpretation: str = ""

    def render(self) -> str:
        lines = [f"{self.name} = {self.value:.4g}",
                 f"  formula: {self.formula}",
                 "  inputs:  " + ", ".join(f"{k}={v}" for k, v in self.inputs.items())]
        if self.assumptions:
            lines.append("  assumptions (stated, not hidden):")
            lines += [f"    - {a}" for a in self.assumptions]
        if self.interpretation:
            lines.append(f"  reading: {self.interpretation}")
        return "\n".join(lines)


def _require(**kwargs: Any) -> None:
    missing = [k for k, v in kwargs.items() if v is None]
    if missing:
        raise MissingInput(
            "Cannot compute this group without: " + ", ".join(missing) +
            ". FLARE-X does not substitute assumed values for measured ones. "
            "Supply the value from the experiment record, or leave the group "
            "unreported."
        )


def reynolds(velocity_m_s: float | None = None,
             length_m: float | None = None,
             kinematic_viscosity_m2_s: float | None = None,
             assumptions: list[str] | None = None) -> PhysicsResult:
    """Re = u L / nu — forced inertia against viscous diffusion."""
    _require(velocity_m_s=velocity_m_s, length_m=length_m,
             kinematic_viscosity_m2_s=kinematic_viscosity_m2_s)
    re = velocity_m_s * length_m / kinematic_viscosity_m2_s
    interp = ("Well below 1 - viscous, creeping. Order 1-100 - laminar boundary "
              "layer regime, which is where these low-speed duct flows sit.")
    return PhysicsResult("Reynolds number", re,
                         {"u [m/s]": velocity_m_s, "L [m]": length_m,
                          "nu [m^2/s]": kinematic_viscosity_m2_s},
                         "Re = u*L/nu", assumptions or [], interp)


def grashof(g_m_s2: float | None = None,
            beta_1_K: float | None = None,
            delta_T_K: float | None = None,
            length_m: float | None = None,
            kinematic_viscosity_m2_s: float | None = None,
            assumptions: list[str] | None = None) -> PhysicsResult:
    """Gr = g beta dT L^3 / nu^2 — buoyant against viscous forces.

    `g_m_s2` must be supplied explicitly. The whole point of this project is
    that g is the independent variable, so defaulting it would defeat the
    analysis. For a microgravity case pass the measured or quoted residual
    acceleration and say so in `assumptions`.
    """
    _require(g_m_s2=g_m_s2, beta_1_K=beta_1_K, delta_T_K=delta_T_K,
             length_m=length_m, kinematic_viscosity_m2_s=kinematic_viscosity_m2_s)
    gr = (g_m_s2 * beta_1_K * delta_T_K * length_m ** 3) / (kinematic_viscosity_m2_s ** 2)
    interp = ("Gr scales linearly with g. Between 1 g and a 1e-6 g environment "
              "this term falls by about six orders of magnitude, which is why "
              "buoyant transport stops being the dominant supply mechanism.")
    return PhysicsResult("Grashof number", gr,
                         {"g [m/s^2]": g_m_s2, "beta [1/K]": beta_1_K,
                          "dT [K]": delta_T_K, "L [m]": length_m,
                          "nu [m^2/s]": kinematic_viscosity_m2_s},
                         "Gr = g*beta*dT*L^3/nu^2", assumptions or [], interp)


def richardson(grashof_number: float | None = None,
               reynolds_number: float | None = None,
               assumptions: list[str] | None = None) -> PhysicsResult:
    """Ri = Gr / Re^2 — the mixed-convection parameter.

    Ri >> 1 : buoyancy-dominated (a normal-gravity upward flame)
    Ri << 1 : forced-flow-dominated (the microgravity duct case)
    Ri ~ 1  : mixed convection, where 1-g and microgravity data can be
              compared on common ground.
    """
    _require(grashof_number=grashof_number, reynolds_number=reynolds_number)
    if reynolds_number == 0:
        raise MissingInput("Re = 0 gives an undefined Richardson number.")
    ri = grashof_number / reynolds_number ** 2
    interp = ("Ri >> 1 buoyancy-dominated; Ri << 1 forced-flow-dominated. This is "
              "the parameter used in the literature to place normal-gravity "
              "reduced-pressure experiments alongside microgravity data.")
    return PhysicsResult("Richardson number", ri,
                         {"Gr": grashof_number, "Re": reynolds_number},
                         "Ri = Gr/Re^2", assumptions or [], interp)


def peclet(velocity_m_s: float | None = None,
           length_m: float | None = None,
           diffusivity_m2_s: float | None = None,
           assumptions: list[str] | None = None) -> PhysicsResult:
    """Pe = u L / D — advective against diffusive transport."""
    _require(velocity_m_s=velocity_m_s, length_m=length_m,
             diffusivity_m2_s=diffusivity_m2_s)
    pe = velocity_m_s * length_m / diffusivity_m2_s
    interp = ("Pe < 1 means molecular diffusion moves oxidiser to the flame faster "
              "than the imposed flow does. Low-speed microgravity flames can sit in "
              "this regime, which has no terrestrial counterpart at these scales "
              "because buoyancy keeps Pe high.")
    return PhysicsResult("Peclet number", pe,
                         {"u [m/s]": velocity_m_s, "L [m]": length_m,
                          "D [m^2/s]": diffusivity_m2_s},
                         "Pe = u*L/D", assumptions or [], interp)


def lewis(thermal_diffusivity_m2_s: float | None = None,
          mass_diffusivity_m2_s: float | None = None,
          assumptions: list[str] | None = None) -> PhysicsResult:
    """Le = alpha / D — heat against species diffusion."""
    _require(thermal_diffusivity_m2_s=thermal_diffusivity_m2_s,
             mass_diffusivity_m2_s=mass_diffusivity_m2_s)
    le = thermal_diffusivity_m2_s / mass_diffusivity_m2_s
    interp = ("Le departing from 1 makes the flame temperature depend on the "
              "balance between heat conducted away and reactant diffused in, "
              "which shifts extinction limits.")
    return PhysicsResult("Lewis number", le,
                         {"alpha [m^2/s]": thermal_diffusivity_m2_s,
                          "D [m^2/s]": mass_diffusivity_m2_s},
                         "Le = alpha/D", assumptions or [], interp)


def damkohler(flow_time_s: float | None = None,
              chemical_time_s: float | None = None,
              assumptions: list[str] | None = None) -> PhysicsResult:
    """Da = t_flow / t_chem — residence time against reaction time.

    This is the extinction parameter of the classical S-curve (Law,
    "Combustion Physics"): a flame quenches when the residence time falls
    below what the chemistry needs.

    Honest caveat, and it matters: t_chem cannot be extracted from a video.
    It requires a kinetic mechanism and a flame temperature. FLARE-X exposes
    this function for the Physics Lab so a user can enter values from the
    literature and see the consequence; it never computes Da from imagery.
    """
    _require(flow_time_s=flow_time_s, chemical_time_s=chemical_time_s)
    if chemical_time_s <= 0:
        raise MissingInput("Chemical time must be positive.")
    da = flow_time_s / chemical_time_s
    interp = ("Da >> 1 chemistry keeps up and the flame is transport-controlled. "
              "Da approaching order 1 is the extinction branch. Both blow-off at "
              "high flow and quenching at low flow can be read as Da falling "
              "toward the limit, for different reasons.")
    return PhysicsResult("Damkohler number", da,
                         {"t_flow [s]": flow_time_s, "t_chem [s]": chemical_time_s},
                         "Da = t_flow/t_chem",
                         (assumptions or []) + [
                             "t_chem is a literature or model input, never derived "
                             "from image data by FLARE-X."],
                         interp)


def buoyant_velocity_scale(g_m_s2: float | None = None,
                           beta_1_K: float | None = None,
                           delta_T_K: float | None = None,
                           length_m: float | None = None,
                           assumptions: list[str] | None = None) -> PhysicsResult:
    """u_b ~ sqrt(g beta dT L) — the natural-convection velocity scale.

    Order-of-magnitude only. It is included because it makes the central
    point of the project quantitative: reducing g by six orders of magnitude
    reduces u_b by three, which is what moves a flame out of the
    buoyancy-dominated regime entirely.
    """
    _require(g_m_s2=g_m_s2, beta_1_K=beta_1_K, delta_T_K=delta_T_K, length_m=length_m)
    ub = math.sqrt(max(g_m_s2 * beta_1_K * delta_T_K * length_m, 0.0))
    return PhysicsResult("Buoyant velocity scale", ub,
                         {"g [m/s^2]": g_m_s2, "beta [1/K]": beta_1_K,
                          "dT [K]": delta_T_K, "L [m]": length_m},
                         "u_b ~ sqrt(g*beta*dT*L)",
                         (assumptions or []) + [
                             "Scaling estimate, not a solution of the momentum "
                             "equation. Prefactors of order unity are omitted."],
                         "Compare against the imposed duct velocity to decide "
                         "whether the case is buoyancy- or forced-flow-dominated.")


def diffusion_time(length_m: float | None = None,
                   diffusivity_m2_s: float | None = None) -> PhysicsResult:
    _require(length_m=length_m, diffusivity_m2_s=diffusivity_m2_s)
    t = length_m ** 2 / diffusivity_m2_s
    return PhysicsResult("Diffusion time", t,
                         {"L [m]": length_m, "D [m^2/s]": diffusivity_m2_s},
                         "t_D = L^2/D", [],
                         "How long molecular diffusion needs to cross the flame "
                         "standoff. In microgravity this can be the rate-limiting "
                         "step for oxygen supply.")


def convection_time(length_m: float | None = None,
                    velocity_m_s: float | None = None) -> PhysicsResult:
    _require(length_m=length_m, velocity_m_s=velocity_m_s)
    if velocity_m_s <= 0:
        raise MissingInput("Convection time is undefined for zero velocity; in a "
                           "quiescent microgravity environment transport is "
                           "diffusion-limited and t_D should be used instead.")
    t = length_m / velocity_m_s
    return PhysicsResult("Convection time", t,
                         {"L [m]": length_m, "u [m/s]": velocity_m_s},
                         "t_c = L/u", [],
                         "Residence time of oxidiser over the flame; the numerator "
                         "of the Damkohler number.")
