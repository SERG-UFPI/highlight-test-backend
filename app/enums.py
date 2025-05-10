from enum import Enum

class LanguageEnum(str, Enum):
    JAVASCRIPT = "JavaScript"
    JAVA = "Java"
    TYPESCRIPT = "TypeScript"
    PYTHON = "Python"
    CSHARP = "C#"
    PHP = "PHP"

class StageEnum(str, Enum):
    CLONE = "Clone Repositories"
    EXTRACT_COMMITS = "Extract Commit Data"
    GENERATE_TIME_SERIES = "Generate Time Series"
    CALCULATE_METRICS = "Calculate Metrics"
    CO_EVOLUTION_ANALYSIS = "Co-evolution Analysis"

class StatusEnum(str, Enum):
    IN_PROGRESS = "In progress"
    COMPLETED = "Completed"
    ERROR = "Error"

class UserStatusEnum(str, Enum):
    ACTIVE = "Active"
    BLOCKED = "Blocked"