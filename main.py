import argparse
import asyncio

from rich.console import Console
from rich.table import Table

from hackerjobs.JobPostingFetcher import JobPostingFetcher
from hackerjobs.JobPostingIndex import JobPostingIndex
from hackerjobs.Posting import Posting

URL = "https://news.ycombinator.com/item"


def print_search_results(results: list[Posting]):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Link", style="dim", width=46)
    table.add_column("Posting Snippet", width=75)

    for result in results:
        table.add_row(f"{URL}?id={result['id']}",
                      result["text"].replace("\n", " ").strip()[:75])

    console.print(f"Found {len(results)} postings\n")
    console.print(table)


async def main(reindex: bool,
               job_posting_id: int,
               query_text: str,
               search_count: int) -> None:
    index_dir = f"hackernews_job_postings_{job_posting_id}.db"

    with JobPostingIndex(index_dir) as index:
        if reindex:
            index.drop_table()

        if not index.table_exists():
            print("Indexing job postings")
            job_posting_fetcher = JobPostingFetcher(job_posting_id)
            results = await job_posting_fetcher.get_posting()
            await job_posting_fetcher.close()
            index.initialize()
            index.index_postings(results)

            print("Done indexing")

        search_results = index.search(query_text, search_count)
        print_search_results(search_results)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reindex", action="store_true",
                        help="Drop the table and index jobs again")
    parser.add_argument("-j", "--job-posting-id", type=int,
                        default=35424807, help="Job posting ID from HackerNews")
    parser.add_argument("-q", "--query-text", default="python AND remote",
                        help="Text to search for in postings")
    parser.add_argument("-c", "--search-count", type=int,
                        default=100, help="Count of posting to be returned")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args.reindex,
                     args.job_posting_id,
                     args.query_text,
                     args.search_count))
