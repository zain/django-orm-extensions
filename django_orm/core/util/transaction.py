# -*- coding: utf-8 -*-

from django.db import transaction

class TransactionContext(object):
    forced_managed = False

    def __init__(self, using="default"):
        self.using = using

    def __enter__(self):
        if not transaction.is_managed(using=self.using):
            transaction.enter_transaction_management(using=self.using)
            self.forced_managed = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.forced_managed:
                transaction.commit(using=self.using)
            else:
                transaction.commit_unless_managed(using=self.using)
        finally:
            if self.forced_managed:
                transaction.leave_transaction_management(using=self.using)
