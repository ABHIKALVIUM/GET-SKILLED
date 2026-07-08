import asyncio
import time
import google.generativeai as genai
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

async def timed_call(label):
    t = time.time()
    await model.generate_content_async("Say hello.")
    print(f"{label}: {time.time()-t:.2f}s")

async def main():
    t = time.time()
    await asyncio.gather(timed_call("A"), timed_call("B"), timed_call("C"))
    print(f"Total: {time.time()-t:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
