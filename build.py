from fabric.api import run, sudo, local, get, settings
from fabric.context_managers import cd, prefix
from fabric.contrib.files import exists

def download_git(name, url, branch, tags=False ):
    """
    Downloads a speciffic branch or tag from git or updates it if it already
    exists

    :param name: Name of package
    :type name: str
    :param url: Package url
    :type url: str
    :param branch: Package branch to follow(everything after `git checkout -B %s`)
    :type branch: str
    :param tags: Should tags be downloaded
    :type tags: str
    """

    if not exists(name):
        run("git clone %s" %url)
    with cd(name):
        if tags:
            run("git fetch --tags")
        run("git checkout -B %s" %branch)
        with settings(warn_only=True):
            run("git pull")

def ffmpeg_build_static(path, packages={}, extraopts=[], reconfigure=False):
    """
    Builds static ffmpeg

    :param path: Build path
    :type path: str
    :param packages: packages to include in ffmpeg
    :type packages: dict
    :param extraopts: Extra options to use when building
    :type extraopts: list
    :param reconfigure: Should be package reconfigured
    :type reconfigure: boolean
    """

    opts = []

    # Alsa support
    # libasound2 must be shared lib
    sudo("apt-get install build-essential git subversion autoconf libtool"
         " libv4l-dev libasound2-dev")

    run("mkdir -p %s"% path)
    with cd(path):
        path = run("pwd")
        print path
        run("mkdir -p build")

        if packages.get("fdk-aac"):
            # Aac support for x264 audio
            download_git("fdk-aac", "git://github.com/mstorsjo/fdk-aac.git",
                        packages.get("fdk-aac") or "master")
            with cd("fdk-aac"):
                if not exists("config.log") or reconfigure:
                    run("autoreconf -fiv")
                run("./configure --prefix=%s/build --enable-static --disable-shared" %path)
                run("make && make install")

            opts.append("--enable-libfdk-aac")

        if packages.get("vorbis"):
            # Vorbis requires libogg
            if not exists("ogg"):
                run("svn co http://svn.xiph.org/trunk/ogg")
            with cd("ogg"):
                run("svn update module")
                if not exists("config.h") or reconfigure:
                    run("./autogen.sh --prefix=%s/build --enable-static --disable-shared" %path)
                    run("./configure --prefix=%s/build --enable-static --disable-shared" %path)
                run("make && make install")

            # Vorbis support for webm audio
            if not exists("vorbis"):
                run("svn co http://svn.xiph.org/trunk/vorbis")
            with cd("vorbis"):
                run("svn update module")
                if not exists("config.h") or reconfigure:
                    run("./autogen.sh --prefix=%s/build --enable-static --disable-shared" %path)
                    run("./configure --prefix=%s/build --enable-static --disable-shared" %path)
                run("make && make install")

            opts.append("--enable-libvorbis")

        # Assambler
        download_git("yasm", "https://github.com/yasm/yasm.git",
                    packages.get("yasm") or "master")
        with cd("yasm"):
            run("git pull")
            if not exists("config.h") or reconfigure:
                run("./autogen.sh")
                run("./configure --prefix=%s/build" %path)
            run("make && make install")

        # Yasm must be in path
        with prefix("export PATH=$PATH:%s/build/bin" %path):

            if packages.get("x264"):
                # x264 video codec used in flash
                download_git("x264", "git://git.videolan.org/x264",
                            packages.get("x264") or "master")
                with cd("x264"):
                    if not exists("config.mk") or reconfigure:
                        run("./configure --prefix=%s/build --enable-static --disable-shared" %path)
                        run("make && make install")

                opts.append("--enable-libx264")

            if packages.get("vpx"):
                # vp8 video codev used in webm
                download_git("libvpx", "http://git.chromium.org/webm/libvpx.git",
                            packages.get("vpx") or "master", tags=True)
                with cd("libvpx"):
                    if not exists("config.mk") or reconfigure:
                        run("./configure --prefix=%s/build --enable-static --disable-shared" %path)
                    run("make && make install")

                opts.append("--enable-libvpx")

            # Now let's compile ffmpeg
            download_git("ffmpeg", "git://source.ffmpeg.org/ffmpeg",
                         packages.get("ffmpeg") or "master")
            with cd("ffmpeg"):
                run('CFLAGS="-I%(path)s/build/include" LDFLAGS="-L%(path)s/build/lib -lm"'
                    " ./configure --prefix=%(path)s/build --extra-version=static"
                    " --disable-debug --disable-shared --enable-static"
                    " --extra-cflags=--static --disable-ffplay"
                    " --disable-doc --enable-gpl --enable-pthreads --enable-postproc"
                    " --enable-gray --enable-runtime-cpudetect"
                    " --enable-nonfree "
                    " --enable-version3 "
                    "%(opts)s %(extraopts)s" %{"path" : path,
                                 "opts": " ".join(opts),
                                 "extraopts": " ".join(extraopts)})
                run("make && make install")

            get("build/bin/ffmpeg", "packages/ffmpeg")
            local("chmod +x packages/ffmpeg")

            get("build/bin/ffserver", "packages/ffserver")
            local("chmod +x packages/ffserver")

