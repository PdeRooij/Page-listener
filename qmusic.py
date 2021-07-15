import requests, dateutil.parser


class Qmusic:
    def __init__(self):
        self.__achannels__ = self.__channels__()

    def __channels__(self):
        return requests.get("https://api.qmusic.nl/2.4/app/channels").json()["data"]

    def get_channel(self, slug="qmusic_nl"):
        """Gets the channel from the slug.
        :param slug: The slug of the channel, defaults to "qmusic_nl"
        :type slug: str, optional
        :return: Returns a Channel object or None if it isn't available
        :rtype: :class:`Channel`
        """
        for channel in self.__achannels__:
            if channel["data"]["id"] == slug:
                return Channel(channel)
        return None


class Channel:
    def __init__(self, json):
        self.json = json
        self.__data__ = self.json["data"]
        self.__apiurl__ = self.__api_url__()
        self.__r__ = self.__req__()

    def __req__(self):
        return requests.get(self.__apiurl__ + "/tracks/plays?limit=1").json()["played_tracks"][0]

    def current_song(self):
        """Gets the current song playing on the channel.
        :return: Returns a Song object
        :rtype: :class:`Song`
        """
        req = self.__req__()

        if "next" in req:
            return Song(req.pop("next"), self.__apiurl__)
        else:
            return Song(req, self.__apiurl__)

    def next_song(self):
        """Gets the next song on the channel. The next song might not be available, in that case it returns None.
        :return: Returns a Song object if the next song is available or None if it isn't available
        :rtype: :class:`Song`, bool
        """
        req = self.__req__()

        if "next" in req:
            return Song(req["next"], self.__apiurl__)
        else:
            return None

    def color(self):
        """Gets the colors of the channel
        :return: Returns a Color object
        :rtype: :class:`Color`
        """
        return Color(self.json["color"])

    def slug(self):
        """Gets the slug of the channel
        :return: Returns a string with the slug
        :rtype: str
        """
        return self.__data__["id"]

    def background_image(self):
        """Gets an url of the background image of the channel
        :return: Returns a string with the background image url
        :rtype: str
        """
        return self.__data__["background_image"]

    def name(self):
        """Gets the name of the channel
        :return: Returns a string with the name of the channel
        :rtype: str
        """
        return self.__data__["name"]

    def __api_url__(self):
        return "http://" + self.__data__["api_url"] + "/2.4"

    def station_id(self):
        """Gets the station id of the channel
        :return: Returns a string with the station id
        :rtype: str
        """
        return self.__data__["station_id"]

    def logo(self):
        """Gets the logo url of the channel
        :return: Returns a string with the logo url
        :rtype: str
        """
        return Logo(self.__data__["logo"])

    def streams(self):
        """Gets the logo url of the channel
        :return: Returns a string with the logo url
        :rtype: str
        """
        return Streams(self.__data__["streams"])

    def search_terms(self):
        """Gets the slug of the channel
        :return: Returns a string with the slug
        :rtype: str
        """
        return self.__data__["search_terms"]


class Streams:
    def __init__(self, json):
        self.json = json

    def aac(self):
        """A list with Stream objects that contains the source url and extra information
        :return: Returns a list with Stream objects
        :rtype: list, :class:`Stream`
        """
        return [Stream(aac) for aac in self.json["aac"]]

    def mp3(self):
        """A list with Stream objects that contains the source url and extra information
        :return: Returns a list with Stream objects
        :rtype: list, :class:`Stream`
        """
        return [Stream(mp3) for mp3 in self.json["mp3"]]

    def video(self):
        """A list with Stream objects that contains the source url and extra information
        :return: Returns a list with Stream objects
        :rtype: list, :class:`Stream`
        """
        return [Stream(video) for video in self.json["video"]]

    def hls(self):
        """A list with Stream objects that contains the source url and extra information
        :return: Returns a list with Stream objects
        :rtype: list, :class:`Stream`
        """
        return [Stream(hls) for hls in self.json["hls"]]

    def radioplayer_id(self):
        """A list with Stream objects that contains the source url and extra information
        :return: Returns a Stream object
        :rtype: list, :class:`Stream`
        """
        return [Stream(radioplayer_id) for radioplayer_id in self.json["radioplayerId"]]

    def mobile(self):
        """A list with Mobile objects that contain the audio url, video url and the live url
        :return: Returns a Mobile object
        :rtype: :class:`Mobile`
        """
        return Mobile(self.json["mobile"])

    def android(self):
        """A list with Mobile objects that contain the high quality url, low quality url and the video url
        :return: Returns an Android object
        :rtype: :class:`Android`
        """
        return Android(self.json["android"])

    def iphone(self):
        """A list with Mobile objects that contain the live url and video url
        :return: Returns an Iphone object
        :rtype: :class:`Iphone`
        """
        return Iphone(self.json["iphone"])


