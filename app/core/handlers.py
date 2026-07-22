from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.responses import ResponseBuilder
from app.utils.logger import logger


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):

        logger.exception(str(exc))

        return JSONResponse(
            status_code=500,
            content=ResponseBuilder.error(
                "Internal Server Error",
                str(exc),
            ),
        )