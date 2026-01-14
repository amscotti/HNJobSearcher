import argparse
import asyncio

from rich.console import Console

from hackerjobs.HNSearch import get_latest_hiring_post_id
from hackerjobs.JobPostingFetcher import JobPostingFetcher
from hackerjobs.JobPostingIndex import JobPostingIndex
from hackerjobs.output import print_search_results, print_search_query_info

URL = "https://news.ycombinator.com/item"
DEFAULT_QUERY_TEXT = "python AND remote"


async def main(
    reindex: bool,
    job_posting_id: int | None,
    query_text: str,
    search_count: int,
    days: int,
) -> None:
    console = Console()

    if job_posting_id is None:
        with console.status(
            "[bold blue]Searching for latest job posting...[/bold blue]", spinner="dots"
        ):
            job_posting_id = await get_latest_hiring_post_id()
        console.print(f"[blue]Using latest job posting: {job_posting_id}[/blue]")

    index_dir = f"hackernews_job_postings_{job_posting_id}.db"

    with JobPostingIndex(index_dir) as index:
        if reindex:
            msg = "[yellow]🔄 Reindexing job postings...[/yellow]"
            console.print(msg)
            console.print(msg)
            index.drop_table()

        if not index.table_exists():
            status_msg = "[bold green]🔄 Indexing job postings...[/bold green]"
            with console.status(status_msg, spinner="dots"):
                job_posting_fetcher = JobPostingFetcher(job_posting_id)
                results = await job_posting_fetcher.get_posting()
                await job_posting_fetcher.close()
                index.initialize()
                index.index_postings(results)

            success_msg = (
                f"[green]✅ Successfully indexed {len(results)} job postings![/green]"
            )
            console.print(success_msg)

        search_results = index.search(
            query_text=query_text, days=days, limit=search_count, sort_by_time=True
        )

        print_search_query_info(query_text, len(search_results), console)
        print_search_results(search_results, console, show_age=True)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--reindex",
        action="store_true",
        help="Drop the table and index jobs again",
    )
    parser.add_argument(
        "-j",
        "--job-posting-id",
        type=int,
        default=None,
        help="Job posting ID from HackerNews (auto-detects latest if not provided)",
    )
    parser.add_argument(
        "-q",
        "--query-text",
        default=DEFAULT_QUERY_TEXT,
        help="Text to search for in postings",
    )
    parser.add_argument(
        "-c",
        "--search-count",
        type=int,
        default=100,
        help="Count of posting to be returned",
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=30,
        help="Filter postings from last N days (default: 30)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(
        main(
            args.reindex,
            args.job_posting_id,
            args.query_text,
            args.search_count,
            args.days,
        )
    )
