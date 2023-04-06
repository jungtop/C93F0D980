from generate_view import generate_view
from collection.views.hfml import HFMLView
from collection.views.plain_text import PlainTextView
from enum import Enum
from openpecha.utils import load_yaml
from pathlib import Path
from github import Github
import os
import logging
import sys


OWNER="jungtop"

logging.basicConfig(
    filename="basefile_metadata.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

class ViewEnum(Enum):
    plaintext =  PlainTextView
    hfml = HFMLView


def notifier(msg):
    logging.info(msg)

def extract_pecha_ids(msg):
    pecha_ids = [i.strip() for i in msg.split(",")]
    return pecha_ids


def update_repo(g, repo_name, file_path, commit_msg, new_content):
    try:
        repo = g.get_repo(f"{OWNER}/{repo_name}")
        contents = repo.get_contents(f"{file_path}",ref="main")
        repo.update_file(path = contents.path, message = commit_msg, content =new_content, sha=contents.sha,branch="main")
        notifier( f'{repo_name} updated ')
    except Exception as e:
        notifier( f'{repo_name} not updated with error {e}')

    
def push_view(pecha_id,view_path,view_type,token)-> None:
    g = Github(token)
    view = view_path.read_text(encoding="utf-8")
    base_id = view_path.stem
    view_name = f"{pecha_id}_{base_id}.txt"
    file_path = f"{collection_id}.opc/views/{view_type}/{view_name}"
    commit_msg = f"Updated {view_name}"
    update_repo(g, collection_id, file_path, commit_msg, view)


def push_views(pecha_id,views_path,view_type,token):
    for view_path in views_path:
        push_view(pecha_id,view_path,view_type,token)


def get_view_types(pecha_id):
    views = []
    collection_id = os.getenv("REPO_NAME")
    meta_path = Path(f"./{collection_id}.opc/meta.yml")
    meta = load_yaml(meta_path)
    view_types = meta["item_views_map"]
    for view_type,body in view_types.items():
        if pecha_id in body.keys():
            views.append(view_type)
        
    return views

def get_view_class(view_name:str):
    try:
        for e in ViewEnum:
            if e.name == view_name:
                return e.value
    except ValueError as e:
        print(f"Unknown View Class {view_name}")
        return []

def update_view(issue_message,token)->None:
    global collection_id
    pecha_ids = extract_pecha_ids(issue_message)
    collection_id = os.getenv("REPO_NAME")
    
    for pecha_id in pecha_ids:
        view_types = get_view_types(pecha_id)
        for view_type in view_types:
            view = get_view_class(view_type)
            views_path = generate_view(pecha_id,view())
            print("Views Created")
            print(views_path)
            print(type(views_path))
            if views_path:
                push_views(pecha_id,views_path,view_type,token)


if __name__ == "__main__":
    issue_message = sys.argv[1]
    token = sys.argv[2]
    update_view(issue_message,token)