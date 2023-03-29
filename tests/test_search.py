#!/usr/bin/env python

import pytest
from ima.engine.search import Search

sear = Search(engine = 'google', query = 'images of madara')

expected_links = [
	'https://www.planetware.com/pictures/spain-e.htm',
	'https://unsplash.com/s/photos/spain',
	'https://www.istockphoto.com/photos/spain',
	'https://www.dreamstime.com/photos-images/spain.html',
	'https://kids.nationalgeographic.com/geography/countries/article/spain',
	'https://unsplash.com/s/photos/spain-flag',
	'https://unsplash.com/photos/ChSZETOal-I',
	'https://unsplash.com/photos/UP22zkjJGZo',
	'https://www.pexels.com/search/spain/',
	'https://www.gettyimages.com/photos/spain',
	'https://www.gettyimages.fr/photos/spain',
	'https://www.shutterstock.com/search/spain',
	'https://pixabay.com/images/search/spain/',
	'https://www.gettyimages.com/photos/spain',
	'https://www.nationalgeographic.com/travel/article/beautiful-photos',
	'https://www.pexels.com/search/spain/',
	'https://www.planetware.com/pictures/spain-e.htm',
	'https://www.shutterstock.com/search/spain',
	'https://www.expedia.com/pictures/europe/spain.d166',
	'https://www.britannica.com/place/Spain',
	'https://www.dreamstime.com/photos-images/spain.html',
	'https://www.gettyimages.com/photos/madrid-spain',
	'https://www.worldatlas.com/maps/spain',
	'https://www.boredpanda.com/interesting-things-spain/',
	'https://www.istockphoto.com/photos/spain',
	'https://www.gettyimages.in/photos/spain',
	'https://travel.usnews.com/Barcelona_Spain/Pictures/',
	'https://www.nationalgeographic.com/travel/article/spain-photos',
	'https://kids.nationalgeographic.com/geography/countries/article/spain',
	'https://pixabay.com/images/search/spain/',
	'https://theculturetrip.com/europe/spain/articles/21-photos-that-prove-seville-is-spains-most-colourful-city/',
	'https://pixabay.com/photos/search/spain/',
	'https://allthatsinteresting.com/vintage-spain',
	'https://zoom.earth/places/spain/',
	'https://www.cia.gov/the-world-factbook/countries/spain/images',
	'https://www.pexels.com/search/barcelona/',
	'https://www.voanews.com/a/spain-morocco-hope-joint-bid-for-world-cup-will-patch-up-differences/7023466.html',
	'https://theculturetrip.com/europe/spain/articles/25-photos-that-prove-you-should-visit-northern-spain-right-now/',
	'https://www.artst.org/famous-spanish-paintings/',
	'https://www.tripadvisor.com/LocationPhotos-g187427-Spain.html',
	'https://theplanetd.com/cities-in-spain/',
	'https://www.catholicworldreport.com/2023/03/26/marianists-in-spain-under-fire-for-lack-of-transparency-regarding-sex-ed-program/',
	'https://www.shutterstock.com/search/naruto',
	'https://www.gettyimages.com/photos/naruto',
	'https://cc.bingj.com/cache.aspx?q=images+of+naruto&d=4874496045955915&mkt=en-US&setlang=en-US&w=su1i-14VPquoqkkxEEwMtPDgFvlFfnan',
	'https://wall.alphacoders.com/by_sub_category.php?id=173173',
	'https://cc.bingj.com/cache.aspx?q=images+of+naruto&d=4992165265749893&mkt=en-US&setlang=en-US&w=X8zspLGmLl_eLLHH_kLHFA10Xe8sA3aT',
	'https://pixabay.com/images/search/naruto/',
	'https://cc.bingj.com/cache.aspx?q=images+of+naruto&d=4554705668942218&mkt=en-US&setlang=en-US&w=5JWO6tfo57sXPZE2vR3JzJB9cajg80TM',
	'https://www.pushsquare.com/news/2023/03/random-lars-tekken-8-rage-art-is-a-reminder-of-his-time-in-naruto-storm-2',
	'https://attackofthefanboy.com/entertainment/why-does-gojo-cover-his-eyes-in-jujutsu-kaisen-explained/',
	'https://tropedia.fandom.com/wiki/With_Friends_Like_These...',
	'https://comicbook.com/anime/news/naruto-boruto-finale-first-look/',
	'https://www.the-sun.com/sport/7701603/who-zion-williamson-nba-pelicans/',
	'https://www.pushsquare.com/news/2023/03/more-games-will-be-removed-from-ps-plus-extra-in-april',
	'https://progameguides.com/roblox/best-roblox-anime-games/',
	'https://collider.com/best-movie-tv-characters-redditors-hate/',
	'https://tropedia.fandom.com/wiki/Evil_Is_Petty',
	'https://twinfinite.net/2023/03/top-10-best-orange-haired-anime-characters/',
	'https://www.shutterstock.com/search/naruto',
	'https://en.wikipedia.org/wiki/List_of_Naruto_characters',
	'https://www.technadu.com/how-many-seasons-are-in-naruto/322610/',
	'https://www.gettyimages.com/photos/images-of-naruto',
	'https://cc.bingj.com/cache.aspx?q=images+of+naruto&d=5007094566312518&mkt=en-US&setlang=en-US&w=N85MwvqZBdXk9vvS3IfwMXWsD7ElKy8w',
	'https://www.shutterstock.com/search/%22uzumaki-naruto%22',
	'https://cc.bingj.com/cache.aspx?q=images+of+naruto&d=4710651629869009&mkt=en-US&setlang=en-US&w=Q4IOd7Ny03BeKCs26SdOHDdVjnXPtoM9',
	'https://yahoo.uservoice.com/forums/193847-search'
]

def test_url_operations():
    assert sear.set_engine('duckduckgo').url == 'https://duckduckgo.com/html/?q=images+of+naruto'
    assert sear.set_query('naruto').set_engine('yahoo').url == 'https://search.yahoo.com/search/?p=naruto'

def test_extract_links():
    html = open('./html/google_index.html')
    sear.page = html
    links = sear.next()
    sear.set_engine('duckduckgo')
    html = open('./html/spain_duckduckgo.html')
    sear.page = html
    links += sear.next()
    html = open('./html/yahoo_index.html')
    sear.page = html
    sear.set_engine('yahoo')
    links += sear.next()
    #assert len(links) == len(expected_links)
    #assert all([ links == expected_links for a, b in zip(links, expected_links) ])

def test_next():
    for i in sear.next(): print(i)

test_next()
