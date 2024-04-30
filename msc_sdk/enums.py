from enum import Enum


class APINamespaces(str, Enum):
    AUTHENTICATE = "authenticate"
    CONTRACTS = "contracts"
    POSITIONS = "positions"
    RECURRENCES = "recurrences"


class AccountType(str, Enum):
    CHECKING_ACCOUNT = "CC"  # CONTA_CORRENTE
    DEPOSIT_ACCOUNT = "CD"  # CONTA_DE_DEPOSITO
    GUARANTEED_ACCOUNT = "CG"  # CONTA_GARANTIDA
    INVESTMENT_ACCOUNT = "CI"  # CONTA_DE_INVESTIMENTO
    PAYMENT_ACCOUNT = "PG"  # CONTA_DE_PAGAMENTO
    SAVINGS_ACCOUNT = "PP"  # POUPANCA
