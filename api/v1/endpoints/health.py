from fastapi import APIRouter, status
router = APIRouter(tags=["Health"])
@router.get("/health",status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "ok", "message": "Serviço funcionando normalmente"}