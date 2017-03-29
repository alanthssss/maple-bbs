#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: filters.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-07 21:00:32 (CST)
# Last Update:星期三 2017-3-29 20:42:23 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime
from config import SITE

from bleach import clean
from flask import Markup, g
from flask_babelex import format_datetime
from flask_login import current_user
from misaka import HtmlRenderer, Markdown


def safe_clean(text):
    tags = ['b', 'i', 'font', 'br', 'blockquote', 'div', 'h2', 'a']
    attrs = {'*': ['style', 'id', 'class'], 'font': ['color'], 'a': ['href']}
    styles = ['color']
    return Markup(clean(text, tags=tags, attributes=attrs, styles=styles))


def markdown(text):
    renderer = HtmlRenderer()
    md = Markdown(renderer, extensions=('fenced-code', ))
    return Markup(md(text))


def safe_markdown(text):
    renderer = HtmlRenderer()
    md = Markdown(renderer, extensions=('fenced-code', ))
    return Markup(safe_clean(md(text)))


def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    if diff.days > 10:
        return format_datetime(dt, 'Y-M-d H:m')
    elif diff.days <= 10 and diff.days > 0:
        periods = ((diff.days, "day", "days"), )
    elif diff.days <= 0 and diff.seconds > 3600:
        periods = ((diff.seconds / 3600, "hour", "hours"), )
    elif diff.seconds <= 3600 and diff.seconds > 90:
        periods = ((diff.seconds / 60, "minute", "minutes"), )
    else:
        return default

    for period, singular, plural in periods:

        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


def show_time():
    from flask_babelex import format_datetime
    if g.user.is_authenticated:
        return 'LOCALE:' + format_datetime(datetime.utcnow())
    else:
        return 'UTC:' + format_datetime(datetime.utcnow())


def notice_count():
    from forums.api.forums.models import Notice
    if g.user.is_authenticated:
        count = Notice.query.filter_by(
            rece_id=g.user.id, is_read=False).count()
        if count > 0:
            return count
    return None


def hot_tags():
    from forums.api.tag.models import Tags
    tags = Tags.query.limit(9).all()
    return tags


def recent_tags():
    from forums.api.tag.models import Tags
    tags = Tags.query.limit(12).all()
    return tags


def is_online(user):
    from forums.api.user.models import UserSetting
    from forums.common.records import load_online_sign_users
    setting = user.setting
    if setting.online_status == UserSetting.STATUS_ALLOW_ALL:
        return user.username in load_online_sign_users()
    elif setting.online_status == UserSetting.STATUS_ALLOW_AUTHENTICATED:
        return user.username in load_online_sign_users(
        ) and current_user.is_authenticated
    elif setting.online_status == UserSetting.STATUS_ALLOW_OWN:
        return current_user.id == user.id
    return False


def is_not_confirmed(user):
    return (not user.is_confirmed and user.id == current_user.id)


def register_jinja2(app):

    app.jinja_env.globals['SITE'] = SITE
    app.jinja_env.globals['hot_tags'] = hot_tags
    app.jinja_env.globals['recent_tags'] = recent_tags
    app.jinja_env.globals['notice_count'] = notice_count
    app.jinja_env.globals['show_time'] = show_time
    app.jinja_env.filters['timesince'] = timesince
    app.jinja_env.filters['markdown'] = safe_markdown
    app.jinja_env.filters['safe_clean'] = safe_clean
    app.jinja_env.filters['is_online'] = is_online
    app.jinja_env.filters['is_not_confirmed'] = is_not_confirmed