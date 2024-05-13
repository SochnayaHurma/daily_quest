from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from starlette import status

from api import router

from pathlib import Path

from schemas.validation_messages import messages

template = Path(__file__).parent.parent.joinpath('frontend', 'public')
app = FastAPI()
app.include_router(router=router)
templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')
# origins = [
#     'http://localhost:3000',
#     'http://localhost:5173',
#     'http://localhost:8000',
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PATCH"],
#     allow_headers=["*"]
# )

from uuid import uuid4
from itertools import chain
from fastapi import Depends
from service_layer.unit_of_work import get_unit_of_work, SqlAlchemyUnitOfWork


@app.get('/make_data')
async def make_data(uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)):
    rnd_str = lambda: uuid4().hex
    # user = await uow.user.create(username='qwe', email='q@m.ru', password=hash_password('qwe'))
    contract = await uow.contract.create(rnd_str()[:15], 1)
    jobs = [
        await uow.job.create(name=rnd_str(), point=15, default=True)
        for _ in range(3)
    ]
    jobs_editable = [
        await uow.job.create(name=rnd_str(), point=15, default=False)
        for _ in range(5)
    ]
    [
        await uow.contract_jobs.add_job(contract_id=contract.id, job_id=job.id)
        for job in chain(jobs, jobs_editable)
    ]
    rooms = [
        await uow.room.create(rnd_str())
        for _ in range(15)
    ]
    [
        await uow.contract_rooms.add_room(contract_id=contract.id, room_id=room.id)
        for room in rooms
    ]
    return 'success'


@app.get('/{path:path}')
async def index(request: Request, path=None):
    return templates.TemplateResponse(request=request,
                                      name='index.html')


@app.exception_handler(RequestValidationError)
async def translate_validation_messages(request, exc):
    errors = []
    for e in exc.errors():
        error: dict = e.copy()
        translated_message = messages.get(e['type'])
        if translated_message:
            current_message = translated_message.copy()
            ctx_message = error['ctx'][current_message['ctx']]
            error['msg'] = current_message['msg'].format(
                label=error['loc'][1],
                value=ctx_message
            )
        errors.append(error)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': errors}))

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        log_level='info'
    )
