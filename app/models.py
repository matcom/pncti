import collections
from uuid import UUID, uuid4
from pathlib import Path
import enum
import shutil, os

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
    moved: str = None
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
    
    experts: dict = {}

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Application) and self.uuid == __o.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)

    def create(self, docs):
        uuid = self.save()
        for doc in docs:
            self.save_doc(doc)
    
    def save_doc(self, doc):
        with open(f"{self.path}/applications/{doc['key'].capitalize()}-{self.uuid}.{doc['extension']}", "wb") as fp:
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
            
    def move(self, old_program, new_program, new_path):
        uuid = str(self.uuid)
        
        for fname in (Path(self.path) / "applications").rglob(f"*-{uuid}.*"):
            shutil.move(os.path.join(f"{self.path}/applications", fname), f"{new_path}/applications")
        self.moved = old_program
        self.program = new_program
        self.path = new_path
        self.reset()
        
    def reset(self):
        self.doc_review: Status = Status.pending
        self.expert_1_review: Status = Status.pending
        self.expert_2_review: Status = Status.pending
        self.budget_review: Status = Status.pending
        self.social_review: Status = Status.pending
        self.overal_review: Status = Status.pending

        self.expert_1_score: int = 0
        self.expert_2_score: int = 0
        self.budget_score: int = 0
        self.social_score: int = 0

        # expertos
        self.expert_1: str = None
        self.expert_2: str = None
        
        self.experts: dict = {} 

    def file(self, file_name, open_mode='rb', expert=None):
        prefix, extension = file_name.split(".")
        uuid = str(self.uuid)
        if not expert: expert = "" # Parche porque ya las aplicaciones están creadas
        file_name = f"{self.path}/applications/{prefix + expert}-{uuid}.{extension}"
        if open_mode.find('w') != -1:
            return open(file_name, open_mode)
        else:
            return open(file_name, open_mode) if Path(file_name).exists() else False

    def save_expert_eval(self, expert, file_name, doc, extension):
        with open(f"{self.path}/applications/{file_name.capitalize() + expert}-{self.uuid}.{extension}", "wb") as fp:
            fp.write(doc.getbuffer())

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

class Evaluation(BaseModel):
    final_score: float = 0
    coeficent: float = 1

class Expert(BaseModel):
    username: str
    role: str
    emails: list = []
    evaluation: Evaluation()
    count: int = 0
