import logging
import os
import sys
from enum import Enum
from pathlib import Path

from collection.views.hfml import HFMLView
from collection.views.plain_text import PlainTextView
from generate_view import generate_view
from github import Github
from openpecha.utils import load_yaml

OWNER = "jungtop"
collection_id =os.getenv("REPO_NAME")

logging.basicConfig(
    filename="basefile_metadata.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

class ViewEnum(Enum):
    plaintext = PlainTextView
    hfml = HFMLView


def notifier(msg):
    logging.info(msg)


def extract_pecha_ids(msg):
    pecha_ids = [i.strip() for i in msg.split(",")]
    return pecha_ids


def update_repo(g, repo_name, file_path, commit_msg, new_content):
    """
    This functions updated the repo to github
    :param g:Github Obj
    :param repo_name: name of the repo 
    :param file_path: Path of the file to be updated
    :param commit_msg: Commit message
    :param new_cotent: new content to be push in the file_path
    :return: None
    """
    print(file_path)

    repo = g.get_repo(f"{OWNER}/{repo_name}")
    contents = repo.get_contents(f"{file_path}", ref="main")
    repo.update_file(
        path=contents.path,
        message=commit_msg,
        content=new_content,
        sha=contents.sha,
        branch="main",
    )
    """ try:
        repo = g.get_repo(f"{OWNER}/{repo_name}")
        contents = repo.get_contents(f"{file_path}", ref="main")
        repo.update_file(
            path=contents.path,
            message=commit_msg,
            content=new_content,
            sha=contents.sha,
            branch="main",
        )
        print(f"{repo_name} updated ")
    except Exception as e:
        print(f"{repo_name} not updated with error {e}") """


def write_view(file_path:str,commit_msg:str,new_content:str) -> None:
    """
    This function pushes the new view created to the repository itself
    :param file_path: path of the file in the repo
    :param commit_msg: commit message
    :new_content: new content to write in the file_path
    :return: None
    """
    Path(file_path).write_text(new_content)
    #update_repo(g, collection_id, file_path, commit_msg, new_content)


def write_views(views_path, view_type):
    """
    This function pushes the new views created to the repository itself
    :param views_path: Path of Views
    :view_type: Type of View
    :return: None
    """
    for view_path in views_path:   
        base_id = view_path.stem
        view_name = f"{base_id}.txt"
        file_path = f"{collection_id}.opc/views/{view_type}/{view_name}"
        view = view_path.read_text(encoding="utf-8")
        commit_msg = f"Updated {view_path.name}"
        write_view(file_path,commit_msg,view)


def get_view_types(item_id):
    """
    This fucntion returns view types in a collection of a item id
    :param item_id: item id
    :return views: Returns list of view 
    """
    views = []
    meta_path = Path(f"./meta.yml")
    meta = load_yaml(meta_path)
    view_types = meta["item_views_map"]
    for view_type, body in view_types.items():
        if item_id in list(body.keys()):
            views.append(view_type)

    return views


def get_view_class(view_name: str):
    """
    This function return the view class associated with view name
    :param view_name: Name of the view in str
    :return:View Class
    """
    try:
        for e in ViewEnum:
            if e.name == view_name:
                return e.value
    except ValueError:
        print(f"Unknown View Class {view_name}")
        return []


def update_view(issue_message) -> None:
    """
    This function updates the view when given a issue message of items.
    :params issuse_message: a stirng which consist op item ids
    :return : None
    """
    pecha_ids = extract_pecha_ids(issue_message)
    for pecha_id in pecha_ids:
        view_types = get_view_types(pecha_id)
        for view_type in view_types:
            view = get_view_class(view_type)
            views_path = generate_view(pecha_id, view())
            if views_path:
                write_views(views_path, view_type)


if __name__ == "__main__":
    print(sys.argv)
    issue_message = sys.argv[1]
    update_view(issue_message)
