ROCKET-m: Simple html5 live streaming solution using web-m
==========================================================

ROCKET-m is simple html5 live video streaming solution using web-m and chunked
http for streaming with support for still image slides using motion detection.

Features
--------

* Live stream
* Web-m
* HTML5
* Slides

Intro
-----

Have you ever wanted to have a simple stream running on linux and have problems?
Well, me too! 

In age of HTML5 with native video support using video tag, you would thinks you
would be able to throw flash away and burn it in hell, but you just figure out
you can't. Well that's not entierly true.

There currently exists one streaming server that is able to stream live html5
video using webm, it's calle stream-m. 

.. note::

    While ffserver supports streaming live webm, it just does not work with 
    firefox as a client.

What does this project?
-----------------------

This project mixes things together and gives a sane way how to deploy and manage
your stream. 

It takes ffmpeg for streaming stream-m as streaming server, puts it
into buildout for deploy and abuses supervisor for stream control. 
It also takes motion, for motion detection, and uses it for extraction of 
still image slides.

Dependencies
------------

* python 2.6 or 2.7
* sun java6 (for stream-m)

  .. note::

    it might work with openjdk just fine, but i had some problems

* curl

Installation:
-------------

Buildout it with::

    $ cp buildout.d/development.cfg buildout.cfg
    $ python2.7 bootstrap.py
    $ ./bin/buildout

You are probably going to use video4linux2. If you want to access video and
audio devices as a non-root user, you have to add yourself to video and audio 
group::

    $ sudo usermod -a -G video,audio user
    $ newgrp video && newgrp video