class Mobile:
    def __init__(self, json):
        self.json = json

    def audio(self):
        """Gets the audio url for mobile
        :return: Returns a string with the audio url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["audio"] if "audio" in self.json else None

    def video(self):
        """Gets the video url for mobile
        :return: Returns a string with the video url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["video"] if "video" in self.json else None

    def live(self):
        """Gets the live url for mobile
        :return: Returns a string with the live url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["live"] if "live" in self.json else None


class Android:
    def __init__(self, json):
        self.json = json

    def high(self):
        """Gets the high quality url for Android
        :return: Returns a string with the high quality url or None if it isn't available
        :rtype: str, bool;
        """
        return self.json["high"] if "high" in self.json else None

    def low(self):
        """Gets the low quality url for Android
        :return: Returns a string with the low quality url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["low"] if "low" in self.json else None

    def video(self):
        """Gets the video url for Android
        :return: Returns a string with the video url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["video"] if "video" in self.json else None


class Iphone:
    def __init__(self, json):
        self.json = json

    def live(self):
        """Gets the live url for Iphone
        :return: Returns a string with the live url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["live"] if "live" in self.json else None

    def video(self):
        """Gets the video url for Iphone
        :return: Returns a string with the video url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["video"] if "video" in self.json else None


class Stream:
    def __init__(self, json):
        self.json = json

    def source(self):
        """Gets the source url of the Stream
        :return: Returns a string with the source url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["source"]

    def extra(self):
        """Gets a list with extra information about the Stream
        :return: Returns a list with extra information about the Stream or None if it isn't available
        :rtype: list, bool
        """
        return self.json["extra"]


