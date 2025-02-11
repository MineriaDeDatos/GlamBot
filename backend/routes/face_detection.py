from fastapi import APIRouter

router = APIRouter()

@router.get("/detect-face")
def detect_face():
    return {"message": "Face detection endpoint"}
