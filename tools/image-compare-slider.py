#! python
# -*- coding: utf-8 -*-
#
# This file is part of the image-compare-slider project.
# Copyright (c) 2020-2025 zero <zero.kwok@foxmail.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

'''
一个Python脚本, 用于扫描指定目录中的图片, 来生成下面格式的 JSON 文件, 然后使用 HTML 的可视化模板来显示这个 JSON 的内容.

命令行语法:
image-compare-slider.py -d dictory -t templet-directory 
image-compare-slider.py -t templet-directory -h host -p port

-d dictory 需要扫描的目录
-t templet-directory 模板目录, 里面包含 index.html 和相关的 js/css 文件
-h host 预览服务器的 host, 默认 localhost
-p port 预览服务器的端口, 默认 8000

目录结构:
dictory/
  - 1_origin.jpg               # 图片名_原始图像.格式
  - 1_workflow1_10.2.jpg       # 图片名_工作流名_耗时(秒).格式
  - 1_workflow2_35.0.jpg
  - 2_origin.jpg
  - 2_workflow_13.5.jpg

生成的 JSON 文件格式如下, 存储在 templet-directory/data.json 中: 
[
  [
    {
      "label": "1 (原图)",
      "file": "dictory/1_origin.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": 155224
    },
    {
      "label": "workflow1",
      "file": "dictory/1_workflow1_10.2.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": 5245214,
      "elapsedTime": 10.2
    },
    {
      "label": "workflow2",
      "file": "dictory/1_workflow2_10.2.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": 5245214,
      "elapsedTime": 35.0
    },
  ],
  [
    {
      "label": "2 (原图)",
      "file": "dictory/2_origin.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": 155224
    },
    {
      "label": "workflow1",
      "file": "dictory/1_workflow1_10.2.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": 5245214,
      "elapsedTime": 13.5
    }
  ]
]
'''

import os
import re
import json
import argparse

try:
    from flask import Flask, send_from_directory
    from PIL import Image
except ImportError as e:
    print("Missing required module. Please install dependencies with:")
    print("  python -m pip install Flask Pillow")

def scan_images(directory: str):
    """
    扫描目录，返回分组后的图像信息：
    {
       "1": [ {...}, {...}, ... ],
       "2": [ {...}, ... ]
    }
    """
    image_pattern = re.compile(
        r"(?P<name>.+?)_(?P<workflow>.+?)?_?(?P<elapsed>[0-9\.]+)?\.(jpg|jpeg|png|webp)$",
        re.IGNORECASE
    )

    groups = {}  # { name: [file1, file2, ... ] }
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue

        m = image_pattern.match(fname)
        if not m:
            print(f"Skip {fname}.")
            continue

        img_id = m.group("name")
        groups.setdefault(img_id, []).append((fname, m.groupdict()))

    return groups


def read_image_info(path):
    """读取宽、高、字节大小"""
    try:
        with Image.open(path) as im:
            width, height = im.size
    except Exception:
        width = height = 0

    return width, height, os.path.getsize(path)


def build_json(directory: str):
    """
    解析扫描到的文件，生成最终 JSON 结构
    """
    groups = scan_images(directory)
    result = []

    for name, files in sorted(groups.items(), key=lambda x: x[0]):
        items = []

        for fname, meta in files:
            fullpath = os.path.join(directory, fname)
            width, height, size = read_image_info(fullpath)

            workflow = meta["workflow"]
            elapsed = meta["elapsed"]

            if workflow == "origin" or workflow is None:
                label = f"{name} (原图)"
            else:
                label = workflow

            item = {
                "label": label,
                "file": f'/images/{fname}',
                "width": width,
                "height": height,
                "bytes": size,
            }

            if workflow is not None and elapsed is not None:
                item["elapsedTime"] = float(elapsed)

            items.append(item)

        # 原图排最前
        items.sort(key=lambda x: (0, x["label"]) if "_origin." in x["file"] else (1, x["label"]))
        result.append(items)

    return result

def run_server(dirs, host, port):
    url = f"http://{host}:{port}"
    print(f"Running: {url}")

    def make_handler(dir):
        def handler(f='index.html'):
            # print(f"fetch: {dir}, {f}")
            return send_from_directory(dir, f)
        return handler

    app = Flask(__name__)
    for route, dir in dirs.items():
        print(f"  - {route}: {dir}")
        handler = make_handler(dir)
        app.add_url_rule(route, dir, handler)
        app.add_url_rule(f'{route}/<path:f>', f'{dir}/<path:f>', handler)
    app.run(host=host, port=port, debug=False)

def main():
    ap = argparse.ArgumentParser(
        description="Image Compare Slider JSON Builder & Preview Server",
        add_help=False)

    ap.add_argument("-d", "--directory", required=True,
                    help="图片目录")
    ap.add_argument("-t", "--template",
                    help="模板目录，必须包含 index.html")
    ap.add_argument("-h", "--host", default="0.0.0.0",
                    help="预览服务器 host, 默认 0.0.0.0")
    ap.add_argument("-p", "--port", default=8000, type=int,
                    help="预览服务器端口，默认 8000")
    ap.add_argument("--scan", help="扫描图片目录, 生成预览需要的JSON文件", action="store_true")
    ap.add_argument("--view", help="运行预览HTTP服务, 然后可以通过浏览器访问", action="store_true")
    ap.add_argument("--help", action="help", help="显示帮助")
    ap.add_argument('--debug', help='启用调试模式', action='store_true')

    args = ap.parse_args()
    if args.debug:
        print("Debugging mode enabled.")
        print("  - args:", args)
        input('Wait for debugging and press Enter to continue...')

    # 1. 生成 JSON 
    if args.scan:
        print(f"Scanning directory: {args.directory}")
        data = build_json(args.directory)
        if not data:
            print("There is no image file in the directory.。")
            return

        json_path = os.path.join(args.directory, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Writen: {json_path}")

    # 2. 启动预览服务器 
    if args.view:
        if args.template is None:
            f = os.path.join(os.path.dirname(__file__), 'templet')
            if os.path.exists(f):
                args.template = f
            else:
                print("Template directory is required for preview server.")
                return

        dirs = {'/': os.path.abspath(args.template), '/images': os.path.abspath(args.directory)}
        run_server(dirs, args.host, args.port)


if __name__ == "__main__":
    main()
