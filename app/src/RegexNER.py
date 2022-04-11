from spacy.tokens import Doc, Span
from Utils import Utils
from spacy.language import Language
import re

@Language.component("regex")
def REGEXComponent(doc):        
    text = doc.text
    utils = Utils()
    regexes = utils.cargarConfiguracion()["ANONIMIZACION"]["EXPRESIONES_REGULARES"]
    
    chars_to_tokens = {}
    
    for token in doc:
        for i in range(token.idx, token.idx + len(token.text)):
            chars_to_tokens[i] = token.i
    for label, regex in regexes.items():
        for match in re.finditer(re.compile(regex), text):
            start, end = match.span()
            span = doc.char_span(start, end, label=label)
            # If not full tokens, returns None
            if span is not None:
                if span not in doc.ents:
                    try:
                        doc.ents += (span,)
                    except ValueError as e:
                        print('Error ({}): {} {}\n{}'.format(str(1), span.label_, span, e))
            else:
                start_token = chars_to_tokens.get(start)
                end_token = chars_to_tokens.get(end)

                if start_token is not None and end_token is not None:
                    span = Span(doc, start_token, end_token + 1, label=label)
                    try:
                        doc.ents += (span,)
                    except ValueError as e:
                        pass
                else:
                    pass

    return doc