# backend/routers/conversations.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from ..database.database import get_db
from ..models.models import User, Conversation, Message
from ..schemas.schemas import ConversationResponse, ConversationCreate, MessageCreate, MessageResponse
from ..auth.auth import get_current_user
from ..classifiers.simple_risk_classifier import SimpleRiskClassifier
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["Conversaciones"])
risk_classifier = SimpleRiskClassifier()

@router.post("", response_model=ConversationResponse)
def create_conversation(
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva conversación"""
    conversation = Conversation(
        user_id=current_user.id,
        title=conv_data.title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@router.get("", response_model=List[ConversationResponse])
def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las conversaciones del usuario"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
    return conversations

@router.get("/{conv_id}", response_model=ConversationResponse)
def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una conversación específica con sus mensajes"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation

@router.post("/{conv_id}/messages", response_model=MessageResponse)
def send_message(
    conv_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar un mensaje y obtener respuesta de la IA"""
    # Verificar que la conversación pertenece al usuario
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Guardar mensaje del usuario
    user_message = Message(
        conversation_id=conv_id,
        role=message.role,
        content=message.content
    )
    db.add(user_message)
    db.commit()
    
    # Analizar riesgo
    risk_result = risk_classifier.predict_risk(message.content)
    crisis_response = risk_classifier.get_crisis_response(message.content)
    
    # Guardar respuesta de la IA
    ai_message = Message(
        conversation_id=conv_id,
        role="assistant",
        content=crisis_response["message"],
        risk_level=risk_result["risk_level"],
        analysis_data=json.dumps({
            "risk_analysis": risk_result,
            "crisis_response": crisis_response
        })
    )
    db.add(ai_message)
    
    # Actualizar fecha de la conversación
    conversation.updated_at = datetime.now()
    db.commit()
    db.refresh(ai_message)
    
    return ai_message

@router.delete("/{conv_id}")
def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una conversación"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversación eliminada"}