class Logo:
    def __init__(self, json):
        self.json = json

    def active_android_url(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["active_android_url"] if "active_android_url" in self.json else None

    def active_iphone_url(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["active_iphone_url"] if "active_iphone_url" in self.json else None

    def inactive_android_url(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["inactive_android_url"] if "inactive_android_url" in self.json else None

    def inactive_iphone_url(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["inactive_iphone_url"] if "inactive_iphone_url" in self.json else None

    def app_card(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_card"] if "app_card" in self.json else None

    def app_player_bg_phone(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_bg_phone"] if "app_player_bg_phone" in self.json else None

    def app_player_bg_tablet(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_bg_tablet"] if "app_player_bg_tablet" in self.json else None

    def app_player_icon(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_icon"] if "app_player_icon" in self.json else None

    def app_player_thumbnail(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_thumbnail"] if "app_player_thumbnail" in self.json else None

    def app_player_small(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_small"] if "app_player_small" in self.json else None

    def app_player_header(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_player_header"] if "app_player_header" in self.json else None

    def app_square(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_square"] if "app_square" in self.json else None

    def appletv_background(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["appletv_background"] if "appletv_background" in self.json else None

    def app_messages_avatar(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["app_messages_avatar"] if "app_messages_avatar" in self.json else None

    def radioplayer_cover(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["radioplayer_cover"] if "radioplayer_cover" in self.json else None

    def radioplayer_banner(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["radioplayer_banner"] if "radioplayer_banner" in self.json else None

    def site_logo(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["site_logo"] if "site_logo" in self.json else None

    def site_background(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["site_background"] if "site_background" in self.json else None

    def homepage_banner(self):
        """
        :return: Returns a string with the image url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["homepage_banner"] if "homepage_banner" in self.json else None


class Color:
    def __init__(self, json):
        self.json = json

    def background(self):
        """Gets a hex string with the background color
        :return: Returns a string with the background color hex
        :rtype: str
        """
        return self.json["background"]

    def foreground(self):
        """Gets a hex string with the foreground color
        :return: Returns a string with the foreground color hex
        :rtype: str
        """
        return self.json["foreground"]

    def extra(self):
        """Gets a hex string with an extra color
        :return: Returns a string with an extra color hex or #ffffff if it isn't available
        :rtype: str
        """
        return self.json["extra"]


class Song:
    def __init__(self, json, BASE):
        self.json = json
        self.BASE = BASE

    def played_at(self):
        """Gets the timestamp of when the song started playing
        :return: Return a datetime.datetime object
        :rtype: datetime.datetime
        """
        return dateutil.parser.parse(self.json["played_at"])

    def slug(self):
        """Gets the slug of the song. E.g. all-i-want-for-christmas-is-you
        :return: Return a string with the slug
        :rtype: str
        """
        return self.json["slug"]

    def title(self):
        """Gets the title of the song.
        :return: Return a string with the title
        :rtype: str
        """
        return self.json["title"]

    def selector_code(self):
        """Gets the selector code of a song
        :return: Return a string with the selector code
        :rtype: str
        """
        return self.json["selector_code"]

    def release_year(self):
        """Gets the release year of a song
        :return: Return a string with the release year or None if it isn't available
        :rtype: str, bool
        """
        return self.json["release_year"] if "release_year" in self.json else None

    def affiliate_url(self):
        """Gets the affiliate url of a song
        :return: Return a string with the affiliate url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["affiliate_url"] if "affiliate_url" in self.json else None

    def thumbnail_url(self):
        """Gets the thumbnail url of a song
        :return: Return a string with the thumbnail url
        :rtype: str
        """
        return self.BASE[:-3] + "cover" + self.json["thumbnail"]

    def spotify_url(self):
        """Gets the spotify url of a song
        :return: Return a string with the spotify url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["spotify_url"] if "spotify_url" in self.json else None

    def youtube_url(self):
        """Gets the youtube url of a song
        :return: Return a string with the spotiyoutubefy url or None if it isn't available
        :rtype: str, bool
        """
        return "https://www.youtube.com/watch?v=" + self.json["youtube_ids"][
            "default"] if "youtube_ids" in self.json and "default" in self.json["youtube_ids"] else None

    def preview_url(self):
        """Gets the preview url of a song. IT gives an url with the mp3 file of the first 30 seconds of the song.
        :return: Return a string with the preview url or None if it isn't available
        :rtype: str, bool
        """
        return self.json["hooks"]["m4a"] if "m4a" in self.json["hooks"] else None

    def artist(self):
        """Gets the artist of a song
        :return: Return an Artist object
        :rtype: :class:`Artist`
        """
        return Artist(self.json["artist"], self.BASE)

    def featuring_artists(self):
        """Gets the featuring artists of a song
        :return: Return a list with Artist objects of the featuring artists.
        :rtype: list, :class:`Artist`
        """
        return [Artist(artist['artist'], self.BASE) for artist in self.json["sub_artists"]]


class Artist:
    def __init__(self, json, BASE):
        self.json = json
        self.BASE = BASE

    def id_code(self):
        """Gets the id/selector_code of the artist
        :return: Returns an int with the id of the artist
        :rtype: int
        """
        return self.json["id"]

    def name_all_artist(self):
        """Gets the string with all the names of the song artists. E.g.: 'LOST FREQUENCIES & MATHIEU KOSS'
        :return: Returns a string with all the song artists names
        :rtype: str
        """
        return self.json["name"]

    def name_main_artist(self):
        """Gets the string with the name of the artist. E.g.: 'LOST FREQUENCIES'
        :return: Returns a string with the song artist name
        :rtype: str
        """
        return self.json["original_name"]

    def slug(self):
        """Gets the slug of the artist
        :return: Returns a string with the slug of the artist
        :rtype: str
        """
        return self.json["slug"]

    def bio(self):
        """Gets the bio of the artist
        :return: Returns a string with the bio of the artist
        :rtype: str
        """
        return self.json["bio"]

    def social_medias(self):
        """Gets the social medias of the artist
        :return: Returns a dict with the social medias. E.g. {'facebook_url': 'https://www.facebook.com/RolfSanchez', 'twitter_url': 'https://twitter.com/rolfsanchez', 'instagram_url': 'https://www.instagram.com/rolfsanchez/', 'website': 'https://rolf-music.com/'}
        :rtype: dict
        """
        possible_sm = ["facebook_url", "twitter_url", "instagram_url", "website"]
        social_medias = {}
        for sm in possible_sm:
            if sm in self.json:
                social_medias[sm] = self.json[sm]
        return social_medias

    def photo(self):
        """Gets the photo url of the artist
        :return: Returns a string with the photo url of the artist
        :rtype: str
        """
        return self.BASE + self.json["photo"]

    def country_code(self):
        """Gets the country code from where the artist is``
        :return: Returns a string with the country code from where the artist is or None if it isn't available
        :rtype: str, bool
        """
        return self.json["country"]["code"] if "country" in self.json else None

    def country_name(self):
        """Gets the country name from where the artist is``
        :return: Returns a string with the country name from where the artist is or None if it isn't available
        :rtype: str, bool
        """
        return self.json["country"]["name"] if "name" in self.json else None


class Edition:
    def __init__(self, json):
        self.json = json

    def song_position(self):
        """The position of the song in the edition
        :return: Returns an int with the position of the song in the edition
        :rtype: int
        """
        return self.json["position"]

    def release_year(self):
        """The release year of the edition
        :return: Returns a string with the release year of the edition
        :rtype: str
        """
        return self.json["edition"]["name"]

    def name(self):
        """The name of the edition
        :return: Returns a string with the name of the edition
        :rtype: str
        """
        return self.json["list"]["name"]