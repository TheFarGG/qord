# MIT License

# Copyright (c) 2022 Izhar Ahmad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from qord.models.base import BaseModel
from qord.enums import ChannelType
from qord._helpers import get_optional_snowflake, parse_iso_timestamp, EMPTY

import typing

if typing.TYPE_CHECKING:
    from datetime import datetime
    from qord.models.guilds import Guild


class GuildChannel(BaseModel):
    r"""The base class for channel types that are associated to a specific guild.

    For each channel types, Library provides separate subclasses that implement
    related functionality for that channel type.

    Following classes currently inherit this class:

    - :class:`TextChannel`
    - :class:`NewsChannel`
    - :class:`CategoryChannel`
    - :class:`VoiceChannel`
    - :class:`StageChannel`

    Attributes
    ----------
    guild: :class:`Guild`
        The guild associated to this channel.
    id: :class:`builtins.int`
        The ID of this channel.
    type: :class:`builtins.int`
        The type of this channel. See :class:`ChannelType` for more information.
    name: :class:`builtins.str`
        The name of this channel.
    position: :class:`builtins.int`
        The position of this channel in channels list.
    parent_id: :class:`builtins.int`
        The ID of category that this channel is associated to.
    """

    if typing.TYPE_CHECKING:
        guild: Guild
        id: int
        type: int
        name: str
        position: int
        nsfw: bool
        parent_id: typing.Optional[int]

    __slots__ = (
        "_client",
        "_rest",
        "guild",
        "id",
        "type",
        "name",
        "position",
        "parent_id"
    )

    def __init__(self, data: typing.Dict[str, typing.Any], guild: Guild) -> None:
        self.guild = guild
        self._client = guild._client
        self._rest = guild._rest
        self._update_with_data(data)

    def _update_with_data(self, data: typing.Dict[str, typing.Any]) -> None:
        self.id = int(data["id"])
        self.type = int(data["type"])
        self.name = data["name"]
        self.position = data.get("position", 1)
        self.parent_id = get_optional_snowflake(data, "parent_id")

    @property
    def mention(self) -> str:
        r"""The string used for mentioning the channel in Discord client.

        Returns
        -------
        :class:`builtins.str`
        """
        return f"<#{self.id}>"

    async def delete(self, *, reason: str = None) -> None:
        r"""Deletes this channel.

        Requires the :attr:`~Permissions.manage_channels` on the bot
        in the parent :attr:`~GuildChannel.guild` for performing this action.

        Parameters
        ----------
        reason: :class:`builtins.str`
            The reason for performing this action.

        Raises
        ------
        HTTPForbidden
            Missing permissions.
        HTTPException
            Failed to perform this action.
        """
        await self._rest.delete_channel(channel_id=self.id, reason=reason)

    async def edit(self, **kwargs) -> None:
        raise NotImplementedError("edit() must be implemented by subclasses.")


