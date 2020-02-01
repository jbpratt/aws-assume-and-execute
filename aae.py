#!/usr/bin/env python3
"""
assume into numerous accounts and execute a command in parallel
"""

# TODO: determine pool size by number of accounts

import argparse
import sys
import subprocess
import shlex
from multiprocessing import Pool  # type: ignore
from typing import List

import boto3  # type: ignore
from botocore.exceptions import ClientError  # type: ignore


def assume_and_execute(inp: List) -> None:
    """
    assume_and_execute assumes into an account and
    executes a given command in a subprocess
    """
    assert len(inp) == 3
    account: str = inp[0]
    role: str = inp[1]
    function: str = inp[2]

    sts_client = boto3.client('sts')
    try:
        assumed_creds = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account}:role/{role}",
            RoleSessionName="AAE"
        )['Credentials']
    except ClientError as client_error:
        raise client_error

    try:
        proc = subprocess.Popen(shlex.split(function), env={
            "AWS_ACCESS_KEY_ID": assumed_creds['aws_access_key_id'],
            "AWS_SECRET_ACCESS_KEY": assumed_creds['aws_secret_access_key'],
            "AWS_SESSION_TOKEN": assumed_creds['aws_session_token']})
    except ValueError as ex:
        raise ex

    proc.wait()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Execute a command against multiple accounts through sts')
    PARSER.add_argument('--file', dest='file', required=False,
                        help="list of accounts (newline separated)")
    PARSER.add_argument('--command', dest='func', required=True,
                        help="command to execute in each account")
    PARSER.add_argument('--role', dest='role', required=True,
                        help="role in account to assume into")
    ARGS = PARSER.parse_args()

    if ARGS.file is not None:
        with open(ARGS.file) as f:
            ACCTS = f.readlines()
    else:
        ACCTS = sys.stdin.readlines()

    ACCTS = [a.strip('\n\r') for a in ACCTS]

    DATA = map(lambda acct: [acct, ARGS.role, ARGS.func], ACCTS)
    with Pool(3) as p:
        p.map(assume_and_execute, list(DATA))
