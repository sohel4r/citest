import csv
import datetime
import os
import sys
import shutil
from collections import namedtuple

import hashlib
import requests
from requests.auth import HTTPBasicAuth
from invoke import run, task
import yaml

from pg import error, info, BUILD_PATH, ROOT_DIR, bold, pbold, warn
# from pg import frigga
# from pg.util import find_paths, inflect_pipeline, put_s3_file, put_s3_obj_binary, yes_no_prompt, run_cmd, indent


username = os.environ['ARTIFACTORY_NEW_USERNAME']
password = os.environ['ARTIFACTORY_NEW_PASSWORD']
artifactory_url = os.environ['ARTIFACTORY_NEW_URL']
artifactory_repo = os.environ['ARTIFACTORY_NEW_REPO']

def get_md5(fin):
    md5 = hashlib.md5()
    with open(fin, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            md5.update(chunk)
    return md5.hexdigest()

def get_sha1(fin):
    sha1 = hashlib.sha1()
    with open(fin, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            sha1.update(chunk)
    return sha1.hexdigest()


def art_upload(fin, base_file_name=None):
    if base_file_name is None:
        base_file_name = os.path.basename(fin)
    md5hash = get_md5(fin)
    sha1hash = get_sha1(fin)
    headers = {"X-Checksum-Md5": md5hash, "X-Checksum-Sha1": sha1hash}
    r = requests.put("{0}/{1}/{2}".format(artifactory_url, artifactory_repo, base_file_name),auth=(username,password), headers=headers, verify=False, data=open(fin, 'rb'))
    return r

branch_name = run("git branch | grep '*' | awk '{print $2}'", hide='both')

art_upload(os.path.join(BUILD_PATH, 'ansible.tar.gz'), '{}-{}.tar.gz'.format(branch_name, '2'))
