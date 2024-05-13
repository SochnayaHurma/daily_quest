from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings


def make_engine(
        *,
        db_user=settings.db_settings.POSTGRES_USER,
        db_password=settings.db_settings.POSTGRES_PASSWORD,
        db_host=settings.db_settings.POSTGRES_HOST,
        db_port=settings.db_settings.POSTGRES_PORT,
        db_name=settings.db_settings.POSTGRES_DB,
        **kwargs
):
    url = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'.format(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        db=db_name
    )
    return create_async_engine(url, **kwargs)


engine = make_engine(
    db_user=settings.db_settings.POSTGRES_USER,
    db_password=settings.db_settings.POSTGRES_PASSWORD,
    db_host=settings.db_settings.POSTGRES_HOST,
    db_port=settings.db_settings.POSTGRES_PORT,
    db_name=settings.db_settings.POSTGRES_DB,
    echo=True,
    isolation_level='SERIALIZABLE'
)
session_factory = async_sessionmaker(bind=engine)



