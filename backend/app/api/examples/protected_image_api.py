"""
Example: Protected Image Processing API with Authentication

This example shows how to create a protected image processing endpoint
that requires authentication and specific permissions.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import shutil
from pathlib import Path

from app.core.database import get_db
from app.api.dependencies import (
    get_current_user,
    require_permission,
    require_roles,
    get_current_superuser
)
from app.models.models import User, ProcessedFile

router = APIRouter()


# ============================================================================
# EXAMPLE 1: Simple Authentication (Just need to login)
# ============================================================================

@router.get("/my-images")
async def list_my_images(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all images uploaded by current user
    
    Required: Just be logged in
    """
    images = db.query(ProcessedFile).filter(
        ProcessedFile.user_id == current_user.id,
        ProcessedFile.file_type == "image"
    ).all()
    
    return {
        "success": True,
        "count": len(images),
        "images": [
            {
                "id": img.id,
                "filename": img.original_filename,
                "uploaded_at": img.created_at
            }
            for img in images
        ]
    }


# ============================================================================
# EXAMPLE 2: Role-Based Access (Need specific role)
# ============================================================================

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["editor", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Upload an image
    
    Required: User must have 'editor' or 'admin' role
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # Save file (simplified example)
    upload_dir = Path("uploads/images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{current_user.id}_{file.filename}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    processed_file = ProcessedFile(
        user_id=current_user.id,
        original_filename=file.filename,
        processed_filename=str(file_path),
        file_type="image",
        status="completed"
    )
    db.add(processed_file)
    db.commit()
    db.refresh(processed_file)
    
    return {
        "success": True,
        "message": f"Image uploaded by {current_user.username}",
        "file_id": processed_file.id,
        "filename": file.filename
    }


# ============================================================================
# EXAMPLE 3: Permission-Based Access (Need specific permission)
# ============================================================================

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(require_permission("image", "delete")),
    db: Session = Depends(get_db)
):
    """
    Delete an image
    
    Required: User must have 'delete' permission on 'image' resource
    (Only admin role has this permission by default)
    """
    # Find image
    image = db.query(ProcessedFile).filter(
        ProcessedFile.id == image_id,
        ProcessedFile.file_type == "image"
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found"
        )
    
    # Check ownership (non-admin can only delete own images)
    if not current_user.is_superuser and image.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own images"
        )
    
    # Delete file
    file_path = Path(image.processed_filename)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    db.delete(image)
    db.commit()
    
    return {
        "success": True,
        "message": f"Image {image_id} deleted by {current_user.username}"
    }


# ============================================================================
# EXAMPLE 4: Superuser Only (System-level operations)
# ============================================================================

@router.post("/cleanup-all")
async def cleanup_all_images(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete all processed images (dangerous operation)
    
    Required: Must be superuser (is_superuser=True)
    """
    # Delete all image records
    deleted_count = db.query(ProcessedFile).filter(
        ProcessedFile.file_type == "image"
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"All images cleaned up by superuser {current_user.username}",
        "deleted_count": deleted_count
    }


# ============================================================================
# EXAMPLE 5: Mixed Access (Different permissions for different operations)
# ============================================================================

@router.patch("/images/{image_id}")
async def update_image_metadata(
    image_id: int,
    title: str,
    description: str = None,
    current_user: User = Depends(require_permission("image", "write")),
    db: Session = Depends(get_db)
):
    """
    Update image metadata
    
    Required: User must have 'write' permission on 'image' resource
    (Editor and admin roles have this permission)
    """
    # Find image
    image = db.query(ProcessedFile).filter(
        ProcessedFile.id == image_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found"
        )
    
    # Check ownership (non-superuser can only edit own images)
    if not current_user.is_superuser and image.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own images"
        )
    
    # Update metadata (simplified - would normally have metadata field)
    # image.metadata = {"title": title, "description": description}
    db.commit()
    
    return {
        "success": True,
        "message": "Image metadata updated",
        "image_id": image_id,
        "updated_by": current_user.username
    }


# ============================================================================
# EXAMPLE 6: Multiple Permission Check (Need ANY of specified permissions)
# ============================================================================

from app.api.dependencies import require_any_permission

@router.get("/content/{content_id}")
async def view_content(
    content_id: int,
    current_user: User = Depends(require_any_permission([
        ("image", "read"),
        ("document", "read")
    ])),
    db: Session = Depends(get_db)
):
    """
    View content (image or document)
    
    Required: User must have EITHER 'image:read' OR 'document:read' permission
    All roles (viewer, editor, admin) have read permissions
    """
    content = db.query(ProcessedFile).filter(
        ProcessedFile.id == content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return {
        "success": True,
        "content": {
            "id": content.id,
            "filename": content.original_filename,
            "type": content.file_type,
            "status": content.status,
            "owner": content.user_id
        }
    }


# ============================================================================
# HOW TO USE IN MAIN.PY
# ============================================================================
"""
from app.api.examples import protected_image_api

app.include_router(
    protected_image_api.router,
    prefix="/api/v1/images",
    tags=["Image Processing (Protected)"]
)
"""
