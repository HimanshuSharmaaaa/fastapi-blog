from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db

router = APIRouter()

SIDEBAR_ITEMS = 5


@router.get("")
async def get_sidebar(db: Annotated[AsyncSession, Depends(get_db)]):
    posts = await db.execute(
        select(models.Post.id, models.Post.title, models.User.username)
        .select_from(models.Post)
        .join(models.User, models.User.id == models.Post.user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(SIDEBAR_ITEMS),
    )

    comments = await db.execute(
        select(
            models.Comment.post_id,
            models.Comment.content,
            models.User.username,
            models.Post.title.label("post_title"),
        )
        .select_from(models.Comment)
        .join(models.User, models.User.id == models.Comment.user_id)
        .join(models.Post, models.Post.id == models.Comment.post_id)
        .order_by(models.Comment.date_posted.desc())
        .limit(SIDEBAR_ITEMS),
    )

    post_count = func.count(models.Post.id)
    authors = await db.execute(
        select(models.User.id, models.User.username, post_count.label("post_count"))
        .select_from(models.User)
        .join(models.Post, models.Post.user_id == models.User.id)
        .group_by(models.User.id, models.User.username)
        .order_by(post_count.desc(), models.User.username)
        .limit(SIDEBAR_ITEMS),
    )

    return {
        "latest_posts": [
            {"id": r.id, "title": r.title, "username": r.username} for r in posts
        ],
        "latest_comments": [
            {
                "post_id": r.post_id,
                "content": r.content[:80],
                "username": r.username,
                "post_title": r.post_title[:40],
            }
            for r in comments
        ],
        "top_authors": [
            {"id": r.id, "username": r.username, "post_count": r.post_count}
            for r in authors
        ],
    }