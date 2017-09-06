svg-colors
==========

Applies Qt (and if available, KDE) colors to SVGs. Ported from `processSvg`_.

Use the Python API:

.. code:: python

    def colorize_svg(
        src: str|Path|IO[bytes],
        dst: None|str|Path|BinaryIO=None,
        *,
        selected: bool=False,
        app: Optional[QApplication]=None,
    ) -> bytes: ...

Or the CLI

.. code:: bash

    python -m svg_colors [src] [dst]

.. _processSvg: https://github.com/KDE/kiconthemes/blob/16c808a0d2b62953420c6740cfeda2c713a90e27/src/kiconloader.cpp#L871-L919
