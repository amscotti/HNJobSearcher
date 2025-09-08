from datetime import datetime
from pydantic import BaseModel, Field


class Posting(BaseModel):
    id: str
    text: str
    by: str
    timestamp: int = Field(description="Unix timestamp from HN API")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def age_days(self) -> int:
        """Calculate days since posting (using HN timestamp)"""
        posting_time = datetime.fromtimestamp(self.timestamp)
        return (datetime.now() - posting_time).days

    @property
    def age_text(self) -> str:
        """Human-readable age description"""
        days = self.age_days
        if days == 0:
            return "today"
        elif days == 1:
            return "1 day ago"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            return f"{days} days ago"

    @property
    def is_recent(self) -> bool:
        """Check if posting is within last 7 days"""
        return self.age_days <= 7
