from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from hackerjobs.Posting import Posting

URL = "https://news.ycombinator.com/item"


def print_search_query_info(query_text: str, result_count: int, console: Console):
    """Print formatted search query information using Rich styling."""
    panel_content = (
        f'[bold white]Query:[/bold white] [yellow]"{query_text}"[/yellow]\n'
        f"[bold white]Results:[/bold white] "
        f"[cyan]{result_count}[/cyan] postings"
    )
    query_panel = Panel(
        panel_content,
        title="[bold blue]🔍 Search Results[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(query_panel)
    console.print()


def print_search_results(
    results: list[Posting], console: Console, show_age: bool = True
):
    """Print formatted search results using Rich styling."""
    if not results:
        console.print("[dim]No results found for your search query.[/dim]")
        return

    # Create styled table with full URL, date, and spacious preview
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("🔗 Link", style="cyan", no_wrap=True)
    table.add_column("📅 Date", style="yellow", width=12, justify="center")
    table.add_column("📝 Job Posting", style="white")

    for result in results:
        # Create full clickable URL
        url = f"{URL}?id={result.id}"
        url_text = f"[link={url}][cyan]{url}[/link]"

        # Format date
        date_text = f"[bold]{result.age_text}[/bold]"

        # Clean and truncate text preview to fit nicely
        preview = result.text.replace("\n", " ").strip()
        if len(preview) > 75:
            preview = preview[:72] + "..."
        preview_text = f"[dim]{preview}[/dim]"

        table.add_row(url_text, date_text, preview_text)

    console.print(table)
    console.print()  # Add some spacing
