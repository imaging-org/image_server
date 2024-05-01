from dataclasses import dataclass


@dataclass
class Status:
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
