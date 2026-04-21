import requests
import os
import sys
import re
from urllib.parse import urlparse
from pathlib import Path

# GitHub 镜像站点列表
MIRROR_SITES = [
    "https://ghfast.top",
    "https://github.moeyy.xyz",
    "https://mirror.ghproxy.com",
    "https://gh-proxy.com",
    "https://ghproxy.net",
]

# 已知镜像域名，用于转换回原始 GitHub 链接
MIRROR_DOMAINS = [
    "download.fastgit.org",
    "ghproxy.com",
    "gh-proxy.com",
    "ghfast.top",
    "github.moeyy.xyz",
    "mirror.ghproxy.com",
    "ghproxy.net",
]

# 默认保存目录
DEFAULT_SAVE_DIR = r"D:\downupload"

def parse_github_url(url):
    """解析 GitHub URL，提取原始下载链接"""
    url = url.strip()
    
    # 如果是镜像站点链接，转换为原始 GitHub 链接
    for domain in MIRROR_DOMAINS:
        if domain in url:
            # 提取 /user/repo/releases/download/... 部分
            match = re.search(r'/(?:[^/]+/)?([^/]+/[^/]+/releases/download/.+)', url)
            if match:
                return f"https://github.com/{match.group(1)}"
            # 提取 /user/repo/archive/... 部分
            match = re.search(r'/(?:[^/]+/)?([^/]+/[^/]+/archive/.+)', url)
            if match:
                return f"https://github.com/{match.group(1)}"
            # 提取 raw.githubusercontent.com 对应的原始文件
            match = re.search(r'/(?:[^/]+/)?(raw\.githubusercontent\.com/.+)', url)
            if match:
                return f"https://{match.group(1)}"
    
    # 如果是 github.com 链接，转换为 raw.githubusercontent.com 或其他下载链接
    if "github.com" in url:
        # Release 下载链接
        if "/releases/download/" in url:
            return url
        # 仓库 ZIP 链接
        if re.search(r'/archive/refs/', url):
            return url
        # 原始文件链接
        if "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com")
            url = re.sub(r'/blob/', '/', url)
            return url
        # 仓库主分支 ZIP
        if re.search(r'github\.com/[^/]+/[^/]+$', url):
            repo = url.rstrip("/")
            return f"{repo}/archive/refs/heads/main.zip"
    
    return url

def convert_to_mirror_url(original_url, mirror):
    """将原始 GitHub URL 转换为镜像 URL"""
    if "github.com" in original_url or "githubusercontent.com" in original_url:
        return f"{mirror}/{original_url}"
    return original_url

def download_file(url, output_path=None, use_mirror=True):
    """下载文件，支持镜像加速"""
    original_url = url
    url = parse_github_url(url)
    
    print(f"原始链接: {original_url}")
    print(f"解析链接: {url}")
    
    if output_path is None:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = "downloaded_file"
        # 确保默认目录存在
        os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)
        output_path = os.path.join(DEFAULT_SAVE_DIR, filename)
    
    print(f"保存路径: {output_path}")
    
    # 尝试使用镜像下载
    if use_mirror:
        for i, mirror in enumerate(MIRROR_SITES, 1):
            mirror_url = convert_to_mirror_url(url, mirror)
            print(f"\n尝试镜像 {i}/{len(MIRROR_SITES)}: {mirror}")
            
            try:
                response = requests.get(mirror_url, stream=True, timeout=30)
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)
                    
                    print(f"\n✓ 下载成功！使用镜像: {mirror}")
                    print(f"文件大小: {downloaded} bytes")
                    return True
                else:
                    print(f"  镜像返回状态码: {response.status_code}")
            except Exception as e:
                print(f"  镜像连接失败: {str(e)}")
                continue
    
    # 如果镜像都失败，尝试直接下载
    print("\n所有镜像失败，尝试直接下载...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)
            
            print(f"\n✓ 下载成功！直接下载")
            print(f"文件大小: {downloaded} bytes")
            return True
        else:
            print(f"✗ 下载失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("GitHub 快速下载工具")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print()
        url = input("请输入 GitHub 链接或镜像链接: ").strip()
        if not url:
            print("错误: 链接不能为空！")
            input("按回车键退出...")
            sys.exit(1)
        output = None
    else:
        url = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = download_file(url, output)
    
    if success:
        print(f"\n下载完成！文件保存在 {DEFAULT_SAVE_DIR} 目录下")
    else:
        print("\n下载失败，请检查链接是否正确")
    
    input("按回车键退出...")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
