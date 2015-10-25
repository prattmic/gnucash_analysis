#!/usr/bin/env python

from __future__ import print_function
import argparse
import datetime
import gnucash

def accounts_by_type(root, account_type):
    """Find gnucash Accounts by account type.

    Args:
        root: Base Account to search for
        account_type: Account type constant

    Returns:
        List of accounts of specified type recursively found under root.
    """
    accounts = []

    for account in root.get_children():
        if account.GetType() == account_type:
            accounts.append(account)

        subaccounts = accounts_by_type(account, account_type)
        for subaccount in subaccounts:
            accounts.append(subaccount)

    return accounts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GNUCash expense moving average')
    parser.add_argument('file', type=str, help='GNUCash file')

    args = parser.parse_args()

    session = gnucash.Session(args.file)

    try:
        book = session.get_book()
        root = book.get_root_account()

        expense_accounts = accounts_by_type(root, gnucash.ACCT_TYPE_EXPENSE)

        print("Expense Accounts:\n")
        for account in expense_accounts:
            print(account.name)
            for split in account.GetSplitList():
                transaction = split.GetParent()
                date = datetime.date.fromtimestamp(transaction.GetDate())
                description = transaction.GetDescription()
                amount = split.GetAmount().to_double()
                print("%s: %s: %f" % (date, description, amount))
    finally:
        session.end()
        session.destroy()
