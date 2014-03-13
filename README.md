# Squirrel

## No Bullshit Static Blogging

![Squirrel](http://i.imgur.com/ibp6Bhc.jpg)

100% pluggable, no bullshit static blogging written on Python 3. **Currently
work in progress and not suitable for real-world use.**

# The Idea

Basic idea is that blogging should be simple (hence the “no bullshit“ part) and
there is no need for _dynamic_ system to serve, you know, _static_ pages. HTML
files are good enough and comment support can be added using services like
Disqus or Discourse. Another benefit for having static, bullshit-less site is
that it will be a whole lot of faster than anything that need a dynamic server
to perform. Another idea that Squirrel cherish is pluggable architecture. Do
you need ReST instead of Markdown for article formatting? No problem, just add
a plugin to your configuration and regenerate site! Hey, do you need comments?
It's just one plugin away! What about RSS feeds and Bootstrap theme? Yes, just
add those plugins.

So lets see how it goes. It has been fun to implement that plugin part so far.
