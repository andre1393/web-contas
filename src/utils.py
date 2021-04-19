import datetime


def get_current_month(request):
    month_int = request.args.get('mes_busca') if request.args.get('mes_busca') else datetime.datetime.now().month
    return month_int, get_month_str(month_int, start_zero=False)


def get_month_str(month_int, start_zero=False):
    if start_zero:
        months = ("'Janeiro'", "'Fevereiro'", "'Março'", "'Abril'", "'Maio'", "'Junho'", "'Julho'", "'Agosto'",
                  "'Setembro'", "'Outubro'", "'Novembro'", "'Dezembro'")
    else:
        months = ("''", "'Janeiro'", "'Fevereiro'", "'Março'", "'Abril'", "'Maio'", "'Junho'", "'Julho'", "'Agosto'",
                  "'Setembro'", "'Outubro'", "'Novembro'", "'Dezembro'")

    return months[int(month_int)]


def to_bit(x):
    return "'1'" if x == 'true' else "'0'"
