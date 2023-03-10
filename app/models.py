import collections
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

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Application) and self.uuid == __o.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)

    def create(self, docs):
        uuid = self.save()
        for doc in docs:
            with open(f"{self.path}/applications/{doc['key'].capitalize()}-{uuid}.{doc['extension']}", "wb") as fp:
                fp.write(doc['file'].getbuffer())

    def save(self):
        uuid = str(self.uuid)
        self.title = self.title.strip()

        with open(f"{self.path}/applications/Application-{uuid}.yml", "wt") as fp:
            safe_dump(jsonable_encoder(self.dict()), fp)

        return uuid

    def destroy(self):
        uuid = str(self.uuid)

        for fname in (Path(self.path) / "applications").rglob(f"*-{uuid}.*"):
            fname.unlink()

    def file(self, file_name, open_mode='rb'):
        prefix, extension = file_name.split(".")
        uuid = str(self.uuid)
        file_name = f"{self.path}/applications/{prefix}-{uuid}.{extension}"

        return open(file_name, open_mode)

    @classmethod
    def expert_doc_save(cls, program, username, key, extension):
        with open(f"/src/data/programs/{program.lower()}/applications/{key.capitalize()}-{username}-{uuid}.{extension}", "wb") as fp:
            fp.write(doc['file'].getbuffer())

    @classmethod
    def expert_doc_load(cls, program, username, key, extension):
        pass

    @classmethod
    def _load_from(cls, program, user=None, expert=False):
        for file in Path(f"/src/data/programs/{program.lower()}/applications").glob("*.yml"):
            app = Application(**safe_load(file.open()))

            if app.program != program:
                continue

            if expert:
                if app.expert_1 == user or app.expert_2 == user:
                    yield app

            elif user is None or app.owner == user :
                yield app

    @classmethod
    def load_from(cls, program, user=None, expert=False):
        result = collections.defaultdict(lambda: None)

        for app in Application._load_from(program, user, expert):
            result[app.title] = app

        return result
