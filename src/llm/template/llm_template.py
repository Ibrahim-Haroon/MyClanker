from textwrap import dedent


class LlmTemplate:
    """
    Templates for the LLM to generate prompts and responses for different roles in the conversation
    """
    @staticmethod
    def web_search_parser(web_search_results: str):
        """
        This prompt is used to parse web search results and extract structured data.
        :return: contextualized prompt
        """
        return dedent(
            f"""
            Here is text field from web search results. 
            
            <text>
            {web_search_results}
            </text>
            
            It may contain markdown-fenced JSON-like block polluted with markdown 
            links (e.g., "( [yelp.com](https://...) )") and other annotations.

            Your task is PURE TRANSFORMATION. Do NOT invent data. Parse and normalize only what is present.
            
            Return ONLY a single JSON object with this exact shape:
            {{
              "Business Name": {{
                "number": "<phone or null>",
                "hours": "<hours string or null>",
                "stars": <number or null>,
                "price_range": "<$, $$, $$$ or null>"
              }},
              ...
            }}
            
            Rules:
            1) Output must be strict JSON: double quotes on all keys/strings, no markdown fences, no comments, no 
               trailing commas, no extra text.
            2) Business names are the top-level keys exactly as in input (trim whitespace).
            3) For each business, extract and clean:
               - number: take the FIRST phone-looking string from the value, remove any surrounding source notes or 
                         links. Examples accepted: "(415) 814-3788", "415-668-7670". If none, set null.
               - hours: take the first hours string; strip any "(...)" source notes and all markdown. Keep a compact
                        one-line form like "Mon–Fri: 9:00 AM – 7:00 PM; Sat: 9:00 AM – 6:00 PM; Sun: Closed". If none, 
                        set null.
               - stars: find the first decimal or integer number that represents a 0–5 rating (e.g., "4.7"). Coerce to
                        a JSON number (not string). If no clear rating, set null.
               - price_range: map the first occurrence of price symbols to "$", "$$", or "$$$". If empty/blank, set 
                              null.
            4) Strip ALL markdown:
               - Remove code fences like ```json ... ```.
               - Replace any markdown links "[label](url)" with just "label".
               - Remove any trailing parenthetical source blocks like "( [yelp.com](...) )" or "(yelp.com)" entirely.
               - Remove UTM parameters if any remained (but URLs should be removed anyway).
            5) If a field contains multiple candidates, select the first plausible value after cleaning.
            6) Never omit required keys; if a value is unknown, use null.
            7) Sort businesses by descending "stars" (null at the end). Ties by business name A→Z.
            8) Return ONLY the cleaned JSON object.
            
            Now read "text", transform, and output the final JSON.
            """
        ).strip()
