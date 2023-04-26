from hackerjobs.JobPostingIndex import JobPostingIndex

POSTINGS = [
    {"id": "1", "text": "Python developer - Remote", "by": "user1"},
    {"id": "2", "text": "Remote work available - Python", "by": "user2"},
    {"id": "3", "text": "Front-end developer", "by": "user3"},
    {"id": "4", "text": "Python developer", "by": "user4"},
    {"id": "5", "text": "Boston Onsite - Python", "by": "user5"}
]


def test_index_postings_and_search():
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND remote"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting["id"] for posting in search_results]

        assert len(search_results) == 2
        assert "1" in search_results_ids
        assert "2" in search_results_ids


def test_not_search():
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python NOT remote"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting["id"] for posting in search_results]

        assert len(search_results) == 2
        assert "4" in search_results_ids
        assert "5" in search_results_ids


def test_complex_search():
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND Boston NOT remote"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting["id"] for posting in search_results]

        assert len(search_results) == 1
        assert "5" in search_results_ids


def test_table_exists():
    with JobPostingIndex(":memory:") as index:
        assert not index.table_exists()

        index.initialize()
        assert index.table_exists()

        index.drop_table()
        assert not index.table_exists()


def test_reindex_postings():
    with JobPostingIndex(":memory:") as index:
        index.initialize()
        index.index_postings(POSTINGS)

        # Test search with matching query
        query_text = "python AND remote"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting["id"] for posting in search_results]

        assert len(search_results) == 2
        assert "1" in search_results_ids
        assert "2" in search_results_ids

        # Drop table and reindex with a new set of postings
        new_postings = [
            {"id": "6", "text": "JavaScript developer", "by": "user6"},
            {"id": "7", "text": "Java developer", "by": "user7"}
        ]

        index.drop_table()
        index.initialize()
        index.index_postings(new_postings)

        # Test search with the new postings
        query_text = "JavaScript"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting["id"] for posting in search_results]

        assert len(search_results) == 1
        assert "6" in search_results_ids
