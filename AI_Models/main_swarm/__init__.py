"""
Main Swarm Router Module

Central hub for routing patient data to appropriate AI prediction models.
"""

from .main_swarm_router import (
    MainSwarmRouter,
    ModelType,
    ModelRequirements,
    CARDIOVASCULAR_REQUIREMENTS,
    DIABETES_REQUIREMENTS,
    get_router,
    route_prediction,
)

__all__ = [
    "MainSwarmRouter",
    "ModelType", 
    "ModelRequirements",
    "CARDIOVASCULAR_REQUIREMENTS",
    "DIABETES_REQUIREMENTS",
    "get_router",
    "route_prediction",
]

__version__ = "1.0.0"
