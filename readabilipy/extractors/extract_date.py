import arrow
from collections import defaultdict
from .extract_element import extract_element
import pendulum
import re


def pendulum_datetime_extract(date_string, date_format=None):
    # Attempt to extract the date using the specified format if provided
    try:
        if date_format:
            if "unix" in date_format:
                if "milliseconds" in date_format:
                    date_string = date_string[:-3]
                datetime = pendulum.from_timestamp(int(date_string))
            else:
                datetime = pendulum.from_format(date_string, date_format)
        else:
            # Assume ISO-8601
            datetime = pendulum.parse(date_string)
    except (ValueError, TypeError, RuntimeError):
        datetime = None
    return datetime


def arrow_datetime_extract(date_string, date_format=None):
    datetime = None
    # Some tricks to avoid some undesired outcomes:
    # (1) Arrow will match the first/last digits of a 4-digit year if passed a 2-digit year format
    #
    if date_format:
        # If 2-digit year at start or end of format string, first try to extract date with equivalent
        arrow_separators = ['-', '/', '.']
        if date_format[:2] == 'YY' and date_format[2] in arrow_separators:
            datetime = arrow_datetime_extract(date_string, "YY{}".format(date_format))
        if not datetime and date_format[-2:] == 'YY' and date_format[-3] in arrow_separators:
            datetime = arrow_datetime_extract(date_string, "{}YY".format(date_format))

    if not datetime:
        try:
            if date_format:
                datetime = arrow.get(date_string, date_format)
            else:
                # Assume ISO-8601
                datetime = arrow.get(date_string)
        except (ValueError, TypeError, RuntimeError):
            # If we fail to parse a datetime, return None
            datetime = None
    return datetime


def extract_datetime_string(date_string, date_format=None, timezone=False, use_arrow=False):
    # Replace lower-case AM and PM with upper-case equivalents since pendulum
    # can only interpret upper-case
    if date_string:
        date_string = date_string.replace("am", "AM").replace("pm", "PM")

    # Huffington Post (sometimes) uses datetimes in the following format:
    # YYYY-MM-DD hh:mm:ss Z and sometimes the normal form with 'T' and no spaces
    # Here we convert the first to the second
    # so 2019-01-30 09:39:19 -0500 goes to 2019-01-30T09:39:19-0500
    if date_string:
        if re.search(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s[+-]\d{4}", date_string):
            date_string = date_string.replace(" -", "-").replace(" +", "+").replace(" ", "T")

    # First try pendulum as it seems to have fewer bugs
    # Source: http://blog.eustace.io/please-stop-using-arrow.html
    datetime = pendulum_datetime_extract(date_string, date_format)
    if not datetime and use_arrow:
        # then try arrow as it can extract dates from within longer non-date strings
        datetime = arrow_datetime_extract(date_string, date_format)

    # If a datetime is successfully extracted, re-export as ISO-8601 string.
    # NOTE: Datetime objects generated by both arrow and pendulum support the format() method
    if datetime:
        if timezone:
            out_string = datetime.format('YYYY-MM-DDTHH:mm:ssZ')
        else:
            out_string = datetime.format('YYYY-MM-DDTHH:mm:ss')
    else:
        out_string = None
    return out_string


def extract_date(html):
    """Return the article date from the article HTML"""

    # List of xpaths for HTML tags that could contain a date
    # Tuple scores reflect confidence in these xpaths and the preference used for extraction
    xpaths = [
        ('//meta[@property="article:published_time"]/@content', 24),  # Unlike with title, makes sense to have extremely high confidence in popular date tags
        ('//meta[@property="article:published"]/@content', 20),
        ('//meta[@name="Last-Modified"]/@content', 1),
        ('//meta[@name="dcterms.created"]/@content', 1),
        ('//meta[@name="published"]/@content', 5),
        ('//meta[@name="published_time_telegram"]/@content', 1),
        ('//meta[@property="og:article:published_time"]/@content', 1),
        ('//meta[@property="og:pubdate"]/@content', 1),
        ('//meta[contains(concat(" ", normalize-space(@property), " "), " article:published_time ")]/@content', 1),
        ('//meta[@itemprop="datePublished"]/@content', 2),
        ('//time[contains(@class, "entry-date")]/@datetime', 3),
        ('//time[@class="post-entry-time"]/@datetime', 1),
        ('//time[@itemprop="datePublished"]/@datetime', 3),
        ('//time[@class="post-date updated"]/@datetime', 1),
        ('//time[@class="post__date"]/@datetime', 1),
        ('//time/@datetime', 1),
        ('//time[@class="post__date"]/@content', 1),
        ('//time/text()', 1),
        ('//div[@class="article-heading-author-name"]//time[@class="timeagofunction"]/@datetime', 1),
        ('//div[@class="keyvals"]/@data-content_published_date', 1),
        ('//div[@class="article-byline"]/time[@class="visually-hidden"]/text()', 1),
        ('//div/time/@datetime', 1),
        ('//div[@class="subarticle"]/p/text()', -1),
        ('//div[@class="text"]/p/text()', -1),
        ('//div[@class="publish-date"]/text()', 1),
        ('//footer[@class="byline"]/time/@datetime', 1),
        ('//span[@class="timestamp "]/@data-epoch-time', 1),
        ('//span[@class="article-element__meta-item"]', 1),
        ('//span[@class="date published time"]/@title', 1),
        ('//span[@class="updated"]/text()', 1),
        ('//span[@class="entry-date"]/text()', 1),
        ('//p[@itemprop="datePublished"]/text()', 1),
        ('//p[@class="entry-byline"]//time[@class="entry-date"]/@datetime', 1),
        ('//article[contains(@id, "post")]//time[@class="entry-date published"]/@datetime', 25),
        ('substring-after(//*[comment()[contains(., "By")]]/comment(), "-")', 1),
        ('substring-after(//p[@class="text-muted"]/text(), ",")', 1)
    ]

    # Get the date
    date_string = extract_element(html, xpaths, delete_longer=False)

    # Proceed only if a date is found in the html. Ignore anything pulled with < 2 characters, which cannot be handled by Pendulum
    if not date_string or len(date_string) < 2:
        return None

    # Convert the date_string to a consistent format
    # Tuple scores reflect preference of format, more specific formats should be prioritised
    formats = [
        ('YYYY-MM-DD hh:mm:ss', 6, False),
        ('YYYY-MM-DD', 1, False),
        ('ddd MMM DD YYYY hh:mm:ss', 6, False),
        ('ddd MMM D YYYY HH:mm:ss', 6, False),
        ('ddd MMM DD YYYY', 1, False),
        ('DD/MM/YY', 1, False),
        ('h:m A MM/DD/YYYY', 2, False),
        ('MM/DD/YYYY', 1, True),
        ('MMM DD YYYY', 1, True),
        ('MMM D, YYYY', 1, True),
        ('MMMM DD, YYYY', 1, True),
        ('MMMM D, YYYY', 1, True),
        ('[Published] hh:mm A [EST] MMM DD, YYYY', 2, True),
        ('unix_milliseconds', 2, False),
        (None, 2, False)
    ]

    # See if a date of any of these formats can be found, including no specific format
    # Put them in a dict because shorter versions of long date formats may also match
    extracted_dates = defaultdict(int)
    for format, score, use_arrow in formats:
        date_in_this_format = extract_datetime_string(date_string, date_format=format, use_arrow=use_arrow)
        if date_in_this_format:
            if "1970-" not in date_in_this_format:
                extracted_dates[date_in_this_format] += score

    if not extracted_dates:
        return None
    # Return the date_string with highest score
    return max(extracted_dates, key=extracted_dates.get)
