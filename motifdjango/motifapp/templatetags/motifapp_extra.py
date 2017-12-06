from django import template
from datetime import date, datetime
from django.template import defaultfilters
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext as _, ngettext, pgettext
import re

register = template.Library()


@register.filter
def find_user_summary_vote(value, arg):
    try:
        list(value).index(arg)
        return True
    except ValueError:
        return False


@register.filter
def find_number_of_rating(value, arg):
    try:
        index = [art.id for art in value].index(arg)
        return [art.total_rated for art in value][index]
    except ValueError:
        return None


@register.filter
# {{ ratings|find_avg_c:article.id }}
def find_avg_c(value, arg):
    try:
        index = [art.id for art in value].index(arg)
        avg_c = [art.avg_c for art in value][index]
        if avg_c is not None:
            avg_c = round(avg_c, 0)
        return avg_c
    except ValueError:
        return None


@register.filter
def naturaltime(value):
    time = django_original_naturaltime(value)
    return re.sub(r', (.*)', " ago", time)


@register.filter
def domain_shorten(value):
    return value.replace('www.', '').replace('.com', '')


@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def sub(value, arg):
    return int(value) - int(arg)


def django_original_naturaltime(value):
    """
    For date and time values show how many seconds, minutes, or hours ago
    compared to current timestamp return representing string.
    """
    if not isinstance(value, date):  # datetime is a subclass of date
        return value

    now = datetime.now(utc if is_aware(value) else None)
    if value < now:
        delta = now - value
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timesince(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a second ago', '%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a minute ago', '%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'an hour ago', '%(count)s hours ago', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s from now'
            ) % {'delta': defaultfilters.timeuntil(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a second from now', '%(count)s seconds from now', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a minute from now', '%(count)s minutes from now', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ngettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'an hour from now', '%(count)s hours from now', count
            ) % {'count': count}
