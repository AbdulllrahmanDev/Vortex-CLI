from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vortex-cli",
    version="1.2.0",
    author="Abdulrahman",
    description="Next-Gen Ultra Media Engine & High-Speed Stream Grabber",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbdulllrahmanDev/Vortex-CLI",
    py_modules=["downloader_cli", "downloader_engine", "config"],
    install_requires=[
        "rich>=13.0.0",
        "questionary>=2.0.0",
        "yt-dlp>=2024.0.0",
        "imageio-ffmpeg>=0.5.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "vortex=downloader_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
