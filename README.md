# rawdog-readable-articles
A [rawdog](http://offog.org/code/rawdog/) plugin to download feed entries using readability stripping them to a bare
minimum readable html content

##Dependencies
This plugin uses:
-	[python readability ( lxml version )](https://github.com/buriy/python-readability)
-	[python requests](http://docs.python-requests.org/)

##Installation
simply drop the file under the plugin folder if the dependencies are satisfied


##Options
**downloadupdates** *(bool)* determines if, when an article gets updated information,
the old version should be overwritten by the new one or skipped

the plugin can operate in 2 modes: inline, or file; toggled with with **inlinecontent** *(bool)*

###file
in file mode, each article's content will be downloaded to a separate file, the paths
will be decided with:
**downloaddir** *(string)* will be the destination path, relative to rawdog's working folder
**downloadurl** *(string)* will control what the output will rebase the path to, useful if hosting
the path will be stored in the variable **localcopy**, available to the rawdog template generator
ready for inclusion in an hyperlink
please note that in this mode, the plugin won't purge old content, so you'll have to setup yourself
an external system to do so

###inline
in inline mode, the html code will be directly inserted in the output variable, properly escaped
and ready for inclusion within an hyperlink
while this mode will allow rawdog's normal article history management due to variable handling, it
comes with a cost: the feed page list will be the sum of the articles' full content and can grow quite
large in size and slow to transfer, I'd personally reccomend to use another plugin to segment it (paged-output)
to make the transfer more reasonable depending on the volume of the backlog


##template item generator example
```
<div class="item feed-__feed_hash__ feed-__feed_id__" id="item-__hash__">
<p class="itemheader">
<span class="itemtitle">__if_localcopy__ <a href="__localcopy__">__title_no_link__</a> __else__ __title_no_link__ __endif__</span>
<span class="itemfrom">[<a href="__url__">__feed_title_no_link__</a>]</span>
</p>
__if_description__<div class="itemdescription">
__description__
</div>__endif__
</div>
```

##TODO
- remove the dependency on requests lib and use simply urllib
- handle purging of old contentin file mode

