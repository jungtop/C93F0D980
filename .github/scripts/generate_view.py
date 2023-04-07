import re
from pathlib import Path
from typing import Dict

from collection.items.alignment import Alignment
from collection.items.collection_meta import CollectionMeta
from collection.items.pecha import Pecha, PechaFragment
from collection.items.work import Work
from collection.utils import get_item
from collection.views.plain_text import PlainTextView
from collection.items.item import Item
from collection.views.view import View
from openpecha.config import BASE_PATH
from openpecha.utils import load_yaml

OPENPECHA_DATA_PREFIX_URL = "https://github.com/OpenPecha-Data"


class ItemEnum:
    pecha = Pecha
    alignment = Alignment
    work = Work
    pecha_fragment = PechaFragment


def get_op_item_meta(item_id:str, item_path:str):
    """
    This function gives the meta of a item
    :param item_id:id of item
    :param item_path:path of the item
    ;return:meta in str
    """
    meta = None
    if re.match("^I", item_id):
        meta_path = Path(f"{item_path}/{item_id}.opf/meta.yml")
        meta = load_yaml(meta_path)
    return meta


def get_item_attr(dic:Dict, item_path:str,item_cls:Item):
    """
    This function gives the attributes of the item_cls
    :param dic: The raw dic containg meta of the item
    :param item_path: Path of the item in str
    :pararm item_cls: Type of Item class
    :return:A dic contating all the attributes of the item_cls 
    """
    pecha = {}
    pecha_attrs = item_cls.__annotations__.keys()
    for pecha_attr in pecha_attrs:
        if pecha_attr in dic.keys():
            pecha[pecha_attr] = dic[pecha_attr]
        else:
            pecha[pecha_attr] = None
    pecha["path"] = item_path
    return pecha


def get_item_cls(item_id:str):
    """
    This function return item class base on the ID
    :param item_id: id of the item
    :return:item class
    """

    if item_id.startswith("A"):
        item_class = ItemEnum.alignment
    elif item_id.startswith("W"):
        item_class = ItemEnum.work
    elif item_id.startswith("I"):
        item_class = ItemEnum.pecha
    return item_class


def get_collection_meta(collection_id:str):
    """
    This function return the meta of the collection considering 
    it's in action pwd.
    :param collection_id:Collection id
    :return: meta in str
    """
    meta_path = Path(f"{collection_id}.opc/meta.yml")
    meta = load_yaml(meta_path)
    return meta


def generate_view(op_item_id: str, view: View, output_dir: Path = None):
    """
    This function generated views of a item
    :param op_item_id: item id
    :param view: View Object
    :param output_dir: output path of the view
    :return: list of path of generated views in Path.
    """
    Path("./data").mkdir(parents=True, exist_ok=True)
    if output_dir is None:
        output_dir = BASE_PATH
    op_item_path = get_item(op_item_id)
    meta = get_op_item_meta(op_item_id, op_item_path)
    item_cls = get_item_cls(op_item_id)
    item_attr = get_item_attr(meta, op_item_path,item_cls)
    item_obj = item_cls(**item_attr)
    serializer = view.serializer
    views_path = serializer().serialize(item=item_obj, output_dir=Path("./data"))
    return views_path


if __name__ == "__main__":
    generate_view("I3D4F1804", PlainTextView(), Path("./data"))
