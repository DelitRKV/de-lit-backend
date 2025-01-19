from typing import List
from pydantic import BaseModel


class config(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    USE_CREDENTIALS: bool
    TEMPLATE_FOLDER: str


class EmailRequest(BaseModel):
    subject: str
    recipients: List[str]
    body: str