class TextChannel(GuildChannel):
    r"""Represents a text messages based channel in a guild.

    This class inherits :class:`GuildChannel`.

    Attributes
    ----------
    topic: typing.Optional[:class:`builtins.str`]
        The topic of this channel.
    last_message_id: typing.Optional[:class:`builtins.int`]
        The ID of last message sent in this channel. Due to Discord limitation, This
        may not point to the actual last message of the channel.
    slowmode_delay: :class:`builtins.int`
        The slowmode per user (in seconds) that is set on this channel.
    nsfw: :class:`builtins.bool`
        Whether this channel is marked as NSFW.
    default_auto_archive_duration: :class:`builtins.int`
        The default auto archiving duration (in minutes) of this channel after which
        in active threads associated to this channel are automatically archived.
    last_pin_timestamp: typing.Optional[:class:`datetime.datetime`]
        The time when last pin in this channel was created.
    """

    if typing.TYPE_CHECKING:
        topic: typing.Optional[str]
        last_message_id: typing.Optional[int]
        last_pin_timestamp: typing.Optional[datetime]
        slowmode_delay: int
        default_auto_archive_duration: int

    __slots__ = (
        "topic",
        "slowmode_delay",
        "last_message_id",
        "default_auto_archive_duration",
        "nsfw",
        "last_pin_timestamp",
    )

    def _update_with_data(self, data: typing.Dict[str, typing.Any]) -> None:
        super()._update_with_data(data)

        self.topic = data.get("topic")
        self.last_message_id = get_optional_snowflake(data, "last_message_id")
        self.slowmode_delay = data.get("rate_limit_per_user", 0)
        self.default_auto_archive_duration = data.get("default_auto_archive_duration", 60)
        self.nsfw = data.get("nsfw", False)
        last_pin_timestamp = data.get("last_pin_timestamp")
        self.last_pin_timestamp = (
            parse_iso_timestamp(last_pin_timestamp) if last_pin_timestamp is not None else None
        )

    async def edit(
        self,
        *,
        name: str = EMPTY,
        type: int = EMPTY,
        position: int = EMPTY,
        nsfw: bool = EMPTY,
        parent: typing.Optional[CategoryChannel] = EMPTY,
        topic: typing.Optional[str] = EMPTY,
        slowmode_delay: typing.Optional[int] = EMPTY,
        default_auto_archive_duration: int = EMPTY,
        reason: str = None,
    ) -> None:
        r"""Edits the channel.

        This operation requires the :attr:`~Permissions.manage_channels` permission
        for the client user in the parent guild.

        When the request is successful, This channel is updated in place with
        the returned data.

        Parameters
        ----------
        name: :class:`builtins.str`
            The name of this channel.
        type: :class:`builtins.int`
            The type of this channel. In this case, Only :attr:`~ChannelType.NEWS`
            and :attr:`~ChannelType.TEXT` are supported.
        position: :class:`builtins.int`
            The position of this channel in channels list.
        parent: Optional[:class:`CategoryChannel`]
            The parent category in which this channel should be moved to. ``None`` to
            remove current category of this channel.
        nsfw: :class:`builtins.bool`
            Whether this channel is marked as NSFW.
        topic: Optional[:class:`builtins.str`]
            The topic of this channel. ``None`` can be used to remove the topic.
        slowmode_delay: Optional[:class:`builtins.int`]
            The slowmode delay of this channel (in seconds). ``None`` can be used to
            disable it. Cannot be greater then 21600 seconds.
        default_auto_archive_duration: :class:`builtins.int`
            The default auto archive duration after which in active threads
            are archived automatically (in minutes). Valid values are 60, 1440, 4320 and 10080.
        reason: :class:`builtins.str`
            The reason for performing this action that shows up on guild's audit log.

        Raises
        ------
        ValueError
            Invalid values supplied in some arguments.
        HTTPForbidden
            Missing permissions.
        HTTPException
            Failed to perform this action.
        """
        json = {}

        if name is not EMPTY:
            json["name"] = name

        if type is not EMPTY:
            if not type in (ChannelType.NEWS, ChannelType.TEXT):
                raise ValueError("type parameter only supports ChannelType.NEWS and TEXT.")

            json["type"] = type

        if position is not EMPTY:
            json["position"] = position

        if nsfw is not EMPTY:
            json["nsfw"] = nsfw

        if topic is not EMPTY:
            json["topic"] = topic

        if slowmode_delay is not EMPTY:
            if slowmode_delay is None:
                slowmode_delay = 0

            json["rate_limit_per_user"] = slowmode_delay

        if default_auto_archive_duration is not EMPTY:
            if not default_auto_archive_duration in (60, 1440, 4320, 10080):
                raise ValueError("Invalid value given for default_auto_archive_duration " \
                                "supported values are 60, 1440, 4320 and 10080.")

            json["default_auto_archive_duration"] = default_auto_archive_duration

        if parent is not EMPTY:
            json["parent_id"] = parent.id if parent is not None else None

        if json:
            data = await self._rest.edit_channel(
                channel_id=self.id,
                json=json,
                reason=reason
            )
            if data:
                self._update_with_data(data)


class NewsChannel(TextChannel):
    r"""Represents a news channel that holds other guild channels.

    This class inherits :class:`TextChannel` so all attributes of
    :class:`TextChannel` and :class:`GuildChannel` classes are valid here too.

    Currently this class has no extra functionality compared to :class:`TextChannel`.
    """

class CategoryChannel(GuildChannel):
    r"""Represents a category channel that holds other guild channels.

    This class inherits the :attr:`GuildChannel` class.
    """

    __slots__ = ()

    @property
    def channels(self) -> typing.List[GuildChannel]:
        r"""The list of channels associated to this category.

        Returns
        -------
        List[:class:`GuildChannel`]
        """
        channels = self.guild.cache.channels()
        return [channel for channel in channels if channel.parent_id == self.id]

    async def edit(
        self,
        *,
        name: str = EMPTY,
        position: int = EMPTY,
        reason: str = None,
    ) -> None:
        r"""Edits the channel.

        This operation requires the :attr:`~Permissions.manage_channels` permission
        for the client user in the parent guild.

        When the request is successful, This channel is updated in place with
        the returned data.

        Parameters
        ----------
        name: :class:`builtins.str`
            The name of this channel.
        position: :class:`builtins.int`
            The position of this channel in channels list.
        reason: :class:`builtins.str`
            The reason for performing this action that shows up on guild's audit log.

        Raises
        ------
        ValueError
            Invalid values supplied in some arguments.
        HTTPForbidden
            Missing permissions.
        HTTPException
            Failed to perform this action.
        """
        json = {}

        if name is not EMPTY:
            json["name"] = name

        if position is not EMPTY:
            json["position"] = position

        if json:
            data = await self._rest.edit_channel(
                channel_id=self.id,
                json=json,
                reason=reason
            )
            if data:
                self._update_with_data(data)


