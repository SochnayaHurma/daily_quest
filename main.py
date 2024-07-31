from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status

from api import router
from schemas.validation_messages import messages

app = FastAPI()
app.include_router(router=router)


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
