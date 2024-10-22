from typing import Annotated

from fastapi import FastAPI, Query

from export_ingester.models import ExportsModel

from .utils import FilterParams, create_data, filter_data

TEST_DATA = list(create_data())


app = FastAPI()


@app.get("/api/1/exports")
def get_export(filter_params: Annotated[FilterParams, Query()]):
    count, data = filter_data(TEST_DATA, filter_params)
    return ExportsModel(count=count, data=data)
