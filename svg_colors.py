import gzip
from pathlib import Path
from typing import Callable, IO, Optional, Union, Sequence, BinaryIO

from qtpy.QtCore import QByteArray, QXmlStreamReader, QXmlStreamWriter
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QApplication

try:
	from PyKF5.KConfigWidgets import KColorScheme
	KColorScheme(QPalette.Active)  # A Bug in PyKF5 sadly triggers a TypeError here
except (ImportError, TypeError):
	KColorScheme = None  # type: Union[None, Callable, any]


STYLESHEET_TEMPLATE = '''
.ColorScheme-Text         {{ color: {} }}
.ColorScheme-Background   {{ color: {} }}
.ColorScheme-Highlight    {{ color: {} }}
.ColorScheme-PositiveText {{ color: {} }}
.ColorScheme-NeutralText  {{ color: {} }}
.ColorScheme-NegativeText {{ color: {} }}
'''


def get_sheet(selected: bool=False, app: Optional[QApplication]=None) -> str:
	if app is None:
		app = QApplication.instance()
	
	pal = app.palette()
	if KColorScheme is not None:
		scheme = KColorScheme(QPalette.Active, KColorScheme.Window)
		positive, neutral, negative = map(scheme.foreground, [KColorScheme.PositiveText, KColorScheme.NeutralText, KColorScheme.NegativeText])
	else:
		positive, neutral, negative = [pal.windowText()] * 3
	
	colors = [
		pal.highlightedText() if selected else pal.windowText(),
		pal.highlight()       if selected else pal.window(),
		pal.highlightedText() if selected else pal.highlight(),
		positive,
		neutral,
		negative,
	]
	
	return STYLESHEET_TEMPLATE.format(*[c.color().name() for c in colors])


def colorize_svg(
	src: Union[str, Path, IO[bytes]],
	dst: Union[None, str, Path, BinaryIO]=None,
	*,
	selected: bool=False,
	app: Optional[QApplication]=None,
) -> bytes:
	"""Inject colors into a breeze-style SVG.
	
	:param src: A file object or path to read SVG data from.
	:param dst: A file object or path to write SVG data to.
	:param selected: Use selection colors?
	:param app: Currently running QApplication. Uses QApplication.instance() by default.
	:return: Returns the SVG as binary data.
	"""
	
	if app is None:
		app = QApplication.instance()
	
	sheet = get_sheet(selected, app)
	
	if hasattr(src, 'read'):
		raw = src.read()
	else:
		path = Path(src)
		with gzip.open(str(path)) if path.suffix == '.svgz' else path.open('rb') as f:
			raw = f.read()
	
	processed = QByteArray()
	reader = QXmlStreamReader(raw)
	writer = QXmlStreamWriter(processed)
	while not reader.atEnd():
		if (
			reader.readNext() == QXmlStreamReader.StartElement and
			reader.qualifiedName() == 'style' and
			reader.attributes().value('id') == 'current-color-scheme'
		):
			writer.writeStartElement('style')
			writer.writeAttributes(reader.attributes())
			writer.writeCharacters(sheet)
			writer.writeEndElement()
			while reader.tokenType() != QXmlStreamReader.EndElement:
				reader.readNext()
		elif reader.tokenType() != QXmlStreamReader.Invalid:
			writer.writeCurrentToken(reader)
	
	processed = bytes(processed)
	if hasattr(dst, 'write'):
		dst.write(processed)
	elif dst is not None:
		with Path(dst).open('wb'):
			dst.write(processed)
	return processed


def main(args: Optional[Sequence[str]]=None):
	import sys
	
	if args is None:
		args = sys.argv
	
	if set(args) & {'-h', '-?', '--help'}:
		print('Usage:', Path(args[0]).name, '[src] [dst]', file=sys.stderr)
		sys.exit(0)
	
	src = dst = '-'
	if len(args) > 1: src = args[1]
	if len(args) > 2: dst = args[2]
	if src == '-': src = sys.stdin.buffer
	if dst == '-': dst = sys.stdout.buffer
	
	app = QApplication.instance() or QApplication(args)
	
	colorize_svg(src, dst, app=app)


if __name__ == '__main__':
	main()
