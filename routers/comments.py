from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from auth import CurrentUser
from database import get_db
from schemas import CommentCreate, CommentResponse

router = APIRouter()



async def get_post_or_404(post_id: int, db: AsyncSession) -> models.Post:
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_post_or_404(post_id, db)

    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.author))
        .where(models.Comment.post_id == post_id)
        .order_by(models.Comment.date_posted.asc()),
    )
    return result.scalars().all()


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_post_or_404(post_id, db)

    new_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        user_id=current_user.id,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment, attribute_names=["author"])
    return new_comment


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.post))
        .where(
            models.Comment.id == comment_id,
            models.Comment.post_id == post_id,
        ),
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    
    if current_user.id not in (comment.user_id, comment.post.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    await db.delete(comment)
    await db.commit()

