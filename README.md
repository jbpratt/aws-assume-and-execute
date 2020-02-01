# assume and execute

Loop over a list of accounts, assuming a role into each account, then executing a command. The role must exist in the account and you must have permissions to assume into it.

```
usage: aae.py [-h] [--file FILE] --command FUNC --role ROLE

Execute a command against multiple accounts through sts

optional arguments:
  -h, --help      show this help message and exit
  --file FILE     list of accounts (newline separated)
  --command FUNC  command to execute in each account
  --role ROLE     role in account to assume into

# pass in account list by flag
python3 aae.py --role "Admin" --file=accounts.txt --command "./cleanup-default-vpcs.sh"

# or pipe in accounts
aws organizations list-accounts | jq '.Accounts | .[].Id' | python3 aae.py --role "Admin" --command "./cleanup-default-vpcs.sh"
```
