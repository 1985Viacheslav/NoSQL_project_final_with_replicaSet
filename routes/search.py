from fastapi import Request, Depends

from dependencies import get_es, router, templates, cookie, SessionData, verifier
from uuid import UUID

@router.get("/search/")
async def search(request: Request, query: str = None):
# async def search(request: Request, session_id: UUID = Depends(cookie), session_data: SessionData = Depends(verifier), query: str = None):
    # username = session_data.username if session_data else None
    username = 'Admin'

    if query:
        es = get_es()
        search_results = es.search(index="rooms", body={"query": {"match": {"name": query}}})
        context = {"request": request, "results": search_results['hits']['hits'], "username": username}
        return templates.TemplateResponse("search_results.html", context)
    else:
        context = {"request": request, "username": username}
        return templates.TemplateResponse("search.html", context)