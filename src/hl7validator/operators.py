import typing


class BaseOperator:
    args: typing.Tuple

    def eval(self) -> bool:
        raise NotImplemented()


class OrOperator(BaseOperator):
    def __init__(self, *args):
        self.args = args

    def eval(self):
        return bool(self.args) and any([arg.eval() for arg in self.args])


class AndOperator(BaseOperator):
    def __init__(self, *args):
        self.args = args

    def eval(self):
        return bool(self.args) and all([arg.eval() for arg in self.args])


__all__ = ["AndOperator", "OrOperator"]
