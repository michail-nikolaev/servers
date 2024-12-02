from .server import serve


def main():
    """Ask human"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()
