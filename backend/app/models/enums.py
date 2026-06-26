import enum


class ServiceCategory(str, enum.Enum):
    lab = "lab"
    doctor_visit = "doctor_visit"
    diagnostics = "diagnostics"
    procedure = "procedure"


class Currency(str, enum.Enum):
    KZT = "KZT"
    USD = "USD"


class UnmatchedStatus(str, enum.Enum):
    pending = "pending"
    matched = "matched"
    rejected = "rejected"
