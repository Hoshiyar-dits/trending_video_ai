class ScriptService:
    def __init__(self, llm):
        self.llm = llm

    async def make_script(self, article, feedback=""):
        prompt = f"""
Create an original 45-60 second vertical-video script based only on this source.
Do not invent facts. Return plain narration text, no markdown.
Title: {article.title}
Source URL: {article.url}
Source summary/content: {article.content or article.summary}
Reviewer feedback to address: {feedback or "None"}
"""
        return (await self.llm.ainvoke(prompt)).content.strip()
