class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class TextNotFoundException(Exception):
    """Вызывается, когда искомый текст не был найден."""
    pass
