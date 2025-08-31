from typing import TypedDict

# StateSchema cho toàn bộ workflow
class WorkflowState(TypedDict):
    note: str
    data: str
    validated_data: str
    report: str

