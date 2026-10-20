from enum import StrEnum


class PrivilegeName(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"
