#!/usr/bin/env python
# coding: utf-8

import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "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"

client: OpenAI = OpenAI()

# Create the prompt with the randomly selected options
random_prompt = f"""
Create an image to use for a loading screen in an app. The app is called "enoch" and is an AI tour guide app. The color scheme is;

086986
1A2838

THe image should only be the name, and a design pattern. The image returned should be 1024x1792.
"""

# print(random_prompt)
for i in range(5):
    response = client.images.generate(
        model="dall-e-3",
        prompt=random_prompt,
        size="1024x1792",
        quality="hd",
        style="natural",
        n=1,
    )

    image_url = response.data[0].url
    print(image_url)
