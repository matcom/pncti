from uuid import UUID, uuid4
from pathlib import Path
import enum

from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from yaml import safe_dump, safe_load


class Status(enum.Enum):
    pending = "Pendiente"
    accept = "Completado"
    reject = "Rechazado"


class Application(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    project_type: str
    program: str
    owner: str
    path: str

    # estado
    doc_review: Status = Status.pending
    expert_1_review: Status = Status.pending
    expert_2_review: Status = Status.pending
    budget_review: Status = Status.pending
    social_review: Status = Status.pending
    overal_review: Status = Status.pending

    expert_1_score: int = 0
    expert_2_score: int = 0
    budget_score: int = 0
    social_score: int = 0

    # expertos
    expert_1: str = None
    expert_2: str = None

    def create(self, docs):
        uuid = self.save()
        for doc in docs:
            with open(f"{self.path}/applications/{doc['key'].capitalize()}-{uuid}.{doc['extension']}", "wb") as fp:
                fp.write(doc['file'].getbuffer())

    def save(self):
        uuid = str(self.uuid)

        with open(f"{self.path}/applications/Application-{uuid}.yml", "wt") as fp:
            safe_dump(jsonable_encoder(self.dict()), fp)

        return uuid

    def file(self, file_name):
        prefix, extension = file_name.split(".")
        uuid = str(self.uuid)
        file_name = f"{self.path}/applications/{prefix}-{uuid}.{extension}"

        return open(file_name, "rb")

    @classmethod
    def load_from(cls, program, user=None):
        for file in Path(f"/src/data/programs/{program}/applications").glob("*.yml"):
            app = Application(**safe_load(file.open()))

            if app.program != program:
                continue

            if user is None or app.owner == user :
                yield app
