from typing import List, Optional, Sequence, cast

from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.mixin import PromptDictType
from llama_index.core.question_gen.prompts import build_tools_text
from llama_index.core.question_gen.types import (
    SubQuestion,
    SubQuestionList,
)
from llama_index.core.settings import Settings
from llama_index.core.tools.types import ToolMetadata
from llama_index.program.openai import OpenAIPydanticProgram

DEFAULT_MODEL_NAME = "gpt-3.5-turbo"

DEFAULT_NEXT_QUESTION_PROMPT_TMPL = """\
You are an AI assistant tasked with recommending the most appropriate next action for an LLM-powered agent. 
The agent is engaged in a conversation or task with a user. 
Your goal is to suggest the action that will be most helpful and relevant to the current context.

Consider the following information to generate your recommendation:

* **User Input:** The latest message or input provided by the user.
* **LLM Response:** The response of the LLM-powered agent to the user input.

Output your lists of 3 recommended questions that user may ask the agent.

Example:
["Search for the most recent trends in AI", "Search some blogs about machine learning", "Tell me about Multimodal AI"]

Here is the list of tools that you can use:

## Tools
```json
{tools_str}
```

## User Input
{query_str}

## LLM Response:
{llm_response}
"""


class QuestionRecommender:
    def __init__(
        self,
        program: OpenAIPydanticProgram,
        verbose: bool = False,
    ) -> None:
        self._program = program
        self._verbose = verbose

    @classmethod
    def from_defaults(
        cls,
        prompt_template_str: str = DEFAULT_NEXT_QUESTION_PROMPT_TMPL,
        llm: Optional[LLM] = None,
        verbose: bool = False,
    ) -> "QuestionRecommender":
        llm = llm or Settings.llm
        program = OpenAIPydanticProgram.from_defaults(
            output_cls=SubQuestionList,
            llm=llm,
            prompt_template_str=prompt_template_str,
            verbose=verbose,
        )
        return cls(program, verbose)

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"question_gen_prompt": self._program.prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "question_gen_prompt" in prompts:
            self._program.prompt = prompts["question_gen_prompt"]

    def generate(
        self, tools: Sequence[ToolMetadata], query_str: str, llm_response: str
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        
        question_list = cast(
            SubQuestionList, self._program(query_str=query_str, tools_str=tools_str, llm_response=llm_response)
        )
        return question_list.items

    async def agenerate(
        self, tools: Sequence[ToolMetadata], query_str: str, llm_response: str
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)

        question_list = cast(
            SubQuestionList,
            await self._program.acall(query_str=query_str, tools_str=tools_str, llm_response=llm_response),
        )
        assert isinstance(question_list, SubQuestionList)
        return question_list.items