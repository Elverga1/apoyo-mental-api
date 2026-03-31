# backend/routers/assessments.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models.models import User, Assessment
from ..schemas.schemas import AssessmentCreate, AssessmentResponse
from ..auth.auth import get_current_user

router = APIRouter(prefix="/assessments", tags=["Evaluaciones"])

@router.post("", response_model=AssessmentResponse)
def save_assessment(
    assessment: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Guardar resultado de evaluación (PHQ-9 o GAD-7)"""
    db_assessment = Assessment(
        user_id=current_user.id,
        type=assessment.type,
        score=assessment.score,
        severity=assessment.severity,
        answers=json.dumps(assessment.answers)
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.get("", response_model=List[AssessmentResponse])
def get_assessments(
    assessment_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener evaluaciones del usuario"""
    query = db.query(Assessment).filter(Assessment.user_id == current_user.id)
    if assessment_type:
        query = query.filter(Assessment.type == assessment_type)
    assessments = query.order_by(Assessment.created_at.desc()).all()
    
    # Convertir answers de JSON a dict
    for a in assessments:
        a.answers = json.loads(a.answers) if a.answers else {}
    return assessments

@router.get("/latest/{assessment_type}", response_model=AssessmentResponse)
def get_latest_assessment(
    assessment_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener la evaluación más reciente de un tipo"""
    assessment = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.type == assessment_type
    ).order_by(Assessment.created_at.desc()).first()
    
    if assessment:
        assessment.answers = json.loads(assessment.answers) if assessment.answers else {}
    return assessment