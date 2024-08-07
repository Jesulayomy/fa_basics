from datetime import (
    datetime,
    time,
    timedelta,
)
from enum import Enum
from fastapi import (
    Body,
    Cookie,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
)
from typing import (
    Annotated,
    Any,
    Union,
)
from uuid import UUID


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

fake_db = {}


class Tags(Enum):
    items = "items"
    users = "users"
    images = "images"
    files = "files"


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    is_offer: Union[bool, None] = None
    tags: set[str] = set()
    images: list[Image] | None = None
    created_at: datetime = datetime.now().isoformat()


list_of_items = [
    {"name": "item1", "price": 9.99, "tags": ["tag1", "tag2", "tag1"]},
    {"name": "item2", "price": 19.99},
    {"name": "item3", "price": 4.99},
    {"name": "item4", "price": 1.99},
]

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class User(BaseModel):
    username: str
    full_name: str | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# class UserIn(BaseUser):
#     password: str


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}


@app.get(
    "/",
    summary="Root",
    description="This is the root path, profiding a file upload form",
)
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/images/multiple/", tags=[Tags.images])
async def create_multiple_images(images: list[Image]):
    return images


@app.post("/files/")
async def create_files(files: Annotated[list[bytes], File()] = []):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")] = []):
    return {"filenames": [file.filename for file in files]}


@app.get("/portal", deprecated=True)
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.get(
    "/items/",
    status_code=200,
    tags=[Tags.items],
    response_description="All Items",
    response_model=list[Item],
)
async def read_items(ads_id: Annotated[str | None, Cookie()] = None, user_agent: Annotated[str | None, Header()] = None):
    return list_of_items


@app.post("/items/", tags=["items"])
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[Item, Body(
        openapi_examples = {
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
        title="The Item to PUT",
        description="An item with properties: name, description, price, tax, tags, images",
    )],
    importance: Annotated[int, Body()] = 0,
    user: Annotated[User, Body()] = None,
):
# async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    # results = {"item_id": item_id, "item": item, "user": user}
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[item_id] = json_compatible_item_data
    return fake_db


# @app.patch("/items/{item_id}")
# async def read_items(
#     item_id: UUID,
#     start_datetime: Annotated[datetime, Body()],
#     end_datetime: Annotated[datetime, Body()],
#     process_after: Annotated[timedelta, Body()],
#     repeat_at: Annotated[time | None, Body()] = None,
# ):
#     start_process = start_datetime + process_after
#     duration = end_datetime - start_process
#     return {
#         "item_id": item_id,
#         "start_datetime": start_datetime,
#         "end_datetime": end_datetime,
#         "process_after": process_after,
#         "repeat_at": repeat_at,
#         "start_process": start_process,
#         "duration": duration,
#     }


@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_item_data = list_of_items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    if item_id not in fake_items_db.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user


# @app.post("/user/")
# async def create_user(user: UserIn) -> BaseUser:
#     return user


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
