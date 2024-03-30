from time import time
from typing import Self


def is_pydantic(obj: object) -> bool:
    """Checks whether an object is pydantic."""
    return type(obj).__class__.__name__ == "ModelMetaclass"


def parse_pydantic_schema(schema):
    """
    Iterates through pydantic schema and parses nested schemas
    to a dictionary containing SQLAlchemy models.
    Only works if nested schemas have specified the Meta.orm_model.
    """
    parsed_schema = dict(schema)
    for key, value in parsed_schema.items():
        try:
            if isinstance(value, list) and len(value):
                if is_pydantic(value[0]):
                    parsed_schema[key] = [
                        schema.Meta.orm_model(**schema.dict()) for schema in value
                    ]
            else:
                if is_pydantic(value):
                    parsed_schema[key] = value.Meta.orm_model(**value.dict())
        except AttributeError:
            raise AttributeError(
                "Found nested Pydantic model but Meta.orm_model was not specified."
            )
    return parsed_schema


class TimeExecution:
    def __enter__(self) -> Self:
        self.start = time()
        print("[TimeExecution] Start")
        return self

    def __exit__(self, *args):
        self.end = time()
        self.interval = self.end - self.start
        print(f"[TimeExecution] End. Elapsed time: {self.interval:.3f}s")
