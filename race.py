from enum import Enum, auto
import logging
import re
import uuid


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
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return "{name}: {url}".format(name=self.name, url=self.url)

    def site(self):
        return Site.from_url(self.url)

    def niconico_community_id(self):
        if self.site() is Site.NICONICO:
            return re.search("co[0-9]+", self.url).group()
        return None

    def template(self, niconico=False):
        niconico_url = self.site() is Site.NICONICO

        url = self.niconico_community_id() if niconico and niconico_url else self.url
        return "{name}さん {url}".format(name=self.name, url=url)


class Race:
    hash_len = 8

    def __init__(self, timestamp):
        self.uuid = uuid.uuid4()
        self.timestamp = timestamp
        self.runner = {}
        self.mirror = {}

    def entry(self, name, url):
        self.runner[name] = Runner(name, url)

    def entry_mirror(self, name, url):
        self.runner[name] = Runner(name, url)

    def retire(self, name):
        del self.runner[name]

    def hash(self):
        return "#" + str(self.uuid)[:Race.hash_len]

    def match_hash(self, hash):
        return hash == self.hash()

    def timestamp_str(self):
        return self.timestamp.strftime("%Y/%m/%d %H:%M")

    def overview(self):
        return "{}: {}".format(self.hash(), self.timestamp_str())

    def template(self, niconico=False):
        nl = "<br >\n" if niconico else "\n"

        s = self.hash() + nl
        s += self.timestamp_str() + "~" + nl

        sorted_runner = sorted(self.runner.items())
        s += "【走者一覧】{}".format(nl)
        for _, runner in sorted_runner:
            s += runner.template() + nl

        if any(self.mirror):
            sorted_mirror = sorted(self.mirror.items())
            s += "【ミラー】" + nl
            for _, mirror in sorted_mirror:
                s += mirror.template(niconico) + nl

        return s
