import re
EXPRESION_PARAM = re.compile(r'(\${(\w+)})')

def parse_expressions(expression, context):
    '''
    Reemplazo de las expresiones en el contexto
    ${expression} a buscar en el contexto
    '''
    matches = EXPRESION_PARAM.findall(expression)
    for match in matches:
        if match[1] in context:
            expression = expression.replace(
                match[0], context[match[1]])
    return expression