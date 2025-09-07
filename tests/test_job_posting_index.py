from hackerjobs.JobPostingIndex import JobPostingIndex
from hackerjobs.Posting import Posting

POSTINGS: list[Posting] = [
    Posting(
        id="1",
        text="Python developer - Remote",
        by="user1",
        timestamp=int(__import__("time").time()) - 86400,
    ),  # 1 day ago
    Posting(
        id="2",
        text="Remote work available - Python",
        by="user2",
        timestamp=int(__import__("time").time()) - 172800,
    ),  # 2 days ago
    Posting(
        id="3",
        text="Front-end developer",
        by="user3",
        timestamp=int(__import__("time").time()) - 259200,
    ),  # 3 days ago
    Posting(
        id="4",
        text="Python developer",
        by="user4",
        timestamp=int(__import__("time").time()) - 345600,
    ),  # 4 days ago
    Posting(
        id="5",
        text="Boston Onsite - Python",
        by="user5",
        timestamp=int(__import__("time").time()) - 432000,
    ),  # 5 days ago
]


def test_index_postings_and_search() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND remote"
        search_results = index.search(query_text, limit=5)
        search_results_ids = [posting.id for posting in search_results]

        assert len(search_results) == 2
        assert "1" in search_results_ids
        assert "2" in search_results_ids


def test_not_search() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python NOT remote"
        search_results = index.search(query_text, limit=5)
        search_results_ids = [posting.id for posting in search_results]

        assert len(search_results) == 2
        assert "4" in search_results_ids
        assert "5" in search_results_ids


def test_complex_search() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND Boston NOT remote"
        search_results = index.search(query_text, limit=5)
        search_results_ids = [posting.id for posting in search_results]

        assert len(search_results) == 1
        assert "5" in search_results_ids


def test_table_exists() -> None:
    with JobPostingIndex(":memory:") as index:
        assert not index.table_exists()

        index.initialize()
        assert index.table_exists()

        index.drop_table()
        assert not index.table_exists()


def test_reindex_postings() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND remote"
        search_results = index.search(query_text, limit=5)
        search_results_ids = [posting.id for posting in search_results]

        assert len(search_results) == 2
        assert "1" in search_results_ids
        assert "2" in search_results_ids

        # Drop table and reindex with a new set of postings
        new_postings: list[Posting] = [
            Posting(
                id="6",
                text="JavaScript developer",
                by="user6",
                timestamp=int(__import__("time").time()) - 518400,
            ),  # 6 days ago
            Posting(
                id="7",
                text="Java developer",
                by="user7",
                timestamp=int(__import__("time").time()) - 604800,
            ),  # 7 days ago
        ]

        index.drop_table()
        index.initialize()
        index.index_postings(new_postings)

        # Test search with the new postings
        query_text = "JavaScript"
        search_results = index.search(query_text, limit=5)
        search_results_ids = [posting.id for posting in search_results]

        assert len(search_results) == 1
        assert "6" in search_results_ids


def test_search_limit() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test that limit parameter works correctly
        # "python" should match postings 1, 2, 4, 5 (4 total)
        query_text = "python"
        search_results = index.search(query_text, limit=2)
        search_results_ids = [posting.id for posting in search_results]

        # Should only return 2 results due to limit
        assert len(search_results) == 2
        # Should return the most recent ones (sorted by time DESC)
        assert "1" in search_results_ids  # 1 day ago
        assert "2" in search_results_ids  # 2 days ago


def test_search_days_filter() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test that days filter works correctly
        # With days=3, should only get postings from last 3 days
        query_text = "python"
        search_results = index.search(query_text, days=3, limit=10)
        search_results_ids = [posting.id for posting in search_results]

        # Should only return postings from last 3 days that match "python"
        # Posting 1 (1 day ago) and 2 (2 days ago) should match
        # Posting 4 (4 days ago) and 5 (5 days ago) should be filtered out
        assert len(search_results) == 2
        assert "1" in search_results_ids  # 1 day ago
        assert "2" in search_results_ids  # 2 days ago
        assert "4" not in search_results_ids  # 4 days ago (filtered out)
        assert "5" not in search_results_ids  # 5 days ago (filtered out)


def test_search_days_filter_strict() -> None:
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test with days=1 to be very strict
        query_text = "python"
        search_results = index.search(query_text, days=1, limit=10)
        search_results_ids = [posting.id for posting in search_results]

        # Should only return postings from last 1 day
        # Only posting 1 (1 day ago) should match
        assert len(search_results) == 1
        assert "1" in search_results_ids  # 1 day ago
        assert "2" not in search_results_ids  # 2 days ago (filtered out)
