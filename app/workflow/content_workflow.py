from langgraph.graph import StateGraph, START, END
from app.config import MAX_RETRIES, YOUTUBE_PUBLIC_PUBLISHING_ENABLED
from app.workflow.workflow_state import WorkflowState

class ContentWorkflow:
    def __init__(self, llm):
        from app.agents import VideoCreatorAgent, QualityReviewerAgent, YouTubePublisherAgent
        from app.modules.jobs.services.script_service import ScriptService
        from app.modules.jobs.services.video_check_service import VideoCheckService
        from app.modules.jobs.services.video_render_service import VideoRenderService
        from app.modules.jobs.services.youtube_service import YouTubeService
        self.creator = VideoCreatorAgent(ScriptService(llm), VideoRenderService(llm))
        self.reviewer = QualityReviewerAgent(llm, VideoCheckService())
        self.publisher = YouTubePublisherAgent(YouTubeService())

    async def run(self, article, job, job_repo, review_repo, publish_requested=False):
        state = {
            "article_id": article.id,
            "job_id": job.id,
            "retry_count": 0,
            "feedback": "",
            "status": "processing",
            "approved": False,
            "publish_requested": publish_requested,
        }

        async def create(state):
            job.status = "generating"
            await job_repo.save(job)
            result = await self.creator.run(article, job, state.get("feedback", ""))
            state.update(result)
            return state

        async def review(state):
            result = await self.reviewer.run(article, state["video_path"], state["script"])
            state["review"] = result
            state["approved"] = result["approved"]
            state["feedback"] = result["feedback"]
            await review_repo.create(
                job_id=job.id, approved=result["approved"],
                score=result["score"], issues=str(result["issues"]),
                feedback=result["feedback"]
            )
            job.retry_count = state["retry_count"]
            await job_repo.save(job)
            return state

        def route(state):
            if state["approved"]:
                return "publish" if state.get("publish_requested") else "done"
            if state["retry_count"] < MAX_RETRIES:
                return "retry"
            return "failed"

        def retry(state):
            state["retry_count"] += 1
            return state

        async def publish(state):
            if not YOUTUBE_PUBLIC_PUBLISHING_ENABLED:
                state["publish_result"] = {
                    "published": False,
                    "message": "Publishing disabled. Enable it explicitly in .env after testing."
                }
                state["status"] = "approved_not_published"
                return state
            result = await self.publisher.run(article, job)
            state["publish_result"] = result
            state["status"] = "published" if result["published"] else "approved_publish_failed"
            return state

        def done(state):
            state["status"] = "approved"
            return state

        def failed(state):
            state["status"] = "needs_manual_review"
            return state

        graph = StateGraph(WorkflowState)
        graph.add_node("create", create)
        graph.add_node("review_video", review)
        graph.add_node("retry", retry)
        graph.add_node("publish", publish)
        graph.add_node("done", done)
        graph.add_node("failed", failed)
        graph.add_edge(START, "create")
        graph.add_edge("create", "review_video")
        graph.add_conditional_edges("review_video", route, {
            "retry": "retry", "publish": "publish", "done": "done", "failed": "failed"
        })
        graph.add_edge("retry", "create")
        graph.add_edge("publish", END)
        graph.add_edge("done", END)
        graph.add_edge("failed", END)
        result = await graph.compile().ainvoke(state)
        job.status = result["status"]
        job.retry_count = result["retry_count"]
        if result.get("error"):
            job.error = result["error"]
        await job_repo.save(job)
        return result
