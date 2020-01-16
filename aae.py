#!/usr/bin/env python3
"""
assume into numerous accounts and execute a command in parallel
"""

# TODO: determine pool size by number of accounts
# TODO: determine role_arn in a simpler way
# TODO: properly handle --command args passed to subprocess

import argparse
import sys
import subprocess
from multiprocessing import Pool # type: ignore
from typing import List

import boto3 # type: ignore
from botocore.exceptions import ClientError # type: ignore


def assume_and_execute(inp: List) -> None:
    """
    assume_and_execute assumes into an account and
    executes a given command in a subprocess
    """
    assert len(inp) == 3
    client = inp[0]
    account: str = inp[1]
    role_arn: str = inp[2]
    function: str = inp[3]

    try:
        assumed_creds = client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AAE"
        )['Credentials']
        assert assumed_creds
        try:
            subprocess.Popen([function], env={
                "AWS_ACCESS_KEY_ID": "",
                "AWS_SECRET_ACCESS_KEY": "",
                "AWS_SESSION_TOKEN": ""})
        except ValueError as ex:
            raise ex

    except ClientError as client_error:
        raise client_error


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Execute a command against multiple accounts through sts')
    PARSER.add_argument('--file', dest='file', required=False)
    PARSER.add_argument('--command', dest='func', required=True)
    PARSER.add_argument('--role_arn', dest='role_arn', required=True)
    ARGS = PARSER.parse_args()

    if ARGS.file is not None:
        with open(ARGS.file) as f:
            ACCTS = f.readlines()
    else:
        ACCTS = sys.stdin.readlines()

    ACCTS = [a.strip('\n\r') for a in ACCTS]
    STS_CLIENT = boto3.client('sts')

    DATA = map(lambda acct: [STS_CLIENT, acct, ARGS.role_arn, ARGS.func], ACCTS)
    with Pool(3) as p:
        p.map(assume_and_execute, list(DATA))
