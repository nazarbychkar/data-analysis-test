import asyncio
import os
import time
from typing import List

import aiohttp
import io
from PIL import Image
from googleapiclient.discovery import build

import pandas as pd

import openpyxl

SPREADSHEET_ID = "1QX2IhFyYmGDFMvovw2WFz3wAT4piAZ_8hi5Lzp7LjV0"
GOOGLE_SHEETS_API_KEY = os.environ.get("GOOGLE_SHEETS_API_KEY")
RANGE_NAME = "feed!A1:B46889"  # B46889

image_resolution_cache = {}


def authenticate_sheets(api_key: str):
    return build("sheets", "v4", developerKey=api_key).spreadsheets()


async def sheet_image_sizes(api_key: str):
    sheets = authenticate_sheets(api_key)
    result = (
        sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    values = result.get("values", [])
    print(len(values))

    async with aiohttp.ClientSession() as session:
        tasks = [
            process_image_size(session, image_list[0]) for image_list in values[2:]
        ]
        resolutions = await asyncio.gather(*tasks)

    data = values[1:2] + [
        [image_list[0], resolution]
        for image_list, resolution in zip(values[2:], resolutions)
    ]

    df = pd.DataFrame(data, columns=values[0])

    excel_file_path = "output.xlsx"

    df.to_excel(excel_file_path, index=False)

    print(f"Data has been written to {excel_file_path}")


# async def sheet_image_sizes(api_key: str):
#     sheets = authenticate_sheets(api_key)
#     result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
#     values = result.get("values", [])
#     print(len(values))
#
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         batch_size = 20000  # Змініть розмір пакету відповідно до своїх потреб
#         for i in range(0, len(values[2:]), batch_size):
#             batch_urls = [image_list[0] for image_list in values[2:][i:i + batch_size]]
#             tasks.append(process_batch_images(session, batch_urls))
#
#         resolutions = []
#         for batch_resolutions in await asyncio.gather(*tasks):
#             resolutions.extend(batch_resolutions)
#
#     data = values[1:2] + [[image_list[0], resolution] for image_list, resolution in zip(values[2:], resolutions)]
#
#     df = pd.DataFrame(data, columns=values[0])
#
#     excel_file_path = "output.xlsx"
#
#     df.to_excel(excel_file_path, index=False)
#
#     print(f"Data has been written to {excel_file_path}")
#
#
# async def process_batch_images(session, batch_urls: List[str]) -> List[str]:
#     batch_resolutions = []
#     for image_url in batch_urls:
#         resolution = await process_image_size(session, image_url)
#         batch_resolutions.append(resolution)
#     return batch_resolutions


async def process_image_size(session, image_url: str) -> str:
    if image_url in image_resolution_cache:
        return image_resolution_cache[image_url]
    try:
        async with session.get(
            image_url, headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            image_bytes = await response.read()
        img_iostream = io.BytesIO(image_bytes)
        img = Image.open(img_iostream)
        width, height = img.size
        resolution = f"{width}x{height}"

        image_resolution_cache[image_url] = resolution

        return resolution
    except Exception as err:
        return f"{err}"


if __name__ == "__main__":
    start = time.time()
    asyncio.run(sheet_image_sizes(API_KEY))
    end = time.time()
    print(end - start)
    print(len(image_resolution_cache))
