from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Repository:
    name: str
    full_name: str
    stars: int
    forks: int
    language: Optional[str]
    updated_at: str
    html_url: str


@dataclass
class UserProfile:
    login: str
    name: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    blog: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    followers: int
    following: int
    public_repos: int
    public_gists: int
    created_at: str
    updated_at: str
    repositories: List[Repository] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "login": self.login,
            "name": self.name,
            "bio": self.bio,
            "company": self.company,
            "location": self.location,
            "blog": self.blog,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "followers": self.followers,
            "following": self.following,
            "public_repos": self.public_repos,
            "public_gists": self.public_gists,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
