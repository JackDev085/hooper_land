from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional

from core.database import get_session
from core.security import get_current_user, require_admin
from models.users import User
from repositories.groups_repository import GroupsRepository
from services.email_service import email_service

router = APIRouter(prefix="/email", tags=["Email"])


class EmailSendResponse(BaseModel):
    """Resposta do envio de emails"""
    total: int
    success: int
    failed: int
    errors: list


class BulkEmailRequest(BaseModel):
    """Request para envio de email em massa"""
    group_id: int
    custom_message: Optional[str] = None


def send_emails_background(recipients: list):
    """
    Função para enviar emails em background.
    """
    try:
        result = email_service.send_bulk_reminder_emails(recipients)
        print(f"📧 Background email job concluído: {result}")
    except Exception as e:
        print(f"❌ Erro no job de email em background: {e}")


@router.post(
    "/send-reminder/{group_id}",
    response_model=EmailSendResponse,
    status_code=status.HTTP_200_OK
)
async def send_reminder_to_group(
    group_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Envia email de lembrete de avaliação para todos os membros de um grupo.
    
    Este endpoint envia emails de forma síncrona e retorna o resultado.
    Apenas administradores podem usar este endpoint.
    """
    groups_repo = GroupsRepository(session)
    
    try:
        group = groups_repo.get_group(group_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo com ID {group_id} não encontrado"
        )
    
    members = groups_repo.get_group_members(group_id)
    
    if not members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O grupo não possui membros para enviar email"
        )
    
    recipients = [
        {"email": member.email, "name": member.name}
        for member in members
    ]
    
    result = email_service.send_bulk_reminder_emails(recipients)
    
    return EmailSendResponse(
        total=result["total"],
        success=result["success"],
        failed=result["failed"],
        errors=result["errors"]
    )


@router.post(
    "/send-reminder-async/{group_id}",
    status_code=status.HTTP_202_ACCEPTED
)
async def send_reminder_to_group_async(
    group_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Envia email de lembrete de avaliação para todos os membros de um grupo de forma assíncrona.
    
    Este endpoint agenda o envio de emails em background e retorna imediatamente.
    Apenas administradores podem usar este endpoint.
    """
    groups_repo = GroupsRepository(session)
    
    try:
        group = groups_repo.get_group(group_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo com ID {group_id} não encontrado"
        )
    
    members = groups_repo.get_group_members(group_id)
    
    if not members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O grupo não possui membros para enviar email"
        )
    
    recipients = [
        {"email": member.email, "name": member.name}
        for member in members
    ]
    
    background_tasks.add_task(send_emails_background, recipients)
    
    return {
        "detail": f"Envio de emails agendado para {len(recipients)} membros do grupo '{group.name}'",
        "group_id": group_id,
        "group_name": group.name,
        "total_recipients": len(recipients)
    }


@router.post(
    "/send-test",
    status_code=status.HTTP_200_OK
)
async def send_test_email(
    current_user: User = Depends(get_current_user),
):
    """
    Envia um email de teste para o próprio usuário logado.
    """
    try:
        email_service.send_reminder_email(current_user.email, current_user.name)
        return {
            "detail": f"Email de teste enviado com sucesso para {current_user.email}",
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar email de teste: {str(e)}"
        )
