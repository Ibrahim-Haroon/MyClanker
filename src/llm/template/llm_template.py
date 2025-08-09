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

    @staticmethod
    def web_search_intent(web_search_query: str):
        """
        This prompt is used to classify the high-level intent of the user's web search query.
        Output is a short, imperative-style phrase (e.g., "Book Haircut", "Get Food", "Buy Electronics").
        """
        return dedent(
            f"""
            Given the web search query, identify the **primary user intent**  in a short, action-oriented phrase.

            <query>
            {web_search_query}
            </query>

            Rules:
            1) Output ONLY a single intent string. No explanations, no JSON, no extra text.
            2) Make it imperative and concise (e.g., "Book Haircut", "Get Food", "Buy Electronics", "Find Hotel").
            3) If the query is location-specific (e.g., "... near me",), ignore the location in the intent.
            4) Do not include brand names unless they are the sole purpose of the search (e.g., "Buy iPhone").
            5) If the query is ambiguous, pick the most likely intent based on common human behavior.
            6) Capitalize each word (Title Case).

            Now return the intent.
            """
        ).strip()

    @staticmethod
    def web_search_query(user_request: str):
        """
        Rewrite a natural-language user task into a concise, engine-friendly web search query.

        Examples:
          - "I need a haircut"            -> "barbers near me"
          - "Any good dessert spots"      -> "dessert spots near me"

        """
        return dedent(
            f"""
            You are a Search Query Composer. Convert the user's task into a single, effective web search query.

            <user_request>
            {user_request}
            </user_request>

            Rules:
            1) Output ONLY one search query string. No quotes, no markdown, no JSON, no extra text.
            2) Be concise (3–10 words). Remove filler (“I need”, “please”, “can you”).
            3) Prefer common head terms and plurals for local services
               (e.g., "barbers", "hair salons", "plumbers", "restaurants", "mechanics").
            4) If the task implies a local service and NO location is given, append "near me".
               If a location is given (city/neighborhood/zip), use that location and DO NOT add "near me".
            5) Preserve explicit modifiers the user states: cuisine, brand, price (cheap, $$), “open now”, rating (4.5+)
               delivery/takeout, emergency/24/7, date/time (“today”, “tonight”, “August 12”).
            6) For informational tasks, use clear keywords (“how to”, “guide”, “requirements”, “fix”, “troubleshooting”)
            7) Do not include pronouns or conversational phrasing. Avoid punctuation unless necessary (e.g., +, 4.5+).
            
            Example:
                User: I need to be a haircut
                Query: Barbers near me
                
            Now return only the rewritten search query.
            """
        ).strip()



