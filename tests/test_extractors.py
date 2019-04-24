from ..readabilipy.extractors.extract_title import extract_title
from ..readabilipy.extractors.extract_date import extract_date
from ..readabilipy.extractors.extract_date import standardise_datetime_format


def test_extract_title():
    htmls_with_expected = [
        ("""
            <html>
            <head>
                <meta name="fb_title" content="Example title" />
            </head>
            <body>
                <p>Hello world</p>
            <body>
            </html>
        """, "Example title"),
        ("""
            <html>
            <head>
            </head>
            <body>
                <h2 class="title">Silly title</h2>
                <h1 class="title">Bad title</h1>
                <header><h1>Example title</h1></header>
                <p>Hello world</p>
            <body>
            </html>
        """, "Example title"),
        ("""
            <html>
            <head>
            </head>
            <body>
                <h2 itemprop="headline">Example title</h2>
                <header><h1>Incorrect title</h1></header>
                <p>Hello world</p>
            <body>
            </html>
        """, "Example title"),
        ("""
            <h1 class="entry-title">
                <a href="http://addictinginfo.com/2018/10/15/trump-denies-charitable-donation-he-promised-if-elizabeth-warren-releases-dna-results-and-its-on-video/"
                    title="Permalink to Trump Denies Charitable Donation He Promised If Elizabeth Warren Releases DNA Results And It&#8217;s On Video"
                    rel="bookmark">Trump Denies Charitable Donation He Promised If Elizabeth Warren Releases DNA Results And
                    It&#8217;s On Video</a>
            </h1>
        """, "Trump Denies Charitable Donation He Promised If Elizabeth Warren Releases DNA Results And It’s On Video"),
        ("""
            <meta property="og:title" content="Trump Denies Charitable Donation He Promised If Elizabeth Warren Releases DNA Results And It&#8217;s On Video" />
        """, "Trump Denies Charitable Donation He Promised If Elizabeth Warren Releases DNA Results And It’s On Video"),
        ("""
            <h1 class="entry-title">Pamela Geller in Breitbart News: Dueling Billboards from CAIR, AFDI in Times Square</h1>
            <meta property="og:title" content="Pamela Geller in Breitbart News: Dueling Billboards from CAIR, AFDI in Times Square - Geller Report" />
        """, "Pamela Geller in Breitbart News: Dueling Billboards from CAIR, AFDI in Times Square")
    ]

    for html, expected_output in htmls_with_expected:
        output = extract_title(html)
        assert output == expected_output


def test_extract_date():
    htmls_with_expected = [
        ("""<meta name="Last-Modified" content="2018-12-21 06:30:21" />""", "2018-12-21T06:30:21"),
        ("""<p itemprop="datePublished">12/21/2018</p>""", "2018-12-21T00:00:00"),
        ("""<h1>No dates here</h1>""", None),
        ("""<meta property="article:published_time" content="2018-10-09T01:03:32" />""", "2018-10-09T01:03:32"),
        ("""<meta property="article:published_time" content="2018-12-13T21:02:01+00:00" />""", "2018-12-13T21:02:01"),
        ("""<meta property="article:published_time" content="2019-01-30 09:39:19 -0500" />""", "2019-01-30T09:39:19"),
        ("""<div class="publish-date"> Published 11:32 AM EST Feb 19, 2019 </div>""", "2019-02-19T11:32:00"),
        ("""<meta name="published_time_telegram" content="2019-01-25T15:16:00+00:00" />""", "2019-01-25T15:16:00"),
        ("""<p class="text-muted">Posted Friday, October 19, 2018</p>""", "2018-10-19T00:00:00"),
        ("""<div class="text"><p>2019-01-25T15:16:00+00:00</p></div>""", "2019-01-25T15:16:00"),
        ("""<span class="timestamp " data-localize-time data-epoch-time="1545342875000" data-time-zone="-0800" data-time-format="%A %B %d, %Y">Thursday December 20, 2018</span>""", "2018-12-20T00:00:00"),
        ("""<time style="text-transform:uppercase">8:16 AM 01/31/2019 | Politics</time>""", "2019-01-31T08:16:00"),
        ("""<span class="article-element__meta-item">Jun 01 2017 posted to <a href="/d/politics" title="Politics" class="article-element__meta-link">Politics</a></span>""", "2017-06-01T00:00:00"),
        ("""
            <div class="article-byline">By
                <span itemprop="author creator" itemtype="http://schema.org/Person" itemid="/by/michael-gryboski">
                    <a class="reporter" href="/by/michael-gryboski">
                        <span itemprop="name">Michael Gryboski</span>
                    </a>
                </span>
                , Christian Post Reporter
                <time class="visually-hidden"> | Monday, January 28, 2019</time>
            </div>
        """,
            "2019-01-28T00:00:00")
    ]

    for html, expected_output in htmls_with_expected:
        output = extract_date(html)
        assert output == expected_output


def test_standardise_datetime_format():
    dates_with_expected = [
        ("2019-01-30 09:39:19 -0500", "2019-01-30T09:39:19"),
        ("2018-12-13T21:02:01+05:00", "2018-12-13T21:02:01")
    ]

    for date, expected_output in dates_with_expected:
        output = standardise_datetime_format(date)
        assert output == expected_output