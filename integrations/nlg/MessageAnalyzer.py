from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

organization = os.environ.get("OPEN_AI_ORG")
openai_key = os.environ.get("OPEN_AI_KEY")
client = OpenAI(api_key=openai_key, organization=organization)

# Create class for pre-defined prompt
class MessangeAnalyzer(object):

    def __init__(self, language):
        self._language = language

    def _prompt(self):
        prompt = """
            The following sentence my meal and glucose level is in %s language. 
            Please return this in simple paragraph format not longer than 100 words and
            prevent using the word 'I' and focus on facts and recommendations.
            Avoid using any markdown format or '*' symbols.
        """ % self._language
        return prompt

    def evaluate(self, data, prompt):
        """data: healthcare data
            prompt: crafted prompt saved in nlg_types
        """
        prompt = self._prompt() + data + prompt
        print(prompt)
        # Using chatgpt-4o is much faster, but still not able to compress total runtime below 30seconds
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo", # 4o
        messages=[
            {"role": "system", "content": "You are a healthcare assistant, skilled in discovering healthcare insights from data provided, and gives healthy lifestyle recommendations for diabetic patients."},
            {"role": "user", "content": prompt}
        ]
        )
        # print(completion.choices[0].message.content)
        return(completion.choices[0].message.content)
