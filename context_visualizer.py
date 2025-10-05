"""
Context Evolution Visualizer
可視化不同 context 策略的演變過程和差異

這個工具展示：
1. Context 內容的 DIFF 比較
2. Token 使用量的演變
3. 回應質量的對比
4. 互動式的步驟追蹤
"""

import json
from datetime import datetime
from difflib import unified_diff, SequenceMatcher
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.layout import Layout
from rich.columns import Columns
from rich import box
import tiktoken

console = Console()


class ContextSnapshot:
    """單個 Context 快照"""
    
    def __init__(self, name: str, content: str, metadata: Dict[str, Any] = None):
        self.name = name
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.token_count = self._count_tokens(content)
    
    def _count_tokens(self, text: str) -> int:
        """計算 token 數量"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        except:
            # Fallback: 粗略估計
            return len(text.split())
    
    def summary(self) -> str:
        """返回摘要信息"""
        return f"{self.name} | {self.token_count} tokens | {len(self.content)} chars"


class ContextVisualizer:
    """Context 演變可視化器"""
    
    def __init__(self):
        self.snapshots: List[ContextSnapshot] = []
        self.responses: Dict[str, Any] = {}
    
    def add_snapshot(self, name: str, content: str, metadata: Dict = None):
        """添加一個 context 快照"""
        snapshot = ContextSnapshot(name, content, metadata)
        self.snapshots.append(snapshot)
        console.print(f"✅ Added snapshot: {snapshot.summary()}", style="green")
    
    def add_response(self, context_name: str, response: str, score: float = None):
        """記錄 context 對應的回應"""
        self.responses[context_name] = {
            "content": response,
            "score": score,
            "length": len(response),
            "timestamp": datetime.now().isoformat()
        }
    
    def show_diff(self, idx_a: int, idx_b: int):
        """顯示兩個 context 快照的差異"""
        if idx_a >= len(self.snapshots) or idx_b >= len(self.snapshots):
            console.print("❌ Invalid snapshot indices", style="red")
            return
        
        snap_a = self.snapshots[idx_a]
        snap_b = self.snapshots[idx_b]
        
        console.print(f"\n[bold cyan]📊 Comparing:[/bold cyan]")
        console.print(f"  A: {snap_a.summary()}")
        console.print(f"  B: {snap_b.summary()}")
        console.print(f"  Token Δ: {snap_b.token_count - snap_a.token_count:+d}\n")
        
        # 生成 unified diff
        diff = unified_diff(
            snap_a.content.splitlines(keepends=True),
            snap_b.content.splitlines(keepends=True),
            fromfile=snap_a.name,
            tofile=snap_b.name,
            lineterm=""
        )
        
        diff_text = "".join(diff)
        if diff_text:
            syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Context Diff", border_style="cyan"))
        else:
            console.print("✨ No differences found", style="yellow")
    
    def show_similarity(self, idx_a: int, idx_b: int):
        """計算並顯示相似度"""
        snap_a = self.snapshots[idx_a]
        snap_b = self.snapshots[idx_b]
        
        matcher = SequenceMatcher(None, snap_a.content, snap_b.content)
        ratio = matcher.ratio() * 100
        
        console.print(f"\n[bold]Similarity Score: {ratio:.1f}%[/bold]")
        
        # 顯示相似度條
        bar_length = 40
        filled = int(bar_length * ratio / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        console.print(f"[cyan]{bar}[/cyan] {ratio:.1f}%\n")
    
    def show_evolution(self):
        """顯示完整的 context 演變過程"""
        console.print("\n[bold magenta]📈 Context Evolution Timeline[/bold magenta]\n")
        
        table = Table(show_header=True, header_style="bold yellow", box=box.ROUNDED)
        table.add_column("Step", style="cyan", width=8)
        table.add_column("Context Name", style="green")
        table.add_column("Tokens", justify="right", style="blue")
        table.add_column("Δ Tokens", justify="right", style="magenta")
        table.add_column("Time", style="dim")
        
        for i, snap in enumerate(self.snapshots):
            delta = ""
            if i > 0:
                prev_tokens = self.snapshots[i-1].token_count
                diff = snap.token_count - prev_tokens
                delta = f"{diff:+d}"
            
            table.add_row(
                f"#{i}",
                snap.name,
                str(snap.token_count),
                delta,
                snap.timestamp.strftime("%H:%M:%S")
            )
        
        console.print(table)
    
    def show_response_comparison(self):
        """比較不同 context 產生的回應"""
        if not self.responses:
            console.print("⚠️  No responses recorded", style="yellow")
            return
        
        console.print("\n[bold cyan]🎯 Response Comparison[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold yellow", box=box.HEAVY)
        table.add_column("Context", style="green", width=20)
        table.add_column("Score", justify="center", style="blue")
        table.add_column("Length", justify="right", style="cyan")
        table.add_column("Preview", style="dim", width=50)
        
        for ctx_name, resp in self.responses.items():
            score_str = f"{resp['score']:.1%}" if resp['score'] is not None else "N/A"
            preview = resp['content'][:50] + "..." if len(resp['content']) > 50 else resp['content']
            
            # 根據分數添加顏色
            if resp['score'] and resp['score'] >= 0.8:
                score_style = "green"
            elif resp['score'] and resp['score'] >= 0.5:
                score_style = "yellow"
            else:
                score_style = "red"
            
            table.add_row(
                ctx_name,
                f"[{score_style}]{score_str}[/{score_style}]",
                str(resp['length']),
                preview
            )
        
        console.print(table)
    
    def show_side_by_side(self, idx_a: int, idx_b: int, max_lines: int = 20):
        """並排顯示兩個 context"""
        snap_a = self.snapshots[idx_a]
        snap_b = self.snapshots[idx_b]
        
        lines_a = snap_a.content.splitlines()[:max_lines]
        lines_b = snap_b.content.splitlines()[:max_lines]
        
        # 創建並排面板
        panel_a = Panel(
            "\n".join(lines_a),
            title=f"[bold cyan]{snap_a.name}[/bold cyan]",
            border_style="cyan",
            subtitle=f"{snap_a.token_count} tokens"
        )
        
        panel_b = Panel(
            "\n".join(lines_b),
            title=f"[bold magenta]{snap_b.name}[/bold magenta]",
            border_style="magenta",
            subtitle=f"{snap_b.token_count} tokens"
        )
        
        console.print("\n")
        console.print(Columns([panel_a, panel_b]))
    
    def export_comparison(self, filename: str = None):
        """導出比較結果到 JSON"""
        if filename is None:
            filename = f"context_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "snapshots": [
                {
                    "name": s.name,
                    "content": s.content,
                    "tokens": s.token_count,
                    "timestamp": s.timestamp.isoformat(),
                    "metadata": s.metadata
                }
                for s in self.snapshots
            ],
            "responses": self.responses
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n✅ Exported to [cyan]{filename}[/cyan]", style="green")


def demo_context_engineering():
    """演示：比較三種 context 策略"""
    console.print(Panel.fit(
        "[bold yellow]Context Engineering Visualizer Demo[/bold yellow]\n"
        "比較 Baseline、Rules-based 和 Few-shot 三種策略",
        border_style="yellow"
    ))
    
    viz = ContextVisualizer()
    
    # Context A: Baseline
    CTX_A = """You are a sentiment analyzer.
