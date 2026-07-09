from . import parser_exchange
from .views  import ParserExchange

parser_exchange.add_url_rule('/', view_func=ParserExchange.as_view('parser_exchange'))