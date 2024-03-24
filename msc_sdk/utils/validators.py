import re
from itertools import cycle


def validate_cnpj(cnpj: str) -> str:
    cnpj = re.sub("[^0-9]", "", cnpj)

    cnpj = cnpj.zfill(14)

    if cnpj in (c * 14 for c in "1234567890"):
        raise ValueError("Invalid CNPJ")

    cnpj_r = cnpj[::-1]
    for i in range(2, 0, -1):
        cnpj_enum = zip(cycle(range(2, 10)), cnpj_r[i:])
        dv = sum(map(lambda x: int(x[1]) * x[0], cnpj_enum)) * 10 % 11
        if cnpj_r[i - 1 : i] != str(dv % 10):
            raise ValueError("Invalid CNPJ")

    return cnpj
