from tempfile import TemporaryDirectory
from hackerjobs.JobPostingIndex import JobPostingIndex


def test_index_postings_and_search():
    postings = [
        {"id": "1", "text": "Python developer - Remote", "by": "user1"},
        {"id": "2", "text": "Remote work available - Python", "by": "user2"},
        {"id": "3", "text": "Front-end developer", "by": "user3"},
        {"id": "4", "text": "Python developer", "by": "user4"}
    ]

    with TemporaryDirectory() as temp_dir:
        index = JobPostingIndex(temp_dir)
        index.create_index()

        index.index_postings(postings)

        # Test search with matching query
        query_text = "python AND remote"
        search_results = index.search(query_text, search_count=5)
        search_results_ids = [posting['id'] for posting in search_results]

        assert len(search_results) == 2
        assert "1" in search_results_ids
        assert "2" in search_results_ids
