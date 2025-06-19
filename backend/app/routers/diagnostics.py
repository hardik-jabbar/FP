from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="/api", tags=["diagnostics"])


@router.post("/diagnostics")
async def upload_diagnostics(file: UploadFile = File(...)):
    """Accepts a diagnostics log file and simply echoes back metadata.

    This is a stub endpoint intended to demonstrate file‐upload workflow to
    stakeholders. It does NOT persist data yet – it only reads the file in
    memory and returns the filename & size. Extend later with real
    processing/storage.
    """
    try:
        contents = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "message": "Diagnostics file received successfully. Processing TBD."
    }
