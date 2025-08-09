from textwrap import dedent


class LlmTemplate:
    """
    Templates for the LLM to generate prompts and responses for different roles in the conversation
    """
    @staticmethod
    def initial_customer_prompt(arg: str):
        """
        This prompt ...
        :return: contextualized prompt
        """
        return dedent(
            f"""
            "foo {arg}"
            """
        ).strip()
