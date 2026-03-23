from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import (
    EngineerProfileResponse,
    EngineerSetupRequest,
    EngineerUpdateRequest,
)
from backend.db.crud import create_engineer, get_engineer
from backend.db.database import get_db

router = APIRouter(prefix="/engineer", tags=["engineer"])


@router.post("/setup", response_model=EngineerProfileResponse)
async def setup_engineer(
    body: EngineerSetupRequest,
    db: AsyncSession = Depends(get_db),
) -> EngineerProfileResponse:
    engineer = await create_engineer(
        db, name=body.name, role_track=body.role_track, skill_level=body.skill_level
    )
    return EngineerProfileResponse(
        id=engineer.id,
        name=engineer.name,
        role_track=engineer.role_track,
        skill_level=engineer.skill_level,
        total_xp=engineer.total_xp,
        total_sessions=engineer.total_sessions,
    )


@router.get("/profile", response_model=EngineerProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
) -> EngineerProfileResponse:
    engineer = await get_engineer(db)
    if not engineer:
        raise HTTPException(status_code=404, detail="No engineer profile found. Run POST /engineer/setup first.")
    return EngineerProfileResponse(
        id=engineer.id,
        name=engineer.name,
        role_track=engineer.role_track,
        skill_level=engineer.skill_level,
        total_xp=engineer.total_xp,
        total_sessions=engineer.total_sessions,
    )


@router.put("/profile", response_model=EngineerProfileResponse)
async def update_profile(
    body: EngineerUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> EngineerProfileResponse:
    engineer = await get_engineer(db)
    if not engineer:
        raise HTTPException(status_code=404, detail="No engineer profile found.")

    if body.name is not None:
        engineer.name = body.name
    if body.role_track is not None:
        engineer.role_track = body.role_track
    if body.skill_level is not None:
        engineer.skill_level = body.skill_level

    await db.commit()
    await db.refresh(engineer)

    return EngineerProfileResponse(
        id=engineer.id,
        name=engineer.name,
        role_track=engineer.role_track,
        skill_level=engineer.skill_level,
        total_xp=engineer.total_xp,
        total_sessions=engineer.total_sessions,
    )
