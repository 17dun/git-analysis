import sys
import os
import requests
import base64
import markdown
from bs4 import BeautifulSoup

def clean_markdown_to_text(md_content):
    """
    Converts Markdown content to clean plain text, removing HTML tags and other formatting.
    """
    try:
        html = markdown.markdown(md_content)
    except Exception as e:
        print(f"警告：Markdown转换HTML时出错: {e}", file=sys.stderr)
        html = md_content 

    try:
        soup = BeautifulSoup(html, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = soup.get_text(separator='\n', strip=True)
        print("Markdown 内容已成功清洗为纯文本。", file=sys.stderr)
        return text
    except Exception as e:
        print(f"警告：HTML清洗时出错: {e}", file=sys.stderr)
        return md_content

def search_github_repo(search_term):
    """
    Searches GitHub for the top repository and returns its full name and star count.
    """
    print(f"正在搜索关键词: {search_term}...", file=sys.stderr)
    url = f"https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {
        "q": search_term,
        "sort": "stars",
        "order": "desc"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data["items"]:
            print("错误：没有找到相关的仓库。", file=sys.stderr)
            return None, None
        
        top_repo = data["items"][0]
        repo_full_name = top_repo["full_name"]
        star_count = top_repo["stargazers_count"]
        print(f"已找到星标数最高的仓库: {repo_full_name} (Stars: {star_count})", file=sys.stderr)
        return repo_full_name, star_count
    except requests.exceptions.RequestException as e:
        print(f"错误：API 请求失败: {e}", file=sys.stderr)
        return None, None

def get_readme_content(repo_full_name):
    """
    Fetches the README content for a given repository.
    """
    print(f"正在获取 {repo_full_name} 的 README 文件...", file=sys.stderr)
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print(f"错误：仓库 {repo_full_name} 中没有找到 README 文件。", file=sys.stderr)
            return None
        response.raise_for_status()
        
        data = response.json()
        content_base64 = data["content"]
        content_bytes = base64.b64decode(content_base64)
        readme_content = content_bytes.decode("utf-8")
        
        print("README 文件内容获取成功。", file=sys.stderr)
        return readme_content
    except requests.exceptions.RequestException as e:
        print(f"错误：获取 README 失败: {e}", file=sys.stderr)
        return None

def save_content_to_output(filename, content):
    """
    Saves the content to the 'output' directory and returns the absolute path.
    """
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}", file=sys.stderr)

    file_path = os.path.join(output_dir, filename)
    absolute_path = os.path.abspath(file_path)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"文件已成功保存到: {absolute_path}", file=sys.stderr)
        return absolute_path
    except IOError as e:
        print(f"错误：文件保存失败: {e}", file=sys.stderr)
        return None

def main():
    """
    Main function to run the script.
    """
    if len(sys.argv) < 2:
        print("使用方法: python start.py <搜索关键词>", file=sys.stderr)
        sys.exit(1)
        
    search_term = sys.argv[1]
    
    repo_full_name, star_count = search_github_repo(search_term)
    
    if repo_full_name:
        readme_content = get_readme_content(repo_full_name)
        if readme_content:
            clean_text = clean_markdown_to_text(readme_content)
            
            # Construct filename with star count
            output_filename = f"STARS_{star_count}_{repo_full_name.replace('/', '_')}.txt"
            saved_path = save_content_to_output(output_filename, clean_text)
            
            if saved_path:
                print(saved_path)

if __name__ == "__main__":
    main()