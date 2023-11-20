from dataclasses import dataclass


@dataclass
class Company:
    name: str
    linkedin: str
    segment: str
    location: str
    folowers: int = 0
    employees: int = 0
