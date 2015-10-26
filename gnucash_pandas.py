#!/usr/bin/env python

from __future__ import print_function
import argparse
import datetime
import gnucash
import numpy as np
import pandas as pd

account_types = {
    gnucash.ACCT_TYPE_ASSET: "Asset",
    gnucash.ACCT_TYPE_BANK: "Bank",
    gnucash.ACCT_TYPE_CASH: "Cash",
    gnucash.ACCT_TYPE_CHECKING: "Checking",
    gnucash.ACCT_TYPE_CREDIT: "Credit",
    gnucash.ACCT_TYPE_EQUITY: "Equity",
    gnucash.ACCT_TYPE_EXPENSE: "Expense",
    gnucash.ACCT_TYPE_INCOME: "Income",
    gnucash.ACCT_TYPE_LIABILITY: "Liability",
    gnucash.ACCT_TYPE_MUTUAL: "Mutual",
    gnucash.ACCT_TYPE_PAYABLE: "Payable",
    gnucash.ACCT_TYPE_RECEIVABLE: "Receivable",
    gnucash.ACCT_TYPE_ROOT: "Root",
    gnucash.ACCT_TYPE_STOCK: "Stock",
    gnucash.ACCT_TYPE_TRADING: "Trading",
}

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
            name = account.name
            typ = account_types[account.GetType()]

            for split in account.GetSplitList():
                transaction = split.GetParent()
                date = datetime.date.fromtimestamp(transaction.GetDate())
                description = transaction.GetDescription()
                amount = split.GetAmount().to_double()
                splits.append((name, typ, date, description, amount))

        return pd.DataFrame(splits, columns=['account', 'type', 'date',
                                             'description', 'amount'])
    finally:
        session.end()
        session.destroy()

def daily(df, account_type):
    """DataFrame of daily totals in each account.

    Args:
        df: DataFrame in format returned by splits_dataframe
        account_type: Only include accounts of this type

    Returns:
        DataFrame indexed by date, with a column for each account. Each value
        is the transaction total for that account that day.
    """
    df = df[df['type'] == account_type]
    df = pd.pivot_table(df, index=pd.DatetimeIndex(df['date']),
                        columns='account', values='amount', aggfunc=np.sum)
    df = df.resample('D')
    df = df.fillna(0)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GNUCash expense moving average')
    parser.add_argument('file', type=str, help='GNUCash file')

    args = parser.parse_args()

    print(splits_dataframe(args.file))
