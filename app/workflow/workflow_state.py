from typing import TypedDict

class WorkflowState(TypedDict, total=False):
    article_id: int
    job_id: int
    retry_count: int
    feedback: str
    status: str
    approved: bool
    publish_requested: bool
    script: str
    video_path: str
    review: dict
    publish_result: dict
    error: str
