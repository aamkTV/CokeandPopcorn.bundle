import re

VIDEO_PREFIX = "/video/cokeandpopcorn"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():

    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    """Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)"""
    
    HTTP.CacheTime = CACHE_1HOUR


@handler(VIDEO_PREFIX, NAME, art=ART, thumb=ICON)


#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def MainMenu():
    oc = ObjectContainer()

    oc.add(
        DirectoryObject(
            key=Callback(AllShows),
            title="All Shows"
        )
    )
    oc.add(
        DirectoryObject(
            key=Callback(Favs),
            title="Favorites"
        )
    )

    return oc

@route(VIDEO_PREFIX + '/all-shows')
def AllShows():
    oc = ObjectContainer(title2='All the shows')

    pg = HTML.ElementFromURL("http://www.cokeandpopcorn.ch/tvsection.php")
    shows = pg.xpath("//div[@class='tabcontents']//div[@class='lister']//a")

    discard = re.compile(r'(where can i watch|watch series\?)',re.I)


    for show in shows:
        if discard.search(show.text):
            Log('WOOP WOOP WE HAVE A MATCH: %s' % show.text)
            continue
        oc.add(
            TVShowObject(
                url=show.xpath('./@href')[0],
                key=Callback(Show,Title=show.text.strip(),url=show.xpath('./@href')[0]),
                title=show.text.strip(),
                #rating_key=show.text.strip()
            )
        )

    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        return ObjectContainer(header='Empty',message="Unable to fetch shows right now.")

    return oc

@route(VIDEO_PREFIX + '/favorites')
def Favs(url=None):
    if url:
        return MessageContainer('mm', 'got video: %s' % url)
    else:
        return MessageContainer("no", "kbyeee")

@route(VIDEO_PREFIX + '/show')
def Show(Title=None, url=None):
    if not Title:
        return MessageContainer('whoops', 'Something went wrong!')

    oc = ObjectContainer(title2=Title)

    pg = HTML.ElementFromURL(url)
    seasonHeadings = pg.xpath("//div[@class='episodecontainer']//h3//a")
    seasonNumReg = re.compile(r'(\d+)$',re.I)
    #seasons = pg.xpath("//div[@class='episodecontainer']//ul")
    idx=0

    for season in seasonHeadings:
        num = int(seasonNumReg.search(season.text).group(1))
        oc.add(
            SeasonObject(
                key=Callback(Season,Title=Title,url=url,Season=season.text,idx=idx,i=num),
                url=season.xpath('./@href')[0],
                title=season.text,
                show=Title,
                index=num,
                #rating_key="%s_%s" % (Title,season.text)
            )
        )
        idx+=1

    oc.objects.sort(key = lambda obj: obj.title)
    return oc




@route(VIDEO_PREFIX + '/show/season')
def Season(Title=None,url=None,Season=None,idx=None,i=None):
    if not Title:
        return MessageContainer('whoops', 'Something went wrong! Can\'t get this season')

    oc = ObjectContainer(title2="%s %s" % (Title, Season))

    pg = HTML.ElementFromURL(url)
    episodes = pg.xpath("//div[@class='episodecontainer']//ul")[int(idx)]
    episodes = episodes.xpath('./li/a')
    ep_idx=1

    for ep in episodes:
        ep_url=ep.xpath('./@href')[0]
        oc.add(
            EpisodeObject(
                key=Callback(Episode,Title=Title,url=ep_url,Season=Season,Episode="%s %s" % (ep.xpath('./strong/text()')[0],ep.xpath('./text()')[0]),i=i,ep_idx=ep_idx),
                title="%s %s" % (ep.xpath('./strong/text()')[0],ep.xpath('./text()')[0]),
                #season=int(i),
                #show=Title,
                #index=ep_idx,
                #url=ep_url,
                rating_key=ep_url
            )
        )
        ep_idx+=1

    return oc

@route(VIDEO_PREFIX + '/show/episode')
def Episode(Title=None,url=None,Season=None,Episode=None,i=None,ep_idx=None):
    oc = ObjectContainer(title2="%s" % Title)
    oc.add(
        EpisodeObject(
            url=url
        )
    )
    return oc



# Part of the "search" example 
# query will contain the string that the user entered
# see also:
#   http://dev.plexapp.com/docs/Objects.html#InputDirectoryItem
def SearchResults(sender,query=None):
    return MessageContainer(
        "Not implemented",
        "In real life, you would probably perform some search using python\nand then build a MediaContainer with items\nfor the results"
    )
    
  
