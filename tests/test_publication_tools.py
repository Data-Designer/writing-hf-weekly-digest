import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = load_script("audit_publication")

    def test_short_text_only_bundle_fails_publication_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "digest.md").write_text("# 标题\n\n一篇很短的文章。", encoding="utf-8")
            result = self.audit.audit_bundle(root, profile="publication-partial")
            self.assertFalse(result["passed"])
            codes = {item["code"] for item in result["errors"]}
            self.assertIn("missing-html", codes)
            self.assertIn("too-short", codes)
            self.assertIn("too-few-visuals", codes)
            self.assertIn("too-few-paper-cards", codes)

    def test_complete_fixture_passes_publication_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            for index in range(6):
                (assets / f"visual-{index}.svg").write_text(
                    '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="600">'
                    f"<title>Visual {index}</title><text>Chart {index}</text></svg>",
                    encoding="utf-8",
                )
            cards = "\n\n".join(
                f"""### Paper {index} · 快照 {20-index} 票

一句话：问题定义。

- 💡 机制：机制说明。
- 📈 结果：结果与设置。
- ⚠️ 局限：局限说明。
- 🛠 启示：落地启示。
- 🤔 真正的 insight：编辑判断。

[HF](https://huggingface.co/papers/2606.{index:05d})
"""
                for index in range(8)
            )
            images = "\n\n".join(
                f"![图{index}](assets/visual-{index}.svg)\n\n*图{index}：说明。来源：原创统计图。*"
                for index in range(6)
            )
            body = "# 发布级测试\n\n" + ("研究内容。" * 4000) + "\n\n" + images + "\n\n" + cards
            (root / "digest.md").write_text(body, encoding="utf-8")
            (root / "digest-wechat.html").write_text(
                "<html><body>" + "".join(
                    f'<figure><img src="assets/visual-{i}.svg"><figcaption>图{i}：说明</figcaption></figure>'
                    for i in range(6)
                ) + "</body></html>",
                encoding="utf-8",
            )
            (root / "audit.md").write_text("# Audit\n\n完整证据账本。", encoding="utf-8")
            (root / "source.json").write_text('{"entries":[]}', encoding="utf-8")
            (root / "papers.json").write_text('{"papers":[]}', encoding="utf-8")
            (assets / "manifest.json").write_text(
                json.dumps(
                    {
                        "visuals": [
                            {
                                "file": f"assets/visual-{i}.svg",
                                "caption": f"图{i}：说明",
                                "source": "original",
                            }
                            for i in range(6)
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = self.audit.audit_bundle(root, profile="publication-partial")
            self.assertTrue(result["passed"], result)


class VisualBuilderTests(unittest.TestCase):
    def test_builds_four_original_visuals_and_manifest(self):
        visual = load_script("build_visuals")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            papers = {
                "statistics": {
                    "paper_count": 10,
                    "upvotes_total": 100,
                    "daily_counts": {"2026-06-22": 3, "2026-06-23": 7},
                    "top_paper": {"title": "Top", "upvotes": 20},
                },
                "papers": [
                    {
                        "id": f"2606.{i:05d}",
                        "title": f"Paper {i}",
                        "upvotes": 20 - i,
                        "github_repo": "https://github.com/x/y" if i % 2 == 0 else None,
                    }
                    for i in range(10)
                ],
            }
            editorial = {
                "title": "Agent 系统工程周",
                "subtitle": "10 篇论文的结构性观察",
                "period": "2026-06-22—2026-06-24",
                "themes": [
                    {"name": "评测", "papers": 4, "upvotes": 50},
                    {"name": "运行时", "papers": 3, "upvotes": 30},
                    {"name": "世界模型", "papers": 3, "upvotes": 20},
                ],
                "pipeline": ["评测失败", "记录状态", "合成环境", "训练恢复"],
            }
            (root / "papers.json").write_text(json.dumps(papers), encoding="utf-8")
            (root / "editorial.json").write_text(json.dumps(editorial), encoding="utf-8")
            manifest = visual.build_visuals(root / "papers.json", root / "editorial.json", root / "assets")
            self.assertEqual(len(manifest["visuals"]), 5)
            for item in manifest["visuals"]:
                path = root / item["file"]
                self.assertTrue(path.exists())
                svg = path.read_text(encoding="utf-8")
                self.assertIn("<title>", svg)
                self.assertIn('width="1080"', svg)


class WeChatRendererTests(unittest.TestCase):
    def test_renders_images_captions_tables_links_and_paper_cards(self):
        renderer = load_script("render_wechat")
        markdown = """# 标题

> 部分周提示。

## 数据快照

| 指标 | 数值 |
|---|---:|
| 论文 | 89 |

![图1](assets/chart.svg)

*图1：主题分布。来源：原创统计图。*

### Paper A · 快照 82 票

一句话：说明。

- 💡 机制：机制。
- 📈 结果：结果。
- ⚠️ 局限：局限。
- 🛠 启示：启示。
- 🤔 真正的 insight：洞察。

[HF](https://huggingface.co/papers/2606.22388)
"""
        html = renderer.render_markdown(markdown)
        self.assertIn("<table", html)
        self.assertIn("<figure", html)
        self.assertIn("<figcaption", html)
        self.assertIn('src="assets/chart.svg"', html)
        self.assertIn("paper-card", html)
        self.assertIn('href="https://huggingface.co/papers/2606.22388"', html)
        self.assertIn("max-width:100%", html)

    def test_native_paper_figures_link_to_the_high_resolution_source(self):
        renderer = load_script("render_wechat")
        markdown = """![框架图](assets/papers/2606.00001-figure-1.png)

*图1：论文框架。来源：论文Figure 1。*
"""
        html = renderer.render_markdown(markdown)
        self.assertIn(
            'href="assets/papers/2606.00001-figure-1.png"',
            html,
        )
        self.assertIn('target="_blank"', html)
        self.assertIn("点击查看高清原图", html)


class EditorialStyleAuditTests(unittest.TestCase):
    def setUp(self):
        self.style = load_script("audit_editorial_style")

    def test_research_report_fails_paperscope_editorial_profile(self):
        text = """# Agent 系统工程观察

## 第一条主线：评测

### Paper A · 快照 10票

- 🤔 真正的 insight：一个判断。

## 一句话总结

总结。
"""
        result = self.style.audit_text(text, profile="paperscope-partial")
        self.assertFalse(result["passed"])
        codes = {item["code"] for item in result["errors"]}
        self.assertIn("too-few-themes", codes)
        self.assertIn("missing-theme-engine", codes)
        self.assertIn("too-few-transitions", codes)
        self.assertIn("missing-closing-modules", codes)

    def test_full_editorial_fixture_passes(self):
        opening = """# 一个足够锋利的判断

你能在前30秒读完这一段，就够你判断这周发生了什么。

不是论文突然变多了，是研究问题换了。票数掩盖了真正的信号。

## 三个被票数掩盖的结构性观察

1. 观察一。
2. 观察二。
3. 观察三。

## 数据快照

数据说明。
"""
        themes = []
        for index in range(1, 6):
            cards = "\n".join(
                f"""### Paper {index}-{card} · 快照 {30-card}票

- 💡 机制：机制。
- 📈 结果：结果。
- ⚠️ 局限：局限。
- 🛠 你能学到什么：启示。
- 🤔 真正的 insight：这篇论文暴露了一个被忽略的问题。
"""
                for card in range(1, 3)
            )
            transition = (
                f"为什么第{index}条主线会走到这里？因为下一层问题已经出现——下一节告诉你。 ↓"
                if index < 5
                else ""
            )
            themes.append(
                f"""## 0{index}

## 主线{index}

判断：这是本节结论。

### 为什么这件事现在发生

这不是巧合，是条件同时成熟。

### 代表论文

{cards}

### 🔍 技术综观

换一个角度看，这些论文共同改变了系统结构。

### 💼 落地实战

场景一：你是产品经理。 → 先做故障测试。

{transition}
"""
            )
        closing = """## 📋 本周可以做什么：8条行动清单

1. 行动一。

## 给你的三个思考问题

1. 问题一？
2. 问题二？
3. 问题三？

## 一句话总结

一句总结。

## 💬 五句带走：本周最值得记住的判断

1. 金句一。
2. 金句二。
3. 金句三。
4. 金句四。
5. 金句五。

## 关于这篇

方法与限制放在最后。
"""
        text = opening + "\n".join(themes) + ("观点内容。" * 2200) + closing
        result = self.style.audit_text(text, profile="paperscope-partial")
        self.assertTrue(result["passed"], result)


class FigureSourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.figure_audit = load_script("audit_figure_sources")

    def test_original_only_manifest_fails_native_figure_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            visuals = []
            for index in range(8):
                relative = f"assets/original-{index}.svg"
                (root / relative).write_text("<svg></svg>", encoding="utf-8")
                visuals.append(
                    {
                        "file": relative,
                        "kind": "original-editorial",
                        "caption": f"Original {index}",
                        "source": "original",
                        "theme": min(index + 1, 5),
                    }
                )
            (assets / "manifest.json").write_text(
                json.dumps({"visuals": visuals}), encoding="utf-8"
            )
            result = self.figure_audit.audit_manifest(root)
            self.assertFalse(result["passed"])
            codes = {item["code"] for item in result["errors"]}
            self.assertIn("native-ratio", codes)
            self.assertIn("too-few-source-papers", codes)
            self.assertIn("theme-without-native-figure", codes)

    def test_provenance_complete_manifest_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            assets = root / "assets"
            papers_dir = assets / "papers"
            papers_dir.mkdir(parents=True)
            visuals = []
            for index in range(5):
                relative = f"assets/papers/2606.{index:05d}-figure-1.png"
                (root / relative).write_bytes(b"png")
                visuals.append(
                    {
                        "file": relative,
                        "kind": "paper-native",
                        "theme": index + 1,
                        "paper_id": f"2606.{index:05d}",
                        "figure": "Figure 1",
                        "original_caption": "Original framework caption.",
                        "article_caption": f"图{index+1}：论文框架图。",
                        "caption": f"图{index+1}：论文框架图。",
                        "source": "arxiv-html",
                        "source_url": f"https://arxiv.org/html/2606.{index:05d}",
                        "image_url": f"https://arxiv.org/html/2606.{index:05d}v1/x1.png",
                        "source_type": "arxiv-html",
                    }
                )
            for index in range(2):
                relative = f"assets/original-{index}.svg"
                (root / relative).write_text("<svg></svg>", encoding="utf-8")
                visuals.append(
                    {
                        "file": relative,
                        "kind": "original-editorial",
                        "caption": f"Original {index}",
                        "source": "original",
                    }
                )
            (assets / "manifest.json").write_text(
                json.dumps({"visuals": visuals}), encoding="utf-8"
            )
            result = self.figure_audit.audit_manifest(root)
            self.assertTrue(result["passed"], result)


class PaperFigureCollectorTests(unittest.TestCase):
    def test_parses_arxiv_figures_and_rejects_logos(self):
        collector = load_script("collect_paper_figures")
        html_text = """
        <html><body>
          <img src="/static/arxiv-logo.svg" alt="arXiv logo">
          <figure id="S1.F1">
            <img src="2606.00001v1/x1.png" alt="Refer to caption">
            <figcaption><span>Figure 1:</span> Overview of the framework.</figcaption>
          </figure>
          <figure id="S1.F2">
            <img src="2606.00001v1/assets/logos/github-logo.png" alt="logo">
            <figcaption>Uncaptioned logo.</figcaption>
          </figure>
          <figure id="S2.F3">
            <img src="2606.00001v1/x3.svg" alt="Refer to caption">
            <figcaption><span>Figure 3:</span> Main evaluation results.</figcaption>
          </figure>
        </body></html>
        """
        figures = collector.parse_arxiv_figures(
            html_text,
            page_url="https://arxiv.org/html/2606.00001",
        )
        self.assertEqual(len(figures), 2)
        self.assertEqual(figures[0]["figure"], "Figure 1")
        self.assertIn("Overview of the framework", figures[0]["original_caption"])
        self.assertEqual(
            figures[0]["image_url"],
            "https://arxiv.org/html/2606.00001v1/x1.png",
        )


if __name__ == "__main__":
    unittest.main()
