#!/usr/bin/env python

from __future__ import print_function
import argparse
import datetime
import gnucash
import pandas as pd

def all_accounts(root):
    """Get all gnucash Accounts,

    Args:
        root: Base Account to start from

    Returns:
        List of all accounts.
    """
    accounts = []

    for account in root.get_children():
        accounts.append(account)

        subaccounts = all_accounts(account)
        for subaccount in subaccounts:
            accounts.append(subaccount)

    return accounts

def splits_dataframe(gnc_file):
    """Get GnuCash splits as Pandas DataFrame.

    Args:
        gnc_file: GnuCash source file.

    Returns:
        DataFrame with split data from each account.
    """
    session = gnucash.Session(gnc_file)

    try:
        book = session.get_book()
        root = book.get_root_account()

        accounts = all_accounts(root)

        splits = []

        for account in accounts:
            for split in account.GetSplitList():
                transaction = split.GetParent()
                date = datetime.date.fromtimestamp(transaction.GetDate())
                description = transaction.GetDescription()
                amount = split.GetAmount().to_double()
                splits.append((account.name, date, description, amount))

        return pd.DataFrame(splits, columns=['account', 'date',
                                             'description', 'amount'])
    finally:
        session.end()
        session.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GNUCash expense moving average')
    parser.add_argument('file', type=str, help='GNUCash file')

    args = parser.parse_args()

    print(splits_dataframe(args.file))