def crtmpserver_build_static():
    """
    Builds static crtmpserver
    """

    sudo("apt-get -y install g++ subversion cmake make libssl-dev")
    if not exists("crtmpserver"):
        run('svn co --username anonymous --password "" https://svn.rtmpd.com/crtmpserver/trunk crtmpserver')
    else:
        run("svn update")

    with cd("crtmpserver/builders/cmake/"):
        run("""COMPILE_STATIC=1 cmake -DCRTMPSERVER_VERSION_RELEASE_NUMBER=trunk"""
            """-DCRTMPSERVER_VERSION_CODE_NAME=Barbarian -DCMAKE_BUILD_TYPE=Release .""")
        run("make")
        run("./package.sh")
        get("crtmpserver-trunk---.tar.gz","packages/crtmpserver.tar.gz")

def motion_build_static(path, packages={}, reconfigure=False):
    """
    Builds motion static

    :param path: Build path
    :type path: str
    :param packages: List of packages and branches to use
    :type packages: dict
    :param reconfigure: Should we reconfigure
    :type reconfigure: boolean
    """

    sudo("apt-get install build-essential git wget autoconf libtool"
         " libv4l-dev libz-dev")

    run("mkdir -p %s" %path)
    with cd(path):
        path = run("pwd")
        run("mkdir -p build")

        ffmpeg_build_static(".", packages,
                            extraopts=["--disable-indev=alsa", "--disable-outdev=alsa"],
                            reconfigure=reconfigure)

        # Yasm must be in path
        with prefix("export PATH=$PATH:%s/build/bin" %path):
            # libjpeg-turbo for faster, and static linkable jpeg
            if not exists("libjpeg-turbo"):
                run('wget "http://downloads.sourceforge.net/project/libjpeg-turbo/1.2.1/libjpeg-turbo-1.2.1.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Flibjpeg-turbo%2Ffiles%2F1.2.1%2F&ts=1349857893&use_mirror=switch" '
                 '-O libjpeg-turbo-1.2.1.tar.gz')
                run("tar -xvf libjpeg-turbo-1.2.1.tar.gz")
                run("mv libjpeg-turbo-1.2.1 libjpeg-turbo")
            with cd("libjpeg-turbo"):
                if not exists("config.h") or reconfigure:
                    run("./configure --prefix=%s/build --enable-static --disable-shared" %path)

                run("make && make install")
                with settings(warn_only=True):
                    run("rm %s/build/lib/libjpeg.so*" %path)

            # and the last let's go for the motion
            download_git("motion", "https://github.com/sackmotion/motion.git",
                         packages.get("motion") or "master")
            with cd("motion"):
                if not exists("config.h") or reconfigure:
                    run('LDFLAGS="-L%(path)s/build/lib/" CFLAGS="-static" '
                        './configure --with-ffmpeg=%(path)s/build/lib/ '
                        '--with-ffmpeg-headers=%(path)s/build/include/ '
                        '--with-jpeg-turbo=%(path)s/build/lib/ '
                        '--without-optimizecpu --prefix=%(path)s/build' %{"path":path})

                run("make && make install")

            get("build/bin/motion", "packages/motion")
            local("chmod +x packages/motion")