class VoiceChannel(GuildChannel):
    r"""Represents a voice channel in a guild.

    This class inherits the :class:`GuildChannel` class.

    Attributes
    ----------
    bitrate: :class:`builtins.int`
        The bitrate of this channel, in bits.
    user_limit: :class:`builtins.int`
        The number of users that can connect to this channel at a time. The
        value of ``0`` indicates that there is no limit set.
    rtc_region: Optional[:class:`builtins.str`]
        The string representation of RTC region of the voice channel. This
        is only available when a region is explicitly set. ``None`` indicates
        that region is chosen automatically.
    video_quality_mode: :class:`builtins.int`
        The video quality mode of this channel. See :class:`VideoQualityMode` for
        more information.
    """
    if typing.TYPE_CHECKING:
        bitrate: int
        user_limit: int
        video_quality_mode: int
        rtc_region: typing.Optional[str]

    __slots__ = (
        "bitrate",
        "rtc_region",
        "user_limit",
        "video_quality_mode",
    )

    def _update_with_data(self, data: typing.Dict[str, typing.Any]) -> None:
        super()._update_with_data(data)

        self.bitrate = data.get("bitrate") # type: ignore
        self.rtc_region = data.get("rtc_region")
        self.user_limit = data.get("user_limit", 0)
        self.video_quality_mode = data.get("video_quality_mode", 1)

    async def edit(
        self,
        *,
        name: str = EMPTY,
        position: int = EMPTY,
        bitrate: int = EMPTY,
        parent: typing.Optional[CategoryChannel] = EMPTY,
        rtc_region: typing.Optional[str] = EMPTY,
        user_limit: typing.Optional[int] = EMPTY,
        video_quality_mode: int = EMPTY,
        reason: str = None,
    ) -> None:
        r"""Edits the channel.

        This operation requires the :attr:`~Permissions.manage_channels` permission
        for the client user in the parent guild.

        When the request is successful, This channel is updated in place with
        the returned data.

        Parameters
        ----------
        name: :class:`builtins.str`
            The name of this channel.
        position: :class:`builtins.int`
            The position of this channel in channels list.
        parent: Optional[:class:`CategoryChannel`]
            The parent category in which this channel should be moved to. ``None`` to
            remove current category of this channel.
        bitrate: :class:`builtins.int`
            The bitrate of this channel in bits. This value can be in range of 8000
            and 96000 (128000 for VIP servers).
        rtc_region: Optional[:class:`builtins.str`]
            The RTC region of this voice channel. ``None`` can be used to
            set this to automatic selection of regions.
        user_limit: Optional[:class:`builtins.int`]
            The number of users that can connect to the channel at a time.
            ``None`` or ``0`` will remove the explicit limit allowing unlimited
            number of users.
        video_quality_mode: :class:`builtins.int`
            The video quality mode of the voice channel. See :class:`VideoQualityMode`
            for valid values.
        reason: :class:`builtins.str`
            The reason for performing this action that shows up on guild's audit log.

        Raises
        ------
        ValueError
            Invalid values supplied in some arguments.
        HTTPForbidden
            Missing permissions.
        HTTPException
            Failed to perform this action.
        """
        json = {}

        if name is not EMPTY:
            json["name"] = name

        if position is not EMPTY:
            json["position"] = position

        if rtc_region is not EMPTY:
            json["rtc_region"] = rtc_region

        if bitrate is not EMPTY:
            if bitrate < 8000 or bitrate > 128000:
                raise ValueError("Parameter 'bitrate' must be in range of 8000 and 128000")

            json["bitrate"] = bitrate

        if user_limit is not EMPTY:
            if user_limit is None:
                user_limit = 0

            json["user_limit"] = user_limit

        if video_quality_mode is not EMPTY:
            json["video_quality_mode"] = video_quality_mode

        if parent is not EMPTY:
            json["parent_id"] = parent.id if parent is not None else None

        if json:
            data = await self._rest.edit_channel(
                channel_id=self.id,
                json=json,
                reason=reason
            )
            if data:
                self._update_with_data(data)


class StageChannel(VoiceChannel):
    r"""Represents a stage channel in a guild.

    This class is a subclass of :class:`VoiceChannel` as such all attributes
    of :class:`VoiceChannel` and :class:`GuildChannel` are valid in this class too.

    Currently this class has no extra functionality compared to :class:`VoiceChannel`,
    More functionality will be included when stage instances are supported
    by the library.
    """
    # TODO: This is currently empty, Implement methods here when stage instances
    # are implemented.


def _channel_factory(type: int) -> typing.Type[GuildChannel]:
    if type is ChannelType.TEXT:
        return TextChannel
    if type is ChannelType.NEWS:
        return NewsChannel
    if type is ChannelType.CATEGORY:
        return CategoryChannel
    if type is ChannelType.VOICE:
        return VoiceChannel
    if type is ChannelType.STAGE:
        return StageChannel

    return GuildChannel