Extract product info from this review."""
    
    viz.add_snapshot(
        name="Context A (Baseline)",
        content=CTX_A,
        metadata={"strategy": "baseline", "examples": 0}
    )
    
    # Context B: Rules-based
    CTX_B = """You are a sentiment analyzer.

Extract the following information from product reviews:
- sentiment: must be "positive", "neutral", or "negative"
- product: the product name (string)
- issue: description of any issues (string, or empty)

Output must be valid JSON format.
Do not include markdown code blocks."""
    
    viz.add_snapshot(
        name="Context B (Rules-based)",
        content=CTX_B,
        metadata={"strategy": "rules", "examples": 0}
    )
    
    # Context C: Few-shot
    CTX_C = CTX_B + """

Examples:

Input: "這支耳機音質不錯，但藍牙常常斷線。"
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth connection"}

Input: "The keyboard feels great, but the battery dies too fast."
Output: {"sentiment": "negative", "product": "keyboard", "issue": "battery life"}"""
    
    viz.add_snapshot(
        name="Context C (Few-shot)",
        content=CTX_C,
        metadata={"strategy": "fewshot", "examples": 2}
    )
    
    # 模擬回應和分數
    viz.add_response("Context A (Baseline)", 
                     '{"sentiment": "positive", "product": "camera"}', 
                     score=0.50)
    viz.add_response("Context B (Rules-based)", 
                     '{"sentiment": "negative", "product": "camera", "issue": "slow focus"}', 
                     score=0.80)
    viz.add_response("Context C (Few-shot)", 
                     '{"sentiment": "negative", "product": "camera", "issue": "night mode autofocus slow"}', 
                     score=1.00)
    
    # 顯示演變
    viz.show_evolution()
    
    # 顯示差異
    console.print("\n" + "="*80 + "\n")
    viz.show_diff(0, 1)  # A vs B
    
    console.print("\n" + "="*80 + "\n")
    viz.show_diff(1, 2)  # B vs C
    
    # 並排比較
    console.print("\n" + "="*80 + "\n")
    viz.show_side_by_side(0, 2)  # A vs C
    
    # 相似度分析
    console.print("\n" + "="*80 + "\n")
    console.print("[bold]Context A vs Context C:[/bold]")
    viz.show_similarity(0, 2)
    
    # 回應比較
    viz.show_response_comparison()
    
    # 導出
    viz.export_comparison()


if __name__ == "__main__":
    demo_context_engineering()
