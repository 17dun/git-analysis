# GitHub 仓库分析器

一个简单的 Python 脚本，用于根据给定的搜索词查找 GitHub 上星标最多的仓库，下载其 README 文件，并将其保存为纯文本文件。

## 功能

*   在 GitHub 上搜索任何关键词。
*   查找星标数最多的仓库。
*   下载 README 文件。
*   将 Markdown 内容清洗为纯文本。
*   将输出保存到具有描述性名称的文件中。

## 安装

1.  克隆仓库：
    ```bash
    git clone https://github.com/your-username/git-analysis.git
    cd git-analysis
    ```

2.  安装所需的 Python 库：
    ```bash
    pip install requests beautifulsoup4 markdown
    ```

## 使用方法

在终端中运行脚本，并将搜索词作为参数：

```bash
python start.py "<你的搜索词>"
```

### 示例

```bash
python start.py "微信克隆"
```

脚本将在 `output/` 目录中创建一个名为 `STARS_<星标数>_<所有者>_<仓库名>.txt` 的文件。

## 贡献

欢迎贡献！请随时提交拉取请求。

## 许可证

本项目根据 MIT 许可证授权。
