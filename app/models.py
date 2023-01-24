from uuid import UUID, uuid4
from pathlib import Path

from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from yaml import safe_dump, safe_load


class Application(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    project_type: str
    owner: str

    def create(self, anexo3, avalCC, presupuesto):
        uuid = self.save()

        with open(f"/src/data/applications/Anexo3-{uuid}.docx", "wb") as fp:
            fp.write(anexo3.getbuffer())

        with open(f"/src/data/applications/AvalCC-{uuid}.docx", "wb") as fp:
            fp.write(avalCC.getbuffer())

        with open(f"/src/data/applications/Presupuesto-{uuid}.xlsx", "wb") as fp:
            fp.write(presupuesto.getbuffer())

    def save(self):
        uuid = str(self.uuid)

        with open(f"/src/data/applications/Application-{uuid}.yml", "wt") as fp:
            safe_dump(jsonable_encoder(self.dict()), fp)

        return uuid

    def file(self, file_name):
        prefix, extension = file_name.split(".")
        uuid = str(self.uuid)
        file_name = f"/src/data/applications/{prefix}-{uuid}.{extension}"

        return open(file_name, "rb")

    @classmethod
    def load_from(cls, user):
        for file in Path("/src/data/applications").glob("*.yml"):
            app = Application(**safe_load(file.open()))

            if app.owner == user:
                yield app
