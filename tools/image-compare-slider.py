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
import mimetypes
import urllib.parse
from pathlib import Path

# 修复 Flask 静态文件的 MIME 类型问题
mimetypes.add_type('application/javascript', '.js')
try:
    from flask import Flask, send_from_directory, render_template
    from PIL import Image
except ImportError as e:
    print("Missing required module. Please install dependencies with:")
    print("  python -m pip install Flask Pillow")


def read_image_info(path):
    """读取宽、高、字节大小"""
    try:
        with Image.open(path) as im:
            width, height = im.size
    except Exception:
        width = height = 0

    return width, height, os.path.getsize(path)

def relative_path_to_url(path:Path):
    """将相对路径转换为 URL"""
    if type(path) == str:
        path = Path(path)
    return '/'.join(urllib.parse.quote(part) for part in path.parts)

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
            print(f"Skip file: {fname}.")
            continue

        img_id = m.group("name")
        groups.setdefault(img_id, []).append((fname, m.groupdict()))

    return groups

'''
def make_image_mate_data(directory: str):
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
        
    json_path = os.path.join(directory, "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Writen: {json_path}")

    return True
'''

def make_image_mate_data(directory: str):
    """
    递归解析所有子目录，生成最终 JSON 结构
    返回生成 data.json 的目录列表
    """
    pathDirs = []
    pathRoot = Path(directory).resolve()
    
    # 递归遍历所有子目录
    for root, dirs, files in os.walk(directory):
        pathCurr = Path(root)
        
        # 扫描当前目录的图像文件
        groups = scan_images(str(pathCurr))
        if not groups:
            continue  # 如果没有匹配的图像文件，跳过这个目录
        
        # 准备当前目录的元数据
        result = []
        for name, files in sorted(groups.items(), key=lambda x: x[0]):
            items = []

            for fname, meta in files:
                fullpath = pathCurr / fname
                width, height, size = read_image_info(str(fullpath))

                workflow = meta["workflow"]
                elapsed = meta["elapsed"]

                if workflow == "origin" or workflow is None:
                    label = f"{name} (原图)"
                else:
                    label = workflow

                item = {
                    "label": label,
                    "file": '/images/' + relative_path_to_url(fullpath.relative_to(pathRoot)),
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
        
        # 在当前目录生成 data.json
        json_path = pathCurr / "data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Written: {json_path}")
        pathDirs.append(str(pathCurr.relative_to(pathRoot)))

    return pathDirs

def run_server(dirs, indexs, host, port):
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

    linker = []
    for path, url in indexs.items():
        linker.append(f'<a href="{url}">{path}</a>')
    @app.route('/metadata/<path:f>')
    def metadata(f):
        if f == 'index.json':
            return json.dumps(indexs, ensure_ascii=False, indent=2)
        else: # list.html
            return '<br>'.join(linker)

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
        
    args.directory = os.path.abspath(args.directory)
    pathMate = os.path.join(args.directory, "mate.json")

    # 1. 生成 JSON 
    if args.scan:
        print(f"Scanning directory: {args.directory}")
        pathDirs = make_image_mate_data(args.directory)
        if not pathDirs:
            print("There is no image file in the directory.。")
            return
        print(f"Scanning result: {pathDirs}")

        pathDirs = [p for p in pathDirs if p != '.']
        if pathDirs:
            with open(pathMate, "w", encoding="utf-8") as f:
                json.dump(pathDirs, f, ensure_ascii=False, indent=2)

    # 2. 启动预览服务器 
    if args.view:
        if args.template is None:
            f = os.path.join(os.path.dirname(__file__), 'templet')
            if os.path.exists(f):
                args.template = f
            else:
                print("Template directory is required for preview server.")
                return
        else:
            args.template = os.path.abspath(args.template)
    
        pathDirs = []
        if os.path.exists(pathMate):
            with open(pathMate, "r", encoding="utf-8") as f:
                pathDirs = json.load(f)

        url = f"http://{args.host}:{args.port}"
        inds = {}
        dirs = {
            '/': args.template, 
            '/images': args.directory }
        for path in pathDirs:
            stem = f'/images/{relative_path_to_url(path)}'
            dirs[stem] = os.path.abspath(os.path.join(args.directory, path))
            inds[path] = f'{url}?data={stem}/data.json'

        run_server(dirs, inds, args.host, args.port)


if __name__ == "__main__":
    main()
