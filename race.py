from enum import Enum, auto
import logging
import re
import uuid
from hashids import Hashids


class Site(Enum):
    YOUTUBE = auto(),
    TWITCH = auto(),
    NICONICO = auto(),

    @classmethod
    def from_url(cls, url):
        if url.startswith("https://www.youtube.com/channel/"):
            return cls.YOUTUBE
        elif url.startswith("https://www.twitch.tv/"):
            return cls.TWITCH
        elif url.startswith("https://com.nicovideo.jp/community/"):
            return cls.NICONICO
        return None


class Runner:
    def __init__(self, name, id, url):
        self.name = name
        self.id = id
        self.url = url

    def __str__(self):
        return "{name}: {url}".format(name=self.name, url=self.url)

    def site(self):
        return Site.from_url(self.url)

    def niconico_community_id(self):
        if self.site() is Site.NICONICO:
            return re.search("co[0-9]+", self.url).group()
        return None

    def template(self):
        return "{name}さん {url}".format(name=self.name, url=self.url)


class Race:
    hash_len = 8

    def __init__(self, id, channel_id, start_time=None):
        self.id = id
        self.channel_id = channel_id
        self.start_time = start_time
        self.runner = {}
        self.mirror = {}
        self.note = None

    def entry(self, name, id, url):
        self.runner[name] = Runner(name, id, url)

    def entry_mirror(self, name, id, url):
        self.runner[name] = Runner(name, id, url)

    def retire(self, name):
        del self.runner[name]

    def hash(self):
        hi = Hashids(min_length=6)
        return hi.encode(self.id)

    def match_hash(self, hash):
        return hash == self.hash()

    def start_time_str(self):
        return self.start_time.strftime("%Y/%m/%d %H:%M")

    def overview(self):
        return "{}: {}".format(self.hash(), self.start_time_str())

    def template(self, html_mode=False):
        nl = "<br >\n" if html_mode else "\n"

        s = self.hash() + nl
        s += self.start_time_str() + "~" + nl

        sorted_runner = sorted(self.runner.items())
        s += "【走者一覧】{}".format(nl)
        for _, runner in sorted_runner:
            s += runner.template() + nl

        if any(self.mirror):
            sorted_mirror = sorted(self.mirror.items())
            s += "【ミラー】" + nl
            for _, mirror in sorted_mirror:
                s += mirror.template() + nl

        return s
