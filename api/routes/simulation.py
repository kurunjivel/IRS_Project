"""
Simulation API route handler — Phase 1.3 What-If Career Scenario Simulator.
"""

import logging
from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user
from api.schemas.simulation import SimulationRequest, SimulationResponse
from services.simulation_service import SimulationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post(
    "/what-if",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run What-If career scenario simulation",
    description="Simulate skill upgrades, certification completions, projects, and experience without altering database state.",
)
def run_simulation(
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user),
) -> SimulationResponse:
    """Execute What-If scenario simulation."""
    if request.employee_id is None:
        request.employee_id = current_user.get("employee_id", 1)

    logger.info("API POST /simulation/what-if requested for employee %s", request.employee_id)
    service = SimulationService()
    result = service.simulate(request)
    return SimulationResponse.model_validate(result)
