"""Cost + energy + carbon accounting for a run (Feature 26).

Token cost is exact (from usage + a price sheet). Energy/CO2e are **coarse
estimates** (inference energy is workload/hardware-dependent; CodeCarbon-style
factors are approximate) — label them as estimates, never measurements. These
feed the CLEAR "C" (Cost) dimension and the OTel `aobench.cost/energy/co2e`
attributes (ADR 0003).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

# Coarse default: ~kWh per 1k tokens for a mid-size served LLM (order-of-magnitude).
DEFAULT_KWH_PER_1K_TOKENS = 0.0003
# World-average grid intensity (gCO2e/kWh); override per region/facility.
DEFAULT_GRID_INTENSITY_G_PER_KWH = 400.0


def token_cost_usd(
    prompt_tokens: int,
    completion_tokens: int,
    *,
    price_in_per_1k: float,
    price_out_per_1k: float,
) -> float:
    """Exact token cost given a price sheet ($ per 1k tokens)."""
    return round(
        (prompt_tokens / 1000.0) * price_in_per_1k
        + (completion_tokens / 1000.0) * price_out_per_1k,
        6,
    )


def estimate_energy_kwh(
    total_tokens: int, *, kwh_per_1k_tokens: float = DEFAULT_KWH_PER_1K_TOKENS
) -> float:
    """Coarse inference-energy estimate from token count (an estimate, not a measurement)."""
    return round((total_tokens / 1000.0) * kwh_per_1k_tokens, 8)


def estimate_co2e_g(
    energy_kwh: float, *, grid_intensity_g_per_kwh: float = DEFAULT_GRID_INTENSITY_G_PER_KWH
) -> float:
    """Estimated grams CO2e for a given energy draw and grid intensity."""
    return round(energy_kwh * grid_intensity_g_per_kwh, 4)


class RunAccounting(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Optional[float] = None
    energy_kwh: float
    co2e_g: float
    energy_is_estimate: bool = True


def account_run(
    prompt_tokens: int,
    completion_tokens: int,
    *,
    price_in_per_1k: Optional[float] = None,
    price_out_per_1k: Optional[float] = None,
    kwh_per_1k_tokens: float = DEFAULT_KWH_PER_1K_TOKENS,
    grid_intensity_g_per_kwh: float = DEFAULT_GRID_INTENSITY_G_PER_KWH,
) -> RunAccounting:
    """Bundle cost + estimated energy + estimated CO2e for one run."""
    total = prompt_tokens + completion_tokens
    cost = None
    if price_in_per_1k is not None and price_out_per_1k is not None:
        cost = token_cost_usd(
            prompt_tokens, completion_tokens,
            price_in_per_1k=price_in_per_1k, price_out_per_1k=price_out_per_1k,
        )
    energy = estimate_energy_kwh(total, kwh_per_1k_tokens=kwh_per_1k_tokens)
    co2e = estimate_co2e_g(energy, grid_intensity_g_per_kwh=grid_intensity_g_per_kwh)
    return RunAccounting(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
        total_tokens=total, cost_usd=cost, energy_kwh=energy, co2e_g=co2e,
    )
