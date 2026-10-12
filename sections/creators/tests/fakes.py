"""Second adapters for the two real seams (platform, channel), so tests run offline and instantly."""
from creatorops.platforms import PlatformError, Post, Profile


class FakePlatform:
    def __init__(self, name="tiktok"):
        self.name = name
        self.profiles, self.posts, self.comment_map = {}, {}, {}

    def profile(self, username):
        if username not in self.profiles:
            raise PlatformError("not found")
        return self.profiles[username]

    def recent_posts(self, username, n=20):
        return list(self.posts.get(username, []))[:n]

    def post(self, url):
        for posts in self.posts.values():
            for p in posts:
                if p.url == url:
                    return p
        raise PlatformError("no post")

    def comments(self, url, n=50):
        return self.comment_map.get(url, [])[:n]


class FakeChannel:
    def __init__(self, name):
        self.name, self.sent = name, []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))
        return f"fake-{len(self.sent)}"


__all__ = ["FakePlatform", "FakeChannel", "Post", "Profile"]
