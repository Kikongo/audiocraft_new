import os
import json
from datasets import load_dataset
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

HF_token = os.getenv("HF_TOKEN", HF_token)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_token,
)

OUTPUT_DIR = "musiccaps_audio"

dataset = load_dataset("google/MusicCaps", split="train")

SYSTEM_PROMPT = """
You convert music descriptions into structured metadata.

Return ONLY valid JSON with this schema:
{
  "description": "string",
  "general_mood": "string",
  "genre_tags": ["string"],
  "lead_instrument": "string",
  "accompaniment": "string",
  "tempo_and_rhythm": "string",
  "vocal_presence": "string",
  "production_quality": "string"
}
"""

def enrich_caption(caption):

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct:novita",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": caption}
        ]
    )

    text = response.choices[0].message.content
    print(text)

    return json.loads(text)


for item in dataset:

    ytid = item["ytid"]
    start_s = item["start_s"]
    caption = item["caption"]

    wav_file = f"{OUTPUT_DIR}/{ytid}_{start_s}.wav"
    json_file = f"{OUTPUT_DIR}/{ytid}_{start_s}.json"

    if not os.path.exists(wav_file):
        continue

    if os.path.exists(json_file):
        print("Skip:", json_file)
        continue

    try:

        metadata = enrich_caption(caption)

        with open(json_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print("Saved:", json_file)

    except Exception as e:
        print("Error:", e)
