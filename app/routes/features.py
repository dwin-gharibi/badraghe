from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import require_roles, get_current_user


router = APIRouter(prefix="/features")

class FeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None

class FeatureUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

@router.get("/", response_model=List[dict])
async def get_all_features():
    await connect_db()
    features = await execute_query(
        "SELECT id, name, description FROM features",
        fetch_all=True
    )
    await close_db()
    return features

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature: FeatureCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    try:
        await connect_db()
        feature_id = await execute_query(
            """
            INSERT INTO features (name, description)
            VALUES (%s, %s)
            """,
            (feature.name, feature.description),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"feature_id": feature_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/assign-to-train", status_code=status.HTTP_200_OK)
async def assign_feature_to_train(
    train_id: int,
    feature_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    train = await execute_query(
        "SELECT 1 FROM train_details WHERE id = %s",
        (train_id,),
        fetch_one=True
    )
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    feature = await execute_query(
        "SELECT 1 FROM features WHERE id = %s",
        (feature_id,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    try:
        await execute_query(
            "INSERT IGNORE INTO train_features (train_id, feature_id) VALUES (%s, %s)",
            (train_id, feature_id),
            commit=True
        )
        await close_db()
        return {"message": "Feature assigned to train"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/assign-to-plane", status_code=status.HTTP_200_OK)
async def assign_feature_to_train(
    train_id: int,
    feature_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    train = await execute_query(
        "SELECT 1 FROM plane_details WHERE id = %s",
        (train_id,),
        fetch_one=True
    )
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plain not found"
        )
    
    feature = await execute_query(
        "SELECT 1 FROM features WHERE id = %s",
        (feature_id,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    try:
        await execute_query(
            "INSERT IGNORE INTO plane_features (plain_id, feature_id) VALUES (%s, %s)",
            (train_id, feature_id),
            commit=True
        )
        await close_db()
        return {"message": "Feature assigned to plain"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/assign-to-bus", status_code=status.HTTP_200_OK)
async def assign_feature_to_train(
    train_id: int,
    feature_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    train = await execute_query(
        "SELECT 1 FROM bus_details WHERE id = %s",
        (train_id,),
        fetch_one=True
    )
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found"
        )
    
    feature = await execute_query(
        "SELECT 1 FROM features WHERE id = %s",
        (feature_id,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    try:
        await execute_query(
            "INSERT IGNORE INTO bus_features (bus_id, feature_id) VALUES (%s, %s)",
            (train_id, feature_id),
            commit=True
        )
        await close_db()
        return {"message": "Feature assigned to bus"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{id}", response_model=dict)
async def get_feature(id: int):
    await connect_db()
    feature = await execute_query(
        "SELECT id, name, description FROM features WHERE id = %s",
        (id,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    await close_db()
    return feature

@router.patch("/{id}", status_code=200)
async def update_feature(
    id: int,
    feature_data: FeatureUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    update_fields = []
    values = []

    await connect_db()

    for field, value in feature_data.dict(exclude_none=True).items():
        update_fields.append(f"{field} = %s")
        values.append(value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(id)

    await execute_query(
        f"UPDATE features SET {', '.join(update_fields)} WHERE id = %s",
        tuple(values),
        commit=True
    )
    await close_db()
    return {"message": "Feature updated successfully"}

@router.delete("/{id}", status_code=204)
async def delete_feature(
    id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    await execute_query(
        "DELETE FROM features WHERE id = %s",
        (id,),
        commit=True
    )
    await close_db()