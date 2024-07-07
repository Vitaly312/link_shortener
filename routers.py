import asyncio
from fastapi import APIRouter, Depends, Path, Response, Request, Header
from typing import Annotated
from schemas import LinkInModel, LinkOutModel, LinkStatistics
from database.crud import (create_link, get_link_by_short_link,
                            get_link_by_access_key, get_link_stats_data)
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from utils import save_transition_info


router = APIRouter()


@router.post("/links/create/", response_model=LinkOutModel)
async def create_short_link(link: LinkInModel, session: AsyncSession = Depends(get_session)):
    '''При создании ссылки, обязательно указывайте протокол(https:// или http://)'''
    short_link, access_key = await create_link(link=link, session=session)
    return {"short_link": short_link, "access_key": access_key}

@router.get("/links/{short_link}/", response_class=RedirectResponse, status_code=301)
async def get_short_link(response: Response, request: Request, short_link: str = Path(),
                          session: AsyncSession = Depends(get_session),
                          http_referer: Annotated[str | None, Header()] = None):
    link = await get_link_by_short_link(short_link=short_link, session=session)
    if not link:
        response.status_code = 404
        return {"message": "Link not found"}
    
    asyncio.create_task(save_transition_info(session, link, request.client.host, http_referer))
    return RedirectResponse(link.original_link)


@router.get('/stats/{access_key}/', response_model=LinkStatistics)
async def get_link_stats(access_key: str = Path(),
                         session: AsyncSession = Depends(get_session)):
    link = await get_link_by_access_key(
        access_key=access_key, session=session
        )
    if not link:
        return {"message": "Link not found"}
    
    return {**await get_link_stats_data(session, link),
             "original_link": link.original_link,
             "short_link": link.short_link}