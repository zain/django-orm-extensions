# -*- coding: utf-8 -*-

class BaseProcedureException(Exception):
    pass

class UndefinedProcedureSource(BaseProcedureException):
    pass

class UndefinedProcedureName(BaseProcedureException):
    pass


