import json
import re

class QualityReviewerAgent:
    def __init__(self, llm, check_service):
        self.llm, self.check_service = llm, check_service

    async def run(self, article, video_path, script):
        tech_ok, tech_message = await self.check_service.technical_video_check(video_path)
        prompt = f"""
Review this narration against the supplied source. Return ONLY JSON:
{{"approved": true or false, "score": 0-100, "issues": ["..."], "feedback": "..."}}
Approve only if the narration is reasonably supported by the source and has no obvious fabricated claims.
Source title: {article.title}
Source content: {article.content or article.summary}
Narration: {script}
Technical check: {tech_message}
"""
        try:
            response = (await self.llm.ainvoke(prompt)).content
            match = re.search(r"\{.*\}", response, re.S)
            data = json.loads(match.group(0)) if match else {}
        except Exception:
            data = {"approved": False, "score": 0, "issues": ["Reviewer returned invalid JSON"], "feedback": "Review the script and retry."}
        approved = bool(data.get("approved", False)) and tech_ok
        issues = list(data.get("issues", []))
        if not tech_ok:
            issues.append(tech_message)
        return {
            "approved": approved,
            "score": float(data.get("score", 0)),
            "issues": issues,
            "feedback": str(data.get("feedback", "")) or tech_message,
        }
