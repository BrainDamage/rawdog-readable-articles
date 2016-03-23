# rawdog plugin to automatically download local copies of article links
# using readability.
#
# This plugin supports the following configuration options:
#
# downloaddir       Directory to download files to
# downloadurl       How to link to downloaddir in the generated HTML
# downloadupdates	If to download again an article if it was updated
# inlinecontent		If enabled the content won't be downloaded to a separate 
#						file but instead be inlined in a variable that can be
#						embedded in the html output
#					if set to url, the content will be properly escaped so it can
#						be inserted directly within an url link
#
# the options to toggle the content instead of being saved regardless are due to the
# large size of the database which would grow unwieldly if everything would be shoved in
# If it succeeds in downloading a local copy of an article, it'll add a
# "localcopy" bit to the item template for that article with the URL of the
# copy. You can then add something like this to your item template:
#   __if_localcopy__ (<a href="__localcopy__">local copy</a>)__endif__
#
# note: there's no expiry mechanism, so you'll either have to use the
# inlining function to use rawdog's normal shredding of old content, or you'll have
# to setup your own externally
#
#
# Copyright (c) 2016, BrainDamage
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <organization> nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY BrainDamage ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL BrainDamage BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import rawdoglib.plugins
from rawdoglib.rawdog import string_to_html
from readability.readability import Document
from os import path
from requests import get as request_get
from codecs import encode
from hashlib import sha1 as sha1_hash
from urllib import quote as url_quote


class Downloader:
	def __init__(self):
		self.options = {
			"downloaddir": "local-cache",
			"downloadurl": "local-cache",
			"downloadupdates": True,
			"inlinecontent": False,
		}

	def config_option(self, config, name, value):
		if name in self.options:
			self.options[name] = value
			return False
		else:
			return True

	def article_added(self, rawdog, config, article, now):
		self.download_article(config, article)
		return True

	def article_updated(self, rawdog, config, article, now):
		if self.options["downloadupdates"]:
			self.download_article(config, article)
		return True

	def download_article(self, config, article):
		"""Download a local copy of an article."""
		# Find the link from the article
		link = article.entry_info.get("link")
		if link == "" or link is None:
			# No link to follow.
			return

		html = request_get(link).text

		parsed_data = ""
		try:
			parsed_data = Document(html).summary()
		except:
			config.log("error parsing article", article.entry_info.get("title"))
			return
		if self.options["inlinecontent"] is False:
			filename = sha1_hash(encode(article.entry_info.get("title"),'utf-8')).hexdigest()
			local_copy = path.join(self.options["downloaddir"],filename + ".html")

			filedata = codecs.open(local_copy,'w','utf-8-sig')
			#make sure to wipe any old content in order to update it
			filedata.seek(0)
			filedata.truncate()
			try:
				filedata.write(parsed_data)
			except:
				config.log("html failed to parse for article", article.entry_info.get("title"))
			filedata.close()

			local_copy = path.relpath(local_copy,self.options["downloaddir"])

			config.log("Downloaded: ", article.entry_info.get("title"), local_copy)
			# Add an attribute to the article to say where the local copy is.
			article.entry_info["download_articles_local_copy"] = local_copy
		else:
			config.log("Downloaded: ", article.entry_info.get("title"))
			# Add an attribute to the article with the html content.
			article.entry_info["download_articles_local_copy"] = parsed_data

	def output_item_bits(self, rawdog, config, feed, article, -	bits):
		# Retrieve the local copy attribute we saved above.
		local_copy = article.entry_info.get("download_articles_local_copy")
		if local_copy is None:
			# There isn't one.
			pass
		else:
			# Add a localcopy field to the template.
			if self.options["inlinecontent"] is not False:
				if self.options["inlinecontent"] == "url":
					bits["localcopy"] = "data:text/html;charset=utf-8, " + url_quote(encode(local_copy,'utf-8'))
				else:
					bits["localcopy"] = encode(local_copy,'utf-8')
			else:
				bits["localcopy"] = string_to_html(self.options["downloadurl"] + '/' + local_copy, config)

		return True

downloader = Downloader()
rawdoglib.plugins.attach_hook("config_option", downloader.config_option)
rawdoglib.plugins.attach_hook("article_added", downloader.article_added)
rawdoglib.plugins.attach_hook("article_updated", downloader.article_updated)
rawdoglib.plugins.attach_hook("output_item_bits", downloader.output_item_bits)
