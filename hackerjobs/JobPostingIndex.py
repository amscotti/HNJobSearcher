import os

from whoosh import index
from whoosh.analysis import StemmingAnalyzer, KeywordAnalyzer
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.qparser import QueryParser


class JobPostingIndex:
    SCHEMA = Schema(id=ID(stored=True, unique=True),
                    text=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                    by=KEYWORD(analyzer=KeywordAnalyzer(), stored=True))

    def __init__(self, index_dir):
        self.index_dir = index_dir

    def index_postings(self, postings) -> None:
        ix = index.create_in(self.index_dir, self.SCHEMA)

        with ix.writer() as writer:
            for job in postings:
                if job:
                    writer.add_document(**job)

    def does_index_exist(self) -> bool:
        return os.path.exists(self.index_dir)

    def create_index(self) -> None:
        if not self.does_index_exist():
            os.makedirs(self.index_dir)

    def search(self, query_text: str, search_count: int) -> list[dict[str, str]]:
        ix = index.open_dir(self.index_dir)
        parser = QueryParser("text", schema=ix.schema)

        with ix.searcher() as searcher:
            query = parser.parse(query_text)
            results = searcher.search(query, limit=search_count)

            results_list: list[dict[str, str]] = [
                {"id": result['id'], "text": result["text"]}
                for result in results]

        return results_list
