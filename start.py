import sys
import os
import requests
import base64
import markdown
import re
from bs4 import BeautifulSoup

def clean_markdown_to_text(md_content):
    """
    Converts Markdown content to clean plain text, removing HTML tags and other formatting.
    同时应用内容精简策略以减少最终文本体积。
    """
    # 第一步：精简 Markdown 内容
    md_content = simplify_readme_content(md_content)

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

def simplify_readme_content(md_content):
    """
    对 README 内容应用精简策略，去除冗余和不太重要的内容。
    """
    lines = md_content.split('\n')
    result_lines = []
    skip_until_next_section = False
    in_important_section = False
    section_depth = 0
    kept_sections = set()

    # 定义要保留的章节关键词（优先级从高到低）
    important_sections = [
        'quick start', 'getting started', 'installation', 'install', '介绍', '简介',
        'feature', '特性', '功能', 'overview', '概述'
    ]

    # 定义要跳过的章节关键词
    skip_sections = [
        'news', 'release', 'changelog', 'history', 'version',
        'faq', 'question', 'troubleshooting', 'star history',
        'contribution', 'contributing', 'license', 'acknowledgement',
        '新闻', '发布', '版本', '常见问题', '贡献', '许可', '致谢'
    ]

    # 标记是否已经保留了特性列表（避免重复）
    feature_kept = False

    for i, line in enumerate(lines):
        # 检测章节标题
        if line.startswith('#'):
            # 重置跳过标记
            skip_until_next_section = False

            # 获取章节标题（去除 # 号）
            section_title = line.lstrip('#').strip().lower()

            # 判断是否是要跳过的章节
            if any(skip_word in section_title for skip_word in skip_sections):
                skip_until_next_section = True
                continue

            # 判断是否是重要章节（只保留前3个重要章节）
            if any(imp_word in section_title for imp_word in important_sections):
                if len([s for s in kept_sections if any(imp_word in s.lower() for imp_word in important_sections)]) < 3:
                    kept_sections.add(section_title)
                    in_important_section = True
                else:
                    skip_until_next_section = True
                    continue

            # 检测特性列表（只保留第一个）
            if 'feature' in section_title or '特性' in section_title:
                if feature_kept:
                    skip_until_next_section = True
                    continue
                else:
                    feature_kept = True

        # 跳过被标记的章节
        if skip_until_next_section:
            continue

        # 去除 badge 徽章行
        if re.match(r'^\s*\[!\[.*?\]\(.*?\)\]', line):
            continue

        # 去除多语言链接行（如 🇨🇳 中文 · 🇯🇵 日本語）
        if re.search(r'🇨🇳|🇯🇵|🇪🇸|🇫🇷|🇸🇦|🇷🇺|🇮🇳|🇵🇹', line):
            continue

        # 去除纯链接行（导航用）
        if re.match(r'^\s*\[.*?\]\(.*?\)\s*·\s*\[.*?\]\(.*?\)', line):
            continue

        # 去除代码块中的长代码示例（超过20行的代码块）
        if line.strip().startswith('```'):
            # 检查代码块长度
            code_start = i
            code_end = i
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('```'):
                    code_end = j
                    break
            # 如果代码块超过15行，跳过
            if code_end - code_start > 15:
                skip_until_next_section = True
                # 添加简短说明
                result_lines.append('(代码示例已省略)')
                continue

        # 去除表格中的环境变量配置等详细表格（超过5行的表格）
        if line.startswith('|') and i > 0:
            table_start = i
            table_end = i
            for j in range(i, len(lines)):
                if not lines[j].startswith('|'):
                    table_end = j - 1
                    break
            # 如果表格超过5行，跳过
            if table_end - table_start > 5:
                skip_until_next_section = True
                continue

        # 保留该行
        result_lines.append(line)

    return '\n'.join(result_lines)

def search_github_repo(search_term):
    """
    Searches GitHub for the top repository and returns its full name and star count.
    """
    print(f"正在搜索关键词: {search_term}...", file=sys.stderr)
    url = f"https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {
        "q": search_term,
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