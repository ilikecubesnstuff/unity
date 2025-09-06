from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    tag_id = fields.IntField(pk=True)
    trigger = fields.CharField(max_length=2000, unique=True)
    response = fields.CharField(max_length=2000)
