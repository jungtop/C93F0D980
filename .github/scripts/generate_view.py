import re
from pathlib import Path
from collection.items.pecha import Pecha
from collection.items.collection_meta import CollectionMeta
from collection.utils import get_item
from openpecha.config import BASE_PATH
from openpecha.utils import load_yaml
from collection.items.pecha import Pecha,PechaFragment
from collection.items.alignment import Alignment
from collection.items.work import Work
from collection.views.plain_text import PlainTextView
from enum import Enum
from collection.views.view import View
import os


class ItemEnum():
    pecha =  Pecha
    alignment = Alignment
    work = Work
    pecha_fragment = PechaFragment


OPENPECHA_DATA_PREFIX_URL = "https://github.com/OpenPecha-Data"

def get_op_item_meta(item_id, item_path):
    meta = None
    if re.match("^I", item_id):
        meta_path = Path(f"{item_path}/{item_id}.opf/meta.yml")
        meta = load_yaml(meta_path)
    return meta


def get_item_attr(dic, item_path):
    pecha = {}
    pecha_attrs = Pecha.__annotations__.keys()
    for pecha_attr in pecha_attrs:
        if pecha_attr in dic.keys():
            pecha[pecha_attr] = dic[pecha_attr]
        else:
            pecha[pecha_attr] = None
    pecha["path"] = item_path
    return pecha

def get_meta(col):
    meta = CollectionMeta(collection_id=col.id,item_views_map=col.item_views_map)
    return meta

def get_item_cls(item_id):
    
    if item_id.startswith("A"):
        item_class = ItemEnum.alignment
    elif item_id.startswith("W"):
        item_class = ItemEnum.work
    elif item_id.startswith("I"):
        item_class = ItemEnum.pecha
    return item_class


def get_collection_meta(collection_id):
    meta_path = Path(f"{collection_id}.opc/meta.yml")
    meta = load_yaml(meta_path)
    return meta
        

def generate_view(op_item_id: str,view:View,output_dir: Path = None):
    Path("./data").mkdir(parents=True,exist_ok=True)
    if output_dir is None:
        output_dir = BASE_PATH
    op_item_path = get_item(op_item_id)
    meta = get_op_item_meta(op_item_id, op_item_path)
    item_attr = get_item_attr(meta, op_item_path)
    item = get_item_cls(op_item_id)
    item_obj = item(**item_attr)
    serializer = view.serializer
    views_path = serializer().serialize(item=item_obj,output_dir=Path("./data"))

    return views_path

if __name__ == "__main__":
    generate_view("I3D4F1804",PlainTextView(),Path("./data"))