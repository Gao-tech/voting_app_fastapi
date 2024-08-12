from sqlmodel import create_engine, SQLModel, Session

# DATABASE_URL = 'postgresql://<username>:<password>@<ip-address/hostname><port>/<database_name>'
DATABASE_URL = 'postgresql://postgres:root@localhost:5432/voting_fastapi'


engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

