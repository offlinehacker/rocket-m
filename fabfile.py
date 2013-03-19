from fabric.api import task, sudo
from build import ffmpeg_build_static, motion_build_static

@task
def motion_build(reconfigure=False):
    """
    Builds static motion
    """

    packages = {
        "motion": "master",
        "ffmpeg": "master"
    }

    motion_build_static("motion", packages, reconfigure)

@task
def ffmpeg_build_user(reconfigure=False):
    """
    Builds static ffmpeg with x11 grab support
    """
    # x11 support
    sudo("apt-get install libx11-dev libxext-dev libxfixes-dev")

    packages = {
        "fdk-aac": "master",
        "vorbis": "master",
        "x264": "master",
        "vpx": "master",
        "ffmpeg": "master"
    }

    ffmpeg_build_static("ffmpeg-user", packages,
                        extraopts=["--enable-x11grab --enable-indev=alsa"],
                        reconfigure=reconfigure)

@task
def ffmpeg_build_server(reconfigure=False):
    """
    Builds static ffmpeg with server deps
    """
    packages = {
        "fdk-aac": "master",
        "vorbis": "master",
        "x264": "master",
        "vpx": "master",
        "ffmpeg": "master"
    }

    ffmpeg_build_static("ffmpeg-server", packages,
                        extraopts=["--enable-indev=alsa"],
                        reconfigure=reconfigure